package com.biopro.common.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.time.Duration;

/**
 * Configuration properties for BioPro DLQ framework.
 * Allows customization of DLQ behavior, retry policies, circuit breakers, and monitoring.
 */
@Data
@ConfigurationProperties(prefix = "biopro.dlq")
public class BioproDlqProperties {

    /**
     * Enable or disable DLQ processing
     */
    private boolean enabled = true;

    /**
     * Module name (Orders, Collections, Manufacturing, etc.)
     */
    private String moduleName;

    /**
     * DLQ topic configuration
     */
    private DlqTopic dlqTopic = new DlqTopic();

    /**
     * Retry configuration
     */
    private Retry retry = new Retry();

    /**
     * Circuit breaker configuration
     */
    private CircuitBreaker circuitBreaker = new CircuitBreaker();

    /**
     * Monitoring configuration
     */
    private Monitoring monitoring = new Monitoring();

    @Data
    public static class DlqTopic {
        /**
         * DLQ topic name pattern
         */
        private String topicPattern = "biopro.{module}.dlq";

        /**
         * Number of partitions
         */
        private int partitions = 3;

        /**
         * Replication factor
         */
        private int replicationFactor = 3;

        /**
         * Retention period
         */
        private Duration retention = Duration.ofDays(30);
    }

    @Data
    public static class Retry {
        /**
         * Maximum number of retry attempts before sending to DLQ
         */
        private int maxAttempts = 3;

        /**
         * Initial delay between retries
         */
        private Duration initialDelay = Duration.ofSeconds(1);

        /**
         * Backoff multiplier
         */
        private double multiplier = 2.0;

        /**
         * Maximum delay between retries
         */
        private Duration maxDelay = Duration.ofMinutes(5);
    }

    @Data
    public static class CircuitBreaker {
        /**
         * Enable circuit breaker
         */
        private boolean enabled = true;

        /**
         * Failure threshold percentage to open circuit
         */
        private int failureThreshold = 50;

        /**
         * Minimum number of calls before calculating failure rate
         */
        private int minimumNumberOfCalls = 10;

        /**
         * Duration to wait before transitioning from open to half-open
         */
        private Duration waitDurationInOpenState = Duration.ofMinutes(1);

        /**
         * Number of permitted calls in half-open state
         */
        private int permittedNumberOfCallsInHalfOpenState = 3;

        /**
         * Size of the sliding window for recording outcomes
         */
        private int slidingWindowSize = 100;
    }

    @Data
    public static class Monitoring {
        /**
         * Enable monitoring and metrics
         */
        private boolean enabled = true;

        /**
         * Enable Dynatrace business events
         */
        private boolean dynatraceBusinessEventsEnabled = true;

        /**
         * Metrics publish interval
         */
        private Duration publishInterval = Duration.ofSeconds(30);
    }

    /**
     * Gets the DLQ topic name for the configured module
     */
    public String getDlqTopicName() {
        if (moduleName == null || moduleName.isEmpty()) {
            throw new IllegalStateException("Module name must be configured");
        }
        return dlqTopic.getTopicPattern().replace("{module}", moduleName.toLowerCase());
    }
}
