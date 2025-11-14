package com.biopro.common.monitoring.metrics;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.Duration;

/**
 * Collects and publishes metrics for DLQ operations.
 * Integrates with Micrometer for export to Prometheus, Dynatrace, etc.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class DlqMetricsCollector {

    private final MeterRegistry meterRegistry;

    /**
     * Records an event routed to DLQ
     */
    public void recordDlqEvent(String module, String eventType, String errorType) {
        Counter.builder("biopro.dlq.events.total")
                .tag("module", module)
                .tag("eventType", eventType)
                .tag("errorType", errorType)
                .description("Total number of events routed to DLQ")
                .register(meterRegistry)
                .increment();

        log.debug("Recorded DLQ event metric: module={}, type={}, error={}",
                module, eventType, errorType);
    }

    /**
     * Records a successful reprocessing
     */
    public void recordReprocessingSuccess(String module, String eventType) {
        Counter.builder("biopro.dlq.reprocessing.success")
                .tag("module", module)
                .tag("eventType", eventType)
                .description("Number of successfully reprocessed events")
                .register(meterRegistry)
                .increment();
    }

    /**
     * Records a failed reprocessing
     */
    public void recordReprocessingFailure(String module, String eventType, String reason) {
        Counter.builder("biopro.dlq.reprocessing.failure")
                .tag("module", module)
                .tag("eventType", eventType)
                .tag("reason", reason)
                .description("Number of failed reprocessing attempts")
                .register(meterRegistry)
                .increment();
    }

    /**
     * Records event processing duration
     */
    public void recordProcessingDuration(String module, String eventType, Duration duration) {
        Timer.builder("biopro.event.processing.duration")
                .tag("module", module)
                .tag("eventType", eventType)
                .description("Event processing duration")
                .register(meterRegistry)
                .record(duration);
    }

    /**
     * Records schema validation result
     */
    public void recordSchemaValidation(String module, boolean success) {
        Counter.builder("biopro.schema.validation")
                .tag("module", module)
                .tag("result", success ? "success" : "failure")
                .description("Schema validation results")
                .register(meterRegistry)
                .increment();
    }
}
