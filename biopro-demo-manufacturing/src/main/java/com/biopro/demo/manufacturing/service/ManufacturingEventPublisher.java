package com.biopro.demo.manufacturing.service;

import com.biopro.common.core.dlq.processor.DLQProcessor;
import com.biopro.common.integration.schema.SchemaRegistryService;
import com.biopro.common.monitoring.metrics.DlqMetricsCollector;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecord;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Service for publishing manufacturing events to Kafka
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ManufacturingEventPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final SchemaRegistryService schemaRegistryService;
    private final SchemaRegistryClient schemaRegistryClient;
    private final DLQProcessor dlqProcessor;
    private final DlqMetricsCollector metricsCollector;
    private final ObjectMapper objectMapper;

    private static final String MANUFACTURING_TOPIC = "biopro.manufacturing.events";
    private static final String MANUFACTURING_SUBJECT = "ApheresisPlasmaProductCreatedEvent";

    public void publishProductCreated(ProductCreatedRequest request) {
        String eventId = UUID.randomUUID().toString();
        Map<String, Object> event = null;

        try {
            event = buildProductEvent(eventId, request);
            String eventPayload = objectMapper.writeValueAsString(event);

            SchemaRegistryService.ValidationResult validation =
                    schemaRegistryService.validateEvent("ApheresisPlasmaProductCreatedEvent", event);

            if (!validation.isValid()) {
                log.error("Schema validation failed for event {}: {}",
                        eventId, validation.getErrorMessage());
                metricsCollector.recordSchemaValidation("manufacturing", false);

                // Route to DLQ with full payload
                dlqProcessor.routeToDLQ(
                        eventId,
                        "manufacturing",
                        "ApheresisPlasmaProductCreatedEvent",
                        MANUFACTURING_TOPIC,
                        eventPayload,
                        new RuntimeException("Schema validation failed: " + validation.getErrorMessage()),
                        0
                );
                return;
            }

            metricsCollector.recordSchemaValidation("manufacturing", true);

            // Convert to GenericRecord for Avro serialization
            // This embeds the schema ID in the message automatically
            GenericRecord avroRecord = convertToGenericRecord(event);

            // Send as Avro (schema ID automatically embedded by KafkaAvroSerializer)
            kafkaTemplate.send(MANUFACTURING_TOPIC, eventId, avroRecord)
                    .whenComplete((sendResult, ex) -> {
                        if (ex != null) {
                            log.error("Failed to publish manufacturing event: {}", eventId, ex);
                            // Route to DLQ with full payload
                            dlqProcessor.routeToDLQ(
                                    eventId,
                                    "manufacturing",
                                    "ApheresisPlasmaProductCreatedEvent",
                                    MANUFACTURING_TOPIC,
                                    eventPayload,
                                    (Exception) ex,
                                    1
                            );
                            metricsCollector.recordDlqEvent("manufacturing", "ApheresisPlasmaProductCreatedEvent", "KAFKA_PUBLISH_ERROR");
                        } else {
                            log.info("Successfully published manufacturing event: {}", eventId);
                        }
                    });

        } catch (Exception e) {
            log.error("Error processing manufacturing event: {}", eventId, e);
            metricsCollector.recordDlqEvent("manufacturing", "ApheresisPlasmaProductCreatedEvent", "PROCESSING_ERROR");

            // Route to DLQ with full payload if available
            String payload = "";
            if (event != null) {
                try {
                    payload = objectMapper.writeValueAsString(event);
                } catch (Exception jsonEx) {
                    payload = event.toString(); // Fallback to toString if JSON serialization fails
                }
            }
            dlqProcessor.routeToDLQ(
                    eventId,
                    "manufacturing",
                    "ApheresisPlasmaProductCreatedEvent",
                    MANUFACTURING_TOPIC,
                    payload,
                    e,
                    0
            );
        }
    }

    private Map<String, Object> buildProductEvent(String eventId, ProductCreatedRequest request) {
        Map<String, Object> event = new HashMap<>();
        long now = System.currentTimeMillis();

        // Event envelope matching ApheresisPlasmaProductCreatedEvent schema
        event.put("eventId", eventId);
        event.put("occurredOn", now);
        event.put("occurredOnTimeZone", request.getOccurredOnTimeZone());
        event.put("eventType", "ApheresisPlasmaProductCreated");
        event.put("eventVersion", "1.0");

        // Build payload - send data EXACTLY as received, no defaults!
        // Schema validation will catch missing required fields
        Map<String, Object> payload = new HashMap<>();
        payload.put("unitNumber", request.getProductId());
        payload.put("productCode", request.getProductType());
        payload.put("productDescription", request.getProductDescription());
        payload.put("productFamily", request.getProductFamily());
        payload.put("completionStage", request.getCompletionStage());
        payload.put("weight", request.getWeight());
        payload.put("volume", request.getVolume());
        payload.put("anticoagulantVolume", request.getAnticoagulantVolume());
        payload.put("drawTime", request.getDrawTime() != null ? request.getDrawTime() : now);
        payload.put("drawTimeZone", request.getDrawTimeZone());
        payload.put("donationType", request.getDonationType());
        payload.put("procedureType", request.getProcedureType());
        payload.put("collectionLocation", request.getCollectionLocation());
        payload.put("manufacturingLocation", request.getManufacturingLocation());
        payload.put("aboRh", request.getAboRh());
        payload.put("performedBy", request.getPerformedBy());
        payload.put("createDate", now);
        payload.put("createDateTimeZone", request.getCreateDateTimeZone());
        payload.put("expirationDate", request.getExpirationDate());
        payload.put("expirationTime", request.getExpirationTime());
        payload.put("collectionTimeZone", request.getCollectionTimeZone());
        payload.put("bagType", request.getBagType());
        payload.put("autoConverted", request.getAutoConverted());
        payload.put("inputProducts", request.getInputProducts());
        payload.put("additionalSteps", request.getAdditionalSteps());

        event.put("payload", payload);
        return event;
    }

    private GenericRecord convertToGenericRecord(Map<String, Object> eventData) {
        try {
            // Get the latest schema from Schema Registry
            int schemaId = schemaRegistryClient.getLatestSchemaMetadata(MANUFACTURING_SUBJECT).getId();
            Schema schema = new Schema.Parser().parse(
                    schemaRegistryClient.getSchemaById(schemaId).toString()
            );

            // Create GenericRecord matching the schema structure
            GenericRecord record = new GenericData.Record(schema);

            // Set top-level event envelope fields
            record.put("eventId", eventData.get("eventId"));
            record.put("occurredOn", eventData.get("occurredOn"));
            record.put("occurredOnTimeZone", eventData.get("occurredOnTimeZone"));
            record.put("eventType", eventData.get("eventType"));
            record.put("eventVersion", eventData.get("eventVersion"));

            // Get the payload Map from eventData
            Map<String, Object> payloadData = (Map<String, Object>) eventData.get("payload");

            // Create payload record
            Schema payloadSchema = schema.getField("payload").schema();
            GenericRecord payload = new GenericData.Record(payloadSchema);

            // Map all payload fields to schema structure
            payload.put("unitNumber", payloadData.get("unitNumber"));
            payload.put("productCode", payloadData.get("productCode"));
            payload.put("productDescription", payloadData.get("productDescription"));
            payload.put("productFamily", payloadData.get("productFamily"));
            payload.put("completionStage", payloadData.get("completionStage"));

            // Handle weight (optional nested record)
            Map<String, Object> weightData = (Map<String, Object>) payloadData.get("weight");
            if (weightData != null) {
                Schema weightSchema = payloadSchema.getField("weight").schema().getTypes().get(1);
                GenericRecord weight = new GenericData.Record(weightSchema);
                weight.put("value", weightData.get("value"));
                weight.put("unit", weightData.get("unit"));
                payload.put("weight", weight);
            } else {
                payload.put("weight", null);
            }

            // Handle volume (optional nested record)
            Map<String, Object> volumeData = (Map<String, Object>) payloadData.get("volume");
            if (volumeData != null) {
                Schema volumeSchema = payloadSchema.getField("volume").schema().getTypes().get(1);
                GenericRecord volume = new GenericData.Record(volumeSchema);
                volume.put("value", volumeData.get("value"));
                volume.put("unit", volumeData.get("unit"));
                payload.put("volume", volume);
            } else {
                payload.put("volume", null);
            }

            payload.put("anticoagulantVolume", payloadData.get("anticoagulantVolume"));
            payload.put("drawTime", payloadData.get("drawTime"));
            payload.put("drawTimeZone", payloadData.get("drawTimeZone"));
            payload.put("donationType", payloadData.get("donationType"));
            payload.put("procedureType", payloadData.get("procedureType"));
            payload.put("collectionLocation", payloadData.get("collectionLocation"));
            payload.put("manufacturingLocation", payloadData.get("manufacturingLocation"));
            payload.put("aboRh", payloadData.get("aboRh"));
            payload.put("performedBy", payloadData.get("performedBy"));
            payload.put("createDate", payloadData.get("createDate"));
            payload.put("createDateTimeZone", payloadData.get("createDateTimeZone"));
            payload.put("expirationDate", payloadData.get("expirationDate"));
            payload.put("expirationTime", payloadData.get("expirationTime"));
            payload.put("collectionTimeZone", payloadData.get("collectionTimeZone"));
            payload.put("bagType", payloadData.get("bagType"));
            payload.put("autoConverted", payloadData.get("autoConverted"));
            payload.put("inputProducts", payloadData.get("inputProducts"));
            payload.put("additionalSteps", payloadData.get("additionalSteps"));

            record.put("payload", payload);

            return record;

        } catch (Exception e) {
            log.error("Failed to convert event to GenericRecord", e);
            throw new RuntimeException("Failed to convert event to Avro GenericRecord", e);
        }
    }

    @lombok.Data
    @lombok.Builder
    @lombok.NoArgsConstructor
    @lombok.AllArgsConstructor
    public static class ProductCreatedRequest {
        private String productId;
        private String productType;
        private String status;
        private String occurredOnTimeZone;
        private String productDescription;
        private String productFamily;
        private String completionStage;
        private Object weight;
        private Object volume;
        private Object anticoagulantVolume;
        private Long drawTime;
        private String drawTimeZone;
        private String donationType;
        private String procedureType;
        private String collectionLocation;
        private String manufacturingLocation;
        private String aboRh;
        private String performedBy;
        private String createDateTimeZone;
        private Object expirationDate;
        private Object expirationTime;
        private String collectionTimeZone;
        private String bagType;
        private Boolean autoConverted;
        private Object inputProducts;
        private Object additionalSteps;
    }
}
