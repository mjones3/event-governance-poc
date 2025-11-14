package com.biopro.demo.orders.service;

import com.biopro.common.core.dlq.processor.DLQProcessor;
import com.biopro.common.integration.schema.SchemaRegistryService;
import com.biopro.common.monitoring.metrics.DlqMetricsCollector;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecord;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Service for publishing order events to Kafka.
 * Demonstrates integration with DLQ framework.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OrderEventPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final SchemaRegistryService schemaRegistryService;
    private final SchemaRegistryClient schemaRegistryClient;
    private final DLQProcessor dlqProcessor;
    private final DlqMetricsCollector metricsCollector;

    private static final String ORDERS_TOPIC = "biopro.orders.events";
    private static final String ORDER_CREATED_SUBJECT = "OrderCreatedEvent";

    /**
     * Publishes an order created event
     */
    public void publishOrderCreated(OrderCreatedRequest request) {
        String eventId = UUID.randomUUID().toString();
        String correlationId = UUID.randomUUID().toString();

        try {
            // Build event payload
            Map<String, Object> event = buildOrderEvent(eventId, correlationId, request);

            // Validate against schema
            SchemaRegistryService.ValidationResult validation =
                    schemaRegistryService.validateEvent("OrderCreatedEvent", event);

            if (!validation.isValid()) {
                log.error("Schema validation failed for event {}: {}",
                        eventId, validation.getErrorMessage());
                metricsCollector.recordSchemaValidation("orders", false);

                // Route to DLQ
                dlqProcessor.routeToDLQ(
                        eventId,
                        "orders",
                        "OrderCreatedEvent",
                        ORDERS_TOPIC,
                        event.toString().getBytes(),
                        new RuntimeException("Schema validation failed: " + validation.getErrorMessage()),
                        0
                );
                return;
            }

            metricsCollector.recordSchemaValidation("orders", true);

            // Convert Map to GenericRecord for Avro serialization
            GenericRecord avroRecord = convertToGenericRecord(event);

            // Publish to Kafka
            kafkaTemplate.send(ORDERS_TOPIC, eventId, avroRecord)
                    .whenComplete((result, ex) -> {
                        if (ex != null) {
                            log.error("Failed to publish order event: {}", eventId, ex);

                            // Route to DLQ on failure
                            dlqProcessor.routeToDLQ(
                                    eventId,
                                    "orders",
                                    "OrderCreatedEvent",
                                    ORDERS_TOPIC,
                                    event.toString().getBytes(),
                                    (Exception) ex,
                                    1
                            );

                            metricsCollector.recordDlqEvent("orders", "OrderCreatedEvent", "KAFKA_PUBLISH_ERROR");
                        } else {
                            log.info("Successfully published order event: {}", eventId);
                        }
                    });

        } catch (Exception e) {
            log.error("Error processing order event: {}", eventId, e);
            metricsCollector.recordDlqEvent("orders", "OrderCreatedEvent", "PROCESSING_ERROR");

            // Route to DLQ
            dlqProcessor.routeToDLQ(
                    eventId,
                    "orders",
                    "OrderCreatedEvent",
                    ORDERS_TOPIC,
                    new byte[0],
                    e,
                    0
            );
        }
    }

    private Map<String, Object> buildOrderEvent(
            String eventId,
            String correlationId,
            OrderCreatedRequest request) {

        Map<String, Object> event = new HashMap<>();
        long currentTime = System.currentTimeMillis();

        // Top-level event fields
        event.put("eventId", eventId);
        event.put("occurredOn", currentTime);
        event.put("eventType", "OrderCreated");
        event.put("eventVersion", "1.0");

        // Build payload object (nested structure required by schema)
        Map<String, Object> payload = new HashMap<>();

        // Generate order number from order ID or use timestamp
        long orderNumber = request.getOrderId() != null ?
            Math.abs(request.getOrderId().hashCode()) : currentTime;

        payload.put("orderNumber", orderNumber);
        payload.put("externalId", request.getOrderId());
        payload.put("orderStatus", "PENDING");
        payload.put("locationCode", request.getFacilityId());
        payload.put("locationName", null); // Not provided in request
        payload.put("createDate", currentTime);
        payload.put("createDateTimeZone", "UTC");
        payload.put("createEmployeeCode", request.getRequestedBy());
        payload.put("shipmentType", null); // Not provided in request
        payload.put("priority", request.getPriority());
        payload.put("transactionId", correlationId); // Required by schema

        // Build order items array - must match schema fields
        List<Map<String, Object>> orderItems = new ArrayList<>();
        Map<String, Object> orderItem = new HashMap<>();
        orderItem.put("productFamily", "BLOOD_PRODUCTS");
        orderItem.put("bloodType", request.getBloodType());
        orderItem.put("quantity", request.getQuantity());
        orderItem.put("comments", null);
        orderItem.put("attributes", null);
        orderItems.add(orderItem);

        payload.put("orderItems", orderItems);

        // Put payload into event
        event.put("payload", payload);

        return event;
    }

    /**
     * Converts a Map to an Avro GenericRecord for Kafka serialization
     */
    private GenericRecord convertToGenericRecord(Map<String, Object> eventData) {
        try {
            // Get the latest schema from Schema Registry
            int schemaId = schemaRegistryClient.getLatestSchemaMetadata(ORDER_CREATED_SUBJECT).getId();
            Schema schema = new Schema.Parser().parse(
                    schemaRegistryClient.getSchemaById(schemaId).toString()
            );

            // Create GenericRecord matching the schema structure
            GenericRecord record = new GenericData.Record(schema);

            // Set top-level fields (directly from eventData)
            record.put("eventId", eventData.get("eventId"));
            record.put("occurredOn", eventData.get("occurredOn"));  // Fixed: was "timestamp"
            record.put("eventType", eventData.get("eventType"));
            record.put("eventVersion", eventData.get("eventVersion"));

            // Get the payload Map from eventData
            Map<String, Object> payloadData = (Map<String, Object>) eventData.get("payload");

            // Create payload record
            Schema payloadSchema = schema.getField("payload").schema();
            GenericRecord payload = new GenericData.Record(payloadSchema);

            // Map payload data to schema structure
            payload.put("orderNumber", payloadData.get("orderNumber"));
            payload.put("externalId", payloadData.get("externalId"));
            payload.put("orderStatus", payloadData.get("orderStatus"));
            payload.put("locationCode", payloadData.get("locationCode"));
            payload.put("locationName", payloadData.get("locationName"));
            payload.put("createDate", payloadData.get("createDate"));
            payload.put("createDateTimeZone", payloadData.get("createDateTimeZone"));
            payload.put("createEmployeeCode", payloadData.get("createEmployeeCode"));
            payload.put("shipmentType", payloadData.get("shipmentType"));
            payload.put("priority", payloadData.get("priority"));
            payload.put("shippingMethod", null);
            payload.put("productCategory", null);
            payload.put("desiredShippingDate", null);
            payload.put("shippingCustomerCode", null);
            payload.put("shippingCustomerName", null);
            payload.put("billingCustomerCode", null);
            payload.put("comments", null);
            payload.put("willPickUp", false);
            payload.put("willPickUpPhoneNumber", null);
            payload.put("transactionId", payloadData.get("transactionId")); // Required by schema
            payload.put("quarantinedProducts", null);
            payload.put("labelStatus", null);
            payload.put("version", null);

            // Get order items from payload
            List<Map<String, Object>> orderItemsData = (List<Map<String, Object>>) payloadData.get("orderItems");

            // Create order items array - must match schema fields
            Schema orderItemsSchema = payloadSchema.getField("orderItems").schema();
            Schema orderItemSchema = orderItemsSchema.getElementType();

            List<GenericRecord> orderItemRecords = new ArrayList<>();
            for (Map<String, Object> itemData : orderItemsData) {
                GenericRecord orderItem = new GenericData.Record(orderItemSchema);
                orderItem.put("productFamily", itemData.get("productFamily"));
                orderItem.put("bloodType", itemData.get("bloodType"));
                orderItem.put("quantity", itemData.get("quantity"));
                orderItem.put("comments", itemData.get("comments"));
                orderItem.put("attributes", itemData.get("attributes"));
                orderItemRecords.add(orderItem);
            }

            payload.put("orderItems", orderItemRecords);

            record.put("payload", payload);

            return record;

        } catch (Exception e) {
            log.error("Failed to convert event to GenericRecord", e);
            throw new RuntimeException("Failed to convert event to Avro GenericRecord", e);
        }
    }

    @lombok.Data
    @lombok.Builder
    public static class OrderCreatedRequest {
        private String orderId;
        private String bloodType;
        private int quantity;
        private String priority;
        private String facilityId;
        private String requestedBy;
    }
}
