package com.biopro.common.config;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import io.github.resilience4j.retry.RetryRegistry;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;

/**
 * Spring Boot Auto-Configuration for BioPro DLQ framework.
 * Automatically configures all necessary beans when the starter is added to a project.
 */
@Slf4j
@AutoConfiguration
@EnableConfigurationProperties(BioproDlqProperties.class)
@ConditionalOnProperty(prefix = "biopro.dlq", name = "enabled", havingValue = "true", matchIfMissing = true)
@ComponentScan(basePackages = {
        "com.biopro.common.core",
        "com.biopro.common.integration",
        "com.biopro.common.security",
        "com.biopro.common.monitoring"
})
public class BioproDlqAutoConfiguration {

    /**
     * Creates Resilience4j Circuit Breaker for DLQ operations
     */
    @Bean
    public CircuitBreaker dlqCircuitBreaker(BioproDlqProperties properties) {
        log.info("Configuring DLQ Circuit Breaker with properties: {}", properties.getCircuitBreaker());

        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
                .failureRateThreshold(properties.getCircuitBreaker().getFailureThreshold())
                .minimumNumberOfCalls(properties.getCircuitBreaker().getMinimumNumberOfCalls())
                .waitDurationInOpenState(properties.getCircuitBreaker().getWaitDurationInOpenState())
                .permittedNumberOfCallsInHalfOpenState(
                        properties.getCircuitBreaker().getPermittedNumberOfCallsInHalfOpenState())
                .slidingWindowSize(properties.getCircuitBreaker().getSlidingWindowSize())
                .build();

        CircuitBreakerRegistry registry = CircuitBreakerRegistry.of(config);
        CircuitBreaker circuitBreaker = registry.circuitBreaker("dlq-circuit-breaker");

        // Add event listeners for monitoring
        circuitBreaker.getEventPublisher()
                .onStateTransition(event -> {
                    log.warn("Circuit Breaker state transition: {} -> {}",
                            event.getStateTransition().getFromState(),
                            event.getStateTransition().getToState());
                })
                .onFailureRateExceeded(event -> {
                    log.error("Circuit Breaker failure rate exceeded: {}%",
                            event.getFailureRate());
                });

        return circuitBreaker;
    }

    /**
     * Creates Resilience4j Retry for DLQ operations
     */
    @Bean
    public Retry dlqRetry(BioproDlqProperties properties) {
        log.info("Configuring DLQ Retry with properties: {}", properties.getRetry());

        RetryConfig config = RetryConfig.custom()
                .maxAttempts(properties.getRetry().getMaxAttempts())
                .waitDuration(properties.getRetry().getInitialDelay())
                .build();

        RetryRegistry registry = RetryRegistry.of(config);
        Retry retry = registry.retry("dlq-retry");

        // Add event listeners for monitoring
        retry.getEventPublisher()
                .onRetry(event -> {
                    log.warn("Retry attempt {} for DLQ operation. Last exception: {}",
                            event.getNumberOfRetryAttempts(),
                            event.getLastThrowable().getMessage());
                })
                .onError(event -> {
                    log.error("All retry attempts exhausted for DLQ operation after {} attempts",
                            event.getNumberOfRetryAttempts());
                });

        return retry;
    }

    /**
     * Bean post-processor to log successful initialization
     */
    @Bean
    public BioproDlqInitializationLogger initializationLogger(BioproDlqProperties properties) {
        return new BioproDlqInitializationLogger(properties);
    }

    /**
     * Logs successful initialization of BioPro DLQ framework
     */
    @Slf4j
    public static class BioproDlqInitializationLogger {
        public BioproDlqInitializationLogger(BioproDlqProperties properties) {
            log.info("┌─────────────────────────────────────────────────────────┐");
            log.info("│  BioPro Event Governance Framework Initialized          │");
            log.info("├─────────────────────────────────────────────────────────┤");
            log.info("│  Module: {}", String.format("%-45s", properties.getModuleName() != null ? properties.getModuleName() : "Not Set") + "│");
            log.info("│  DLQ Enabled: {}", String.format("%-41s", properties.isEnabled()) + "│");
            log.info("│  Retry Max Attempts: {}", String.format("%-34s", properties.getRetry().getMaxAttempts()) + "│");
            log.info("│  Circuit Breaker: {}", String.format("%-38s", properties.getCircuitBreaker().isEnabled() ? "Enabled" : "Disabled") + "│");
            log.info("└─────────────────────────────────────────────────────────┘");
        }
    }
}
