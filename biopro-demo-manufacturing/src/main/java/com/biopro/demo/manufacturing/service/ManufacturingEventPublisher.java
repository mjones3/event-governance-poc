package com.biopro.demo.manufacturing.service;

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

    private static final String MANUFACTURING_TOPIC = "biopro.manufacturing.events";
    private static final String MANUFACTURING_SUBJECT = "ApheresisPlasmaProductCreatedEvent";

    public void publishProductCreated(ProductCreatedRequest request) {
        String eventId = UUID.randomUUID().toString();

        try {
            Map<String, Object> event = buildProductEvent(eventId, request);

            SchemaRegistryService.ValidationResult validation =
                    schemaRegistryService.validateEvent("ApheresisPlasmaProductCreatedEvent", event);

            if (!validation.isValid()) {
                log.error("Schema validation failed for event {}: {}",
                        eventId, validation.getErrorMessage());
                metricsCollector.recordSchemaValidation("manufacturing", false);

                dlqProcessor.routeToDLQ(
                        eventId,
                        "manufacturing",
                        "ApheresisPlasmaProductCreatedEvent",
                        MANUFACTURING_TOPIC,
                        event.toString().getBytes(),
                        new RuntimeException("Schema validation failed: " + validation.getErrorMessage()),
                        0
                );
                return;
            }

            metricsCollector.recordSchemaValidation("manufacturing", true);

            // Send as JSON
            kafkaTemplate.send(MANUFACTURING_TOPIC, eventId, event)
                    .whenComplete((sendResult, ex) -> {
                        if (ex != null) {
                            log.error("Failed to publish manufacturing event: {}", eventId, ex);
                            dlqProcessor.routeToDLQ(
                                    eventId,
                                    "manufacturing",
                                    "ApheresisPlasmaProductCreatedEvent",
                                    MANUFACTURING_TOPIC,
                                    event.toString().getBytes(),
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

            dlqProcessor.routeToDLQ(
                    eventId,
                    "manufacturing",
                    "ApheresisPlasmaProductCreatedEvent",
                    MANUFACTURING_TOPIC,
                    new byte[0],
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
        event.put("occurredOnTimeZone", "UTC");
        event.put("eventType", "ApheresisPlasmaProductCreated");
        event.put("eventVersion", "1.0");

        // Build complete payload with all required fields
        Map<String, Object> payload = new HashMap<>();
        payload.put("unitNumber", request.getProductId());
        payload.put("productCode", request.getProductType());
        payload.put("productDescription", "Apheresis Plasma Product");
        payload.put("productFamily", "PLASMA");
        payload.put("completionStage", "FINAL");

        // Weight (optional)
        Map<String, Object> weight = new HashMap<>();
        weight.put("value", 250);
        weight.put("unit", "GRAMS");
        payload.put("weight", weight);

        // Volume (optional)
        Map<String, Object> volume = new HashMap<>();
        volume.put("value", 500);
        volume.put("unit", "MILLILITERS");
        payload.put("volume", volume);

        // Anticoagulant volume (optional)
        payload.put("anticoagulantVolume", null);

        // Required timing fields
        payload.put("drawTime", now);
        payload.put("drawTimeZone", "UTC");
        payload.put("donationType", "ALLOGENEIC");
        payload.put("procedureType", "APHERESIS_PLASMA");
        payload.put("collectionLocation", "LAB-001");
        payload.put("manufacturingLocation", "FAC-001");
        payload.put("aboRh", "OP");
        payload.put("performedBy", "EMP-001");
        payload.put("createDate", now);
        payload.put("createDateTimeZone", "UTC");
        payload.put("expirationDate", null);
        payload.put("expirationTime", null);
        payload.put("collectionTimeZone", "UTC");
        payload.put("bagType", "TRIPLE");
        payload.put("autoConverted", false);
        payload.put("inputProducts", null);
        payload.put("additionalSteps", null);

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
    }
}
