package com.biopro.common.core.dlq.model;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.Map;

/**
 * Represents an event that has been routed to the Dead Letter Queue (DLQ).
 * Contains the original event data, error information, and business context.
 */
@Data
@Builder
public class DLQEvent {

    /**
     * Unique identifier for this DLQ event
     */
    private String dlqEventId;

    /**
     * Original event ID from the source event
     */
    private String originalEventId;

    /**
     * BioPro module that generated the event (Orders, Collections, Manufacturing, etc.)
     */
    private String module;

    /**
     * Type of the original event
     */
    private String eventType;

    /**
     * Original Kafka topic the event was published to
     */
    private String originalTopic;

    /**
     * Original event payload as plaintext JSON for human readability
     */
    private String originalPayload;

    /**
     * Error category (e.g., SCHEMA_VALIDATION, PROCESSING_ERROR, BUSINESS_RULE_VIOLATION)
     */
    private ErrorType errorType;

    /**
     * Detailed error message
     */
    private String errorMessage;

    /**
     * Stack trace of the exception (if applicable)
     */
    private String stackTrace;

    /**
     * Number of retry attempts made before routing to DLQ
     */
    private int retryCount;

    /**
     * Priority level for reprocessing
     */
    private Priority priority;

    /**
     * Timestamp when the original event was first received
     */
    private Instant originalTimestamp;

    /**
     * Timestamp when the event was routed to DLQ
     */
    private Instant dlqTimestamp;

    /**
     * Correlation ID for distributed tracing
     */
    private String correlationId;

    /**
     * Business context metadata
     */
    private Map<String, String> businessContext;

    /**
     * Reprocessing status
     */
    private ReprocessingStatus status;

    /**
     * Timestamp of last reprocessing attempt (if any)
     */
    private Instant lastReprocessingAttempt;

    /**
     * Number of reprocessing attempts
     */
    private int reprocessingCount;

    /**
     * User who initiated reprocessing (if manual)
     */
    private String reprocessedBy;

    public enum ErrorType {
        SCHEMA_VALIDATION,
        DESERIALIZATION_ERROR,
        PROCESSING_ERROR,
        BUSINESS_RULE_VIOLATION,
        TIMEOUT,
        RESOURCE_UNAVAILABLE,
        UNKNOWN
    }

    public enum Priority {
        LOW,
        MEDIUM,
        HIGH,
        CRITICAL
    }

    public enum ReprocessingStatus {
        PENDING,
        IN_PROGRESS,
        REPROCESSED_SUCCESS,
        REPROCESSED_FAILED,
        ARCHIVED,
        REQUIRES_MANUAL_INTERVENTION
    }
}
