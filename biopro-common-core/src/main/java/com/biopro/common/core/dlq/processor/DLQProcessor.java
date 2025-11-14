package com.biopro.common.core.dlq.processor;

import com.biopro.common.core.dlq.model.DLQEvent;
import com.biopro.common.monitoring.metrics.DlqMetricsCollector;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.retry.Retry;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.UUID;

/**
 * Core DLQ processor that handles routing failed events to the Dead Letter Queue.
 * Implements retry logic and circuit breaker patterns for resilience.
 */
@Slf4j
@Service
public class DLQProcessor {

    private final KafkaTemplate<String, Object> dlqKafkaTemplate;
    private final CircuitBreaker circuitBreaker;
    private final Retry retry;
    private final DlqMetricsCollector metricsCollector;

    public DLQProcessor(
            @Qualifier("dlqKafkaTemplate") KafkaTemplate<String, Object> dlqKafkaTemplate,
            CircuitBreaker circuitBreaker,
            Retry retry,
            DlqMetricsCollector metricsCollector) {
        this.dlqKafkaTemplate = dlqKafkaTemplate;
        this.circuitBreaker = circuitBreaker;
        this.retry = retry;
        this.metricsCollector = metricsCollector;
    }

    /**
     * Routes a failed event to the DLQ with comprehensive error context
     */
    public void routeToDLQ(
            String originalEventId,
            String module,
            String eventType,
            String originalTopic,
            byte[] originalPayload,
            Exception exception,
            int retryCount) {

        try {
            DLQEvent dlqEvent = buildDLQEvent(
                    originalEventId,
                    module,
                    eventType,
                    originalTopic,
                    originalPayload,
                    exception,
                    retryCount
            );

            String dlqTopic = buildDLQTopicName(module);

            log.warn("Routing event to DLQ. EventId: {}, Module: {}, EventType: {}, RetryCount: {}, Error: {}",
                    originalEventId, module, eventType, retryCount, exception.getMessage());

            // Record DLQ metrics
            metricsCollector.recordDlqEvent(module, eventType, dlqEvent.getErrorType().name());

            // Send to DLQ with circuit breaker and retry
            String result = executeWithResilience(() -> {
                dlqKafkaTemplate.send(dlqTopic, dlqEvent.getDlqEventId(), dlqEvent)
                        .whenComplete((sendResult, ex) -> {
                            if (ex != null) {
                                log.error("Failed to send event to DLQ: {}", dlqEvent.getDlqEventId(), ex);
                            } else {
                                log.info("Successfully routed event to DLQ: {}", dlqEvent.getDlqEventId());
                            }
                        });
                return "success";
            });

        } catch (Exception e) {
            log.error("Critical failure: Unable to route event to DLQ. EventId: {}", originalEventId, e);
            // In a production system, this would trigger an alert
            // For now, we log critically and continue
        }
    }

    /**
     * Builds a comprehensive DLQ event with all context
     */
    private DLQEvent buildDLQEvent(
            String originalEventId,
            String module,
            String eventType,
            String originalTopic,
            byte[] originalPayload,
            Exception exception,
            int retryCount) {

        return DLQEvent.builder()
                .dlqEventId(UUID.randomUUID().toString())
                .originalEventId(originalEventId)
                .module(module)
                .eventType(eventType)
                .originalTopic(originalTopic)
                .originalPayload(originalPayload)
                .errorType(determineErrorType(exception))
                .errorMessage(extractDetailedErrorMessage(exception))
                .stackTrace(getStackTraceAsString(exception))
                .retryCount(retryCount)
                .priority(determinePriority(module, eventType, exception))
                .originalTimestamp(Instant.now().minusSeconds(retryCount * 2L)) // Estimate
                .dlqTimestamp(Instant.now())
                .correlationId(extractCorrelationId())
                .status(DLQEvent.ReprocessingStatus.PENDING)
                .reprocessingCount(0)
                .build();
    }

    /**
     * Determines the error type based on the exception
     */
    private DLQEvent.ErrorType determineErrorType(Exception exception) {
        String exceptionName = exception.getClass().getSimpleName();

        if (exceptionName.contains("Schema") || exceptionName.contains("Serialization")) {
            return DLQEvent.ErrorType.SCHEMA_VALIDATION;
        } else if (exceptionName.contains("Deserialization")) {
            return DLQEvent.ErrorType.DESERIALIZATION_ERROR;
        } else if (exceptionName.contains("Timeout")) {
            return DLQEvent.ErrorType.TIMEOUT;
        } else if (exceptionName.contains("Business") || exceptionName.contains("Validation")) {
            return DLQEvent.ErrorType.BUSINESS_RULE_VIOLATION;
        } else {
            return DLQEvent.ErrorType.PROCESSING_ERROR;
        }
    }

    /**
     * Determines priority based on module, event type, and error
     */
    private DLQEvent.Priority determinePriority(String module, String eventType, Exception exception) {
        // Emergency events always get CRITICAL priority
        if (eventType.contains("EMERGENCY") || eventType.contains("LIFE_THREATENING")) {
            return DLQEvent.Priority.CRITICAL;
        }

        // Orders module gets high priority
        if ("orders".equalsIgnoreCase(module)) {
            return DLQEvent.Priority.HIGH;
        }

        // Schema validation errors are high priority (likely configuration issue)
        if (determineErrorType(exception) == DLQEvent.ErrorType.SCHEMA_VALIDATION) {
            return DLQEvent.Priority.HIGH;
        }

        return DLQEvent.Priority.MEDIUM;
    }

    /**
     * Builds the DLQ topic name following BioPro naming convention
     */
    private String buildDLQTopicName(String module) {
        return String.format("biopro.%s.dlq", module.toLowerCase());
    }

    /**
     * Extracts correlation ID from current context (simplified for POC)
     */
    private String extractCorrelationId() {
        // In production, this would extract from MDC or trace context
        return UUID.randomUUID().toString();
    }

    /**
     * Extracts detailed error message by walking the exception cause chain.
     * This is especially important for Avro serialization errors where
     * the root cause contains the actual validation failure details.
     */
    private String extractDetailedErrorMessage(Exception exception) {
        StringBuilder details = new StringBuilder();

        // Start with the top-level message
        if (exception.getMessage() != null) {
            details.append(exception.getMessage());
        }

        // Walk the exception chain to find detailed causes
        Throwable cause = exception.getCause();
        int depth = 0;
        final int MAX_DEPTH = 5; // Prevent infinite loops

        while (cause != null && depth < MAX_DEPTH) {
            String causeMessage = cause.getMessage();

            // Only add if the message is different and not null
            if (causeMessage != null && !causeMessage.equals(details.toString())) {
                // For Avro errors, the cause message often contains the actual validation error
                if (details.length() > 0) {
                    details.append(" | Cause: ");
                }
                details.append(causeMessage);
            }

            cause = cause.getCause();
            depth++;
        }

        // If we got nothing, return a default message
        return details.length() > 0 ? details.toString() : "Unknown error";
    }

    /**
     * Converts exception stack trace to string
     */
    private String getStackTraceAsString(Exception exception) {
        StringBuilder sb = new StringBuilder();
        for (StackTraceElement element : exception.getStackTrace()) {
            sb.append(element.toString()).append("\n");
        }
        return sb.toString();
    }

    /**
     * Executes an operation with circuit breaker and retry patterns
     */
    private <T> T executeWithResilience(java.util.function.Supplier<T> supplier) {
        return circuitBreaker.executeSupplier(
                io.github.resilience4j.retry.Retry.decorateSupplier(retry, supplier)
        );
    }
}
