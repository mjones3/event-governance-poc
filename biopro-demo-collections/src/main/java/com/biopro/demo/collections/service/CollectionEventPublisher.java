package com.biopro.demo.collections.service;

import com.biopro.common.core.dlq.processor.DLQProcessor;
import com.biopro.common.integration.schema.SchemaRegistryService;
import com.biopro.common.monitoring.metrics.DlqMetricsCollector;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
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
    private final DLQProcessor dlqProcessor;
    private final DlqMetricsCollector metricsCollector;

    private static final String COLLECTIONS_TOPIC = "biopro.collections.events";

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
        event.put("eventId", eventId);
        event.put("unitNumber", request.getUnitNumber());
        event.put("donationType", request.getDonationType());
        event.put("status", request.getStatus());
        event.put("timestamp", System.currentTimeMillis());
        return event;
    }

    @lombok.Data
    @lombok.Builder
    public static class CollectionReceivedRequest {
        private String unitNumber;
        private String donationType;
        private String status;
    }
}
