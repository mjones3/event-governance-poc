package com.biopro.demo.manufacturing.service;

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
 * Service for publishing manufacturing events to Kafka
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ManufacturingEventPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final SchemaRegistryService schemaRegistryService;
    private final DLQProcessor dlqProcessor;
    private final DlqMetricsCollector metricsCollector;

    private static final String MANUFACTURING_TOPIC = "biopro.manufacturing.events";

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
        event.put("eventId", eventId);
        event.put("productId", request.getProductId());
        event.put("productType", request.getProductType());
        event.put("status", request.getStatus());
        event.put("timestamp", System.currentTimeMillis());
        return event;
    }

    @lombok.Data
    @lombok.Builder
    public static class ProductCreatedRequest {
        private String productId;
        private String productType;
        private String status;
    }
}
