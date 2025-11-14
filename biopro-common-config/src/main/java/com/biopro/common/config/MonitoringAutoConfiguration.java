package com.biopro.common.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.event.EventListener;

/**
 * Monitoring Auto-Configuration for BioPro Event Governance.
 * Supports both Prometheus (local dev) and Dynatrace (production).
 *
 * Configuration:
 * - For Prometheus: Set biopro.monitoring.type=prometheus
 * - For Dynatrace: Set biopro.monitoring.type=dynatrace
 *
 * Prometheus endpoint: /actuator/prometheus
 * Dynatrace: Automatic export via OneAgent
 */
@Slf4j
@Configuration
public class MonitoringAutoConfiguration {

    /**
     * Prometheus configuration (local development)
     */
    @Configuration
    @ConditionalOnProperty(name = "biopro.monitoring.type", havingValue = "prometheus", matchIfMissing = true)
    static class PrometheusConfiguration {

        @EventListener(ApplicationReadyEvent.class)
        public void init() {
            log.info("╔═══════════════════════════════════════════════════════════════════╗");
            log.info("║ BioPro Monitoring: PROMETHEUS                                     ║");
            log.info("║ Metrics endpoint: /actuator/prometheus                           ║");
            log.info("║ Grafana dashboards: http://localhost:3000                        ║");
            log.info("╚═══════════════════════════════════════════════════════════════════╝");
        }
    }

    /**
     * Dynatrace configuration (production)
     */
    @Configuration
    @ConditionalOnProperty(name = "biopro.monitoring.type", havingValue = "dynatrace")
    static class DynatraceConfiguration {

        @EventListener(ApplicationReadyEvent.class)
        public void init() {
            log.info("╔═══════════════════════════════════════════════════════════════════╗");
            log.info("║ BioPro Monitoring: DYNATRACE                                      ║");
            log.info("║ Metrics exported via OneAgent                                     ║");
            log.info("║ Custom business events enabled                                    ║");
            log.info("╚═══════════════════════════════════════════════════════════════════╝");
        }
    }
}
