package com.biopro.demo.collections.service;

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
 * Service for publishing collection events to Kafka
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CollectionEventPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final SchemaRegistryService schemaRegistryService;
    private final SchemaRegistryClient schemaRegistryClient;
    private final DLQProcessor dlqProcessor;
    private final DlqMetricsCollector metricsCollector;

    private static final String COLLECTIONS_TOPIC = "biopro.collections.events";
    private static final String COLLECTIONS_SUBJECT = "CollectionReceivedEvent";

    public void publishCollectionReceived(CollectionReceivedRequest request) {
        String eventId = UUID.randomUUID().toString();

        try {
            Map<String, Object> event = buildCollectionEvent(eventId, request);

            SchemaRegistryService.ValidationResult validation =
                    schemaRegistryService.validateEvent("CollectionReceivedEvent", event);

            if (!validation.isValid()) {
                log.error("Schema validation failed for event {}: {}",
                        eventId, validation.getErrorMessage());
                metricsCollector.recordSchemaValidation("collections", false);

                dlqProcessor.routeToDLQ(
                        eventId,
                        "collections",
                        "CollectionReceivedEvent",
                        COLLECTIONS_TOPIC,
                        event.toString().getBytes(),
                        new RuntimeException("Schema validation failed: " + validation.getErrorMessage()),
                        0
                );
                return;
            }

            metricsCollector.recordSchemaValidation("collections", true);

            // Send as JSON
            kafkaTemplate.send(COLLECTIONS_TOPIC, eventId, event)
                    .whenComplete((sendResult, ex) -> {
                        if (ex != null) {
                            log.error("Failed to publish collection event: {}", eventId, ex);
                            dlqProcessor.routeToDLQ(
                                    eventId,
                                    "collections",
                                    "CollectionReceivedEvent",
                                    COLLECTIONS_TOPIC,
                                    event.toString().getBytes(),
                                    (Exception) ex,
                                    1
                            );
                            metricsCollector.recordDlqEvent("collections", "CollectionReceivedEvent", "KAFKA_PUBLISH_ERROR");
                        } else {
                            log.info("Successfully published collection event: {}", eventId);
                        }
                    });

        } catch (Exception e) {
            log.error("Error processing collection event: {}", eventId, e);
            metricsCollector.recordDlqEvent("collections", "CollectionReceivedEvent", "PROCESSING_ERROR");

            dlqProcessor.routeToDLQ(
                    eventId,
                    "collections",
                    "CollectionReceivedEvent",
                    COLLECTIONS_TOPIC,
                    new byte[0],
                    e,
                    0
            );
        }
    }

    private Map<String, Object> buildCollectionEvent(String eventId, CollectionReceivedRequest request) {
        Map<String, Object> event = new HashMap<>();
        long now = System.currentTimeMillis();

        // Required fields matching CollectionReceivedEvent schema
        event.put("unitNumber", request.getUnitNumber());
        event.put("status", request.getStatus());
        event.put("bagType", request.getBagType() != null ? request.getBagType() : "TRIPLE");
        event.put("drawTime", now);
        event.put("drawTimeZone", "UTC");
        event.put("withdrawalTime", now);
        event.put("withdrawalTimeZone", "UTC");
        event.put("donationType", request.getDonationType());
        event.put("procedureType", request.getProcedureType() != null ? request.getProcedureType() : "APHERESIS");
        event.put("collectionLocation", request.getCollectionLocation() != null ? request.getCollectionLocation() : "LAB-001");
        event.put("aboRh", request.getAboRh() != null ? request.getAboRh() : "OP");

        // Optional fields
        event.put("machineSerialNumber", null);
        event.put("machineType", null);
        event.put("donationProperties", null);
        event.put("drawProperties", null);

        // Required volumes array with sample plasma volume
        Map<String, Object> plasmaVolume = new HashMap<>();
        plasmaVolume.put("type", "PLASMA");
        plasmaVolume.put("amount", 600);
        plasmaVolume.put("excludeInCalculation", false);

        Map<String, Object> anticoagVolume = new HashMap<>();
        anticoagVolume.put("type", "ANTICOAGULANT");
        anticoagVolume.put("amount", 100);
        anticoagVolume.put("excludeInCalculation", false);

        event.put("volumes", java.util.List.of(plasmaVolume, anticoagVolume));

        return event;
    }

    private GenericRecord convertToGenericRecord(Map<String, Object> eventData) {
        try {
            // Get the latest schema from Schema Registry
            int schemaId = schemaRegistryClient.getLatestSchemaMetadata(COLLECTIONS_SUBJECT).getId();
            Schema schema = new Schema.Parser().parse(
                    schemaRegistryClient.getSchemaById(schemaId).toString()
            );

            // Create GenericRecord matching the schema structure (CollectionReceivedEvent has no envelope, it's flat)
            GenericRecord record = new GenericData.Record(schema);

            // Map all fields directly to the record
            record.put("unitNumber", eventData.get("unitNumber"));
            record.put("status", eventData.get("status"));
            record.put("bagType", eventData.get("bagType"));
            record.put("drawTime", eventData.get("drawTime"));
            record.put("drawTimeZone", eventData.get("drawTimeZone"));
            record.put("withdrawalTime", eventData.get("withdrawalTime"));
            record.put("withdrawalTimeZone", eventData.get("withdrawalTimeZone"));
            record.put("donationType", eventData.get("donationType"));
            record.put("procedureType", eventData.get("procedureType"));
            record.put("collectionLocation", eventData.get("collectionLocation"));
            record.put("aboRh", eventData.get("aboRh"));
            record.put("machineSerialNumber", eventData.get("machineSerialNumber"));
            record.put("machineType", eventData.get("machineType"));
            record.put("donationProperties", eventData.get("donationProperties"));
            record.put("drawProperties", eventData.get("drawProperties"));

            // Handle volumes array
            List<Map<String, Object>> volumesData = (List<Map<String, Object>>) eventData.get("volumes");
            Schema volumesSchema = schema.getField("volumes").schema();
            Schema volumeSchema = volumesSchema.getElementType();

            List<GenericRecord> volumeRecords = new ArrayList<>();
            for (Map<String, Object> volumeData : volumesData) {
                GenericRecord volume = new GenericData.Record(volumeSchema);
                volume.put("type", volumeData.get("type"));
                volume.put("amount", volumeData.get("amount"));
                volume.put("excludeInCalculation", volumeData.get("excludeInCalculation"));
                volumeRecords.add(volume);
            }

            record.put("volumes", volumeRecords);

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
    public static class CollectionReceivedRequest {
        private String unitNumber;
        private String donationType;
        private String status;
        private String bagType;
        private String procedureType;
        private String collectionLocation;
        private String aboRh;
    }
}
