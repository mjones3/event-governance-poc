package com.biopro.demo.collections.service;

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
    private final ObjectMapper objectMapper;

    private static final String COLLECTIONS_TOPIC = "biopro.collections.events";
    private static final String COLLECTIONS_SUBJECT = "CollectionReceivedEvent";

    public void publishCollectionReceived(CollectionReceivedRequest request) {
        String eventId = UUID.randomUUID().toString();
        Map<String, Object> event = null;

        try {
            event = buildCollectionEvent(eventId, request);
            String eventPayload = objectMapper.writeValueAsString(event);

            SchemaRegistryService.ValidationResult validation =
                    schemaRegistryService.validateEvent("CollectionReceivedEvent", event);

            if (!validation.isValid()) {
                log.error("Schema validation failed for event {}: {}",
                        eventId, validation.getErrorMessage());
                metricsCollector.recordSchemaValidation("collections", false);

                // Route to DLQ with full payload
                dlqProcessor.routeToDLQ(
                        eventId,
                        "collections",
                        "CollectionReceivedEvent",
                        COLLECTIONS_TOPIC,
                        eventPayload,
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
                            // Route to DLQ with full payload
                            dlqProcessor.routeToDLQ(
                                    eventId,
                                    "collections",
                                    "CollectionReceivedEvent",
                                    COLLECTIONS_TOPIC,
                                    eventPayload,
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
                    "collections",
                    "CollectionReceivedEvent",
                    COLLECTIONS_TOPIC,
                    payload,
                    e,
                    0
            );
        }
    }

    private Map<String, Object> buildCollectionEvent(String eventId, CollectionReceivedRequest request) {
        Map<String, Object> event = new HashMap<>();
        long now = System.currentTimeMillis();

        // Send data EXACTLY as received - no defaults!
        // Schema validation will catch missing required fields
        event.put("unitNumber", request.getUnitNumber());
        event.put("status", request.getStatus());
        event.put("bagType", request.getBagType());
        event.put("drawTime", now);
        event.put("drawTimeZone", request.getDrawTimeZone());
        event.put("withdrawalTime", now);
        event.put("withdrawalTimeZone", request.getWithdrawalTimeZone());
        event.put("donationType", request.getDonationType());
        event.put("procedureType", request.getProcedureType());
        event.put("collectionLocation", request.getCollectionLocation());
        event.put("aboRh", request.getAboRh());

        // Optional fields - pass as-is
        event.put("machineSerialNumber", request.getMachineSerialNumber());
        event.put("machineType", request.getMachineType());
        event.put("donationProperties", request.getDonationProperties());
        event.put("drawProperties", request.getDrawProperties());

        // Volumes - only create if provided, otherwise send empty or null
        if (request.getVolumes() != null) {
            event.put("volumes", request.getVolumes());
        } else {
            event.put("volumes", new ArrayList<>());
        }

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
        private String drawTimeZone;
        private String withdrawalTimeZone;
        private String machineSerialNumber;
        private String machineType;
        private Object donationProperties;
        private Object drawProperties;
        private Object volumes;
    }
}
