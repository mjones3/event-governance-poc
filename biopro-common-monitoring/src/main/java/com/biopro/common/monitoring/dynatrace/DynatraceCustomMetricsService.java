package com.biopro.common.monitoring.dynatrace;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tag;
import io.micrometer.core.instrument.Tags;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * Dynatrace Custom Metrics Service for BioPro Event Governance.
 * Publishes custom statistics and business metrics to Dynatrace.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DynatraceCustomMetricsService {

    private final MeterRegistry meterRegistry;

    /**
     * Records a custom DLQ business event for Dynatrace
     */
    public void recordDlqBusinessEvent(DlqBusinessEvent event) {
        // Create custom metric with Dynatrace dimensions
        meterRegistry.counter(
                "biopro.dlq.business.event",
                Tags.of(
                        Tag.of("module", event.getModule()),
                        Tag.of("eventType", event.getEventType()),
                        Tag.of("priority", event.getPriority()),
                        Tag.of("errorCategory", event.getErrorCategory()),
                        Tag.of("environment", event.getEnvironment())
                )
        ).increment();

        log.debug("Recorded Dynatrace business event: module={}, type={}, priority={}",
                event.getModule(), event.getEventType(), event.getPriority());
    }

    /**
     * Records processing duration as a custom statistic
     */
    public void recordProcessingDuration(String module, String eventType, long durationMs) {
        meterRegistry.timer(
                "biopro.event.processing.duration",
                Tags.of(
                        Tag.of("module", module),
                        Tag.of("eventType", eventType)
                )
        ).record(java.time.Duration.ofMillis(durationMs));
    }

    /**
     * Records schema validation metrics
     */
    public void recordSchemaMetric(String module, String operation, boolean success) {
        meterRegistry.counter(
                "biopro.schema.operations",
                Tags.of(
                        Tag.of("module", module),
                        Tag.of("operation", operation),
                        Tag.of("result", success ? "success" : "failure")
                )
        ).increment();
    }

    /**
     * Records circuit breaker state changes
     */
    public void recordCircuitBreakerState(String circuitName, String state) {
        meterRegistry.gauge(
                "biopro.circuit.breaker.state",
                Tags.of(
                        Tag.of("circuit", circuitName),
                        Tag.of("state", state)
                ),
                stateToNumeric(state)
        );

        log.info("Circuit breaker state changed: {} -> {}", circuitName, state);
    }

    /**
     * Records retry attempts
     */
    public void recordRetryAttempt(String module, String eventType, int attemptNumber) {
        meterRegistry.counter(
                "biopro.retry.attempts",
                Tags.of(
                        Tag.of("module", module),
                        Tag.of("eventType", eventType),
                        Tag.of("attemptNumber", String.valueOf(attemptNumber))
                )
        ).increment();
    }

    /**
     * Records reprocessing metrics
     */
    public void recordReprocessing(String module, String eventType, String outcome) {
        meterRegistry.counter(
                "biopro.dlq.reprocessing",
                Tags.of(
                        Tag.of("module", module),
                        Tag.of("eventType", eventType),
                        Tag.of("outcome", outcome)
                )
        ).increment();
    }

    /**
     * Custom business event for DLQ operations
     */
    @lombok.Data
    @lombok.Builder
    public static class DlqBusinessEvent {
        private String module;
        private String eventType;
        private String priority;
        private String errorCategory;
        private String environment;
        private Map<String, String> customProperties;

        public Map<String, String> getCustomProperties() {
            if (customProperties == null) {
                customProperties = new HashMap<>();
            }
            return customProperties;
        }
    }

    /**
     * Converts circuit breaker state to numeric value for Dynatrace
     */
    private double stateToNumeric(String state) {
        return switch (state.toUpperCase()) {
            case "CLOSED" -> 0.0;
            case "OPEN" -> 1.0;
            case "HALF_OPEN" -> 0.5;
            default -> -1.0;
        };
    }
}
