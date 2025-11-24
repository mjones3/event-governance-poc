# Story: Event Governance Monitoring and Observability

**Story Points**: 5
**Priority**: High (Patient Safety Critical)
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: Monitoring

---

## User Story

**As a** BioPro operations engineer
**I want** comprehensive monitoring and alerting for event governance infrastructure
**So that** I can detect and respond to event processing failures before they impact patient safety

---

## Description

Implement end-to-end monitoring and observability for Event Governance POC covering Kafka health, Schema Registry availability, DLQ message accumulation, event processing latency, and schema validation failures. Critical alerting required for safety-critical event failures (quarantine, test results, product unsuitability) to ensure zero tolerance for lost events.

### Patient Safety Impact
Silent failures in event processing can lead to:
- Quarantine events not processed → unsuitable products released
- Test result exceptions lost → disease transmission risk
- Product unsuitability events dropped → patient harm

Monitoring ensures operational visibility and immediate response to any event processing anomalies affecting patient safety.

---

## Acceptance Criteria

**AC1: Kafka Health Monitoring**
- GIVEN Kafka cluster running POC events
- WHEN monitoring is configured
- THEN following metrics are tracked:
  - Broker availability and uptime
  - Topic partition health
  - Consumer lag per consumer group
  - Message throughput (messages/sec)
  - Disk usage per broker
- AND metrics visible in dashboard
- AND alerts configured for broker failures

**AC2: Schema Registry Monitoring**
- GIVEN Schema Registry managing event schemas
- WHEN monitoring is active
- THEN following metrics are tracked:
  - Schema Registry availability
  - Schema registration success/failure rate
  - Schema validation latency
  - Number of registered schemas
  - API response times
- AND dashboard shows schema health
- AND alerts fire on registry unavailability

**AC3: DLQ Monitoring and Alerting**
- GIVEN DLQ topics capturing failed events
- WHEN monitoring DLQ health
- THEN following metrics are tracked:
  - DLQ message count per topic
  - DLQ message age (time in queue)
  - DLQ message rate (failures/minute)
  - Safety-critical events in DLQ
- AND **critical alerts** fire for:
  - Any QuarantineEvent in DLQ
  - Any TestResultException in DLQ
  - Any ProductUnsuitability event in DLQ
  - DLQ messages older than 1 hour
- AND alerts include event type and failure context

**AC4: Event Processing Metrics**
- GIVEN services consuming events
- WHEN tracking processing performance
- THEN following metrics are collected:
  - Event processing latency (p50, p95, p99)
  - Event processing success/failure rate
  - Events processed per service per minute
  - Retry attempts per event
  - Circuit breaker state changes
- AND metrics available per service and event type

**AC5: Monitoring Dashboard**
- GIVEN all monitoring metrics collected
- WHEN operations team views dashboard
- THEN dashboard displays:
  - Overall system health status (green/yellow/red)
  - Real-time event flow visualization
  - DLQ status with counts per topic
  - Schema Registry health
  - Consumer lag for all groups
  - Alert summary (active alerts)
- AND dashboard auto-refreshes every 30 seconds
- AND dashboard accessible via web browser

**AC6: Alert Integration**
- GIVEN critical event processing failure
- WHEN alert condition is triggered
- THEN alert is sent via:
  - Email to operations team
  - Slack channel (#event-governance-alerts)
  - PagerDuty for safety-critical events
- AND alert includes:
  - Event type and severity
  - Affected service
  - Failure context
  - Runbook link
- AND alert escalates if not acknowledged within 15 minutes

---

## Technical Details

### Monitoring Stack
- **Metrics Collection**: Prometheus with JMX exporter
- **Visualization**: Grafana dashboards
- **Alerting**: Prometheus Alertmanager
- **Log Aggregation**: ELK stack or Splunk (if available)
- **Service Mesh**: Optional (Dynatrace if already deployed)

### Prometheus Configuration
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka:9092']
    metrics_path: '/metrics'

  - job_name: 'schema-registry'
    static_configs:
      - targets: ['schema-registry:8081']
    metrics_path: '/metrics'

  - job_name: 'orders-service'
    static_configs:
      - targets: ['orders-service:8080']
    metrics_path: '/actuator/prometheus'

  - job_name: 'collections-service'
    static_configs:
      - targets: ['collections-service:8080']
    metrics_path: '/actuator/prometheus'

  - job_name: 'manufacturing-service'
    static_configs:
      - targets: ['manufacturing-service:8080']
    metrics_path: '/actuator/prometheus'
```

### Alert Rules (Prometheus)
```yaml
# alerts.yml
groups:
  - name: patient_safety_critical
    interval: 10s
    rules:
      - alert: SafetyCriticalEventInDLQ
        expr: kafka_topic_messages{topic=~".*quarantine.*DLT|.*testresult.*DLT|.*unsuitability.*DLT"} > 0
        for: 1m
        labels:
          severity: critical
          patient_safety: true
        annotations:
          summary: "Safety-critical event in DLQ"
          description: "{{ $labels.topic }} has {{ $value }} failed messages"
          runbook: "https://wiki.biopro.com/runbook/dlq-safety-critical"

      - alert: DLQMessagesAging
        expr: kafka_topic_oldest_message_age{topic=~".*DLT"} > 3600
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "DLQ messages older than 1 hour"
          description: "{{ $labels.topic }} has messages older than 1 hour"

      - alert: SchemaRegistryDown
        expr: up{job="schema-registry"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Schema Registry unavailable"
          description: "Schema Registry has been down for 2 minutes"

      - alert: HighConsumerLag
        expr: kafka_consumer_group_lag > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High consumer lag detected"
          description: "Consumer group {{ $labels.group }} has lag of {{ $value }}"
```

### Grafana Dashboard Panels
1. **System Health Overview**
   - Green/Yellow/Red status indicator
   - Active alerts count
   - Services health status

2. **Event Flow Visualization**
   - Real-time event rate per topic
   - Producer throughput
   - Consumer throughput

3. **DLQ Status**
   - Messages in DLQ per topic
   - DLQ message age heatmap
   - Safety-critical events highlighted

4. **Schema Registry Health**
   - Availability percentage
   - Schema registration rate
   - Validation failures

5. **Consumer Lag**
   - Lag per consumer group
   - Lag trend over time

6. **Service Performance**
   - Event processing latency (p95, p99)
   - Error rate per service
   - Circuit breaker states

---

## Implementation Tasks

### 1. Deploy Monitoring Infrastructure (3 hours)
- [ ] Add Prometheus to docker-compose.yml
- [ ] Add Grafana to docker-compose.yml
- [ ] Configure Prometheus scrape targets
- [ ] Configure persistent storage for metrics
- [ ] Verify Prometheus collecting metrics
- [ ] Access Grafana UI and configure data source

### 2. Configure Kafka Monitoring (2 hours)
- [ ] Deploy JMX exporter for Kafka
- [ ] Configure Kafka metrics export
- [ ] Verify Kafka metrics in Prometheus
- [ ] Test metric collection for topics and consumer groups
- [ ] Document key Kafka metrics

### 3. Configure Service Metrics (3 hours)
- [ ] Add Spring Boot Actuator to all services
- [ ] Enable Prometheus endpoint in application.yml
- [ ] Add custom metrics for DLQ processing
- [ ] Add custom metrics for schema validation
- [ ] Verify metrics exposed at /actuator/prometheus
- [ ] Test metrics collection

### 4. Create Grafana Dashboards (4 hours)
- [ ] Design system health overview dashboard
- [ ] Create event flow visualization panel
- [ ] Create DLQ monitoring dashboard
- [ ] Create Schema Registry dashboard
- [ ] Create consumer lag dashboard
- [ ] Create service performance dashboard
- [ ] Test auto-refresh functionality
- [ ] Export dashboards as JSON

### 5. Configure Alerting (3 hours)
- [ ] Deploy Prometheus Alertmanager
- [ ] Configure alert rules for safety-critical events
- [ ] Configure alert rules for DLQ aging
- [ ] Configure alert rules for Schema Registry
- [ ] Configure alert rules for high consumer lag
- [ ] Test alert firing and routing
- [ ] Document alert escalation procedures

### 6. Integrate Alert Channels (2 hours)
- [ ] Configure email notifications
- [ ] Configure Slack integration
- [ ] Configure PagerDuty integration (if available)
- [ ] Test end-to-end alert delivery
- [ ] Document alert acknowledgment process

---

## Monitoring Metrics Reference

### Kafka Metrics
- `kafka_server_brokerstate` - Broker state (0=Not Running, 3=Running)
- `kafka_topic_partitions` - Number of partitions per topic
- `kafka_consumer_group_lag` - Consumer lag per group
- `kafka_topic_messages` - Message count per topic
- `kafka_network_requestmetrics_requests` - Request rate

### Schema Registry Metrics
- `schema_registry_api_requests_total` - Total API requests
- `schema_registry_api_latency_seconds` - API response time
- `schema_registry_schemas_created_total` - Schemas registered
- `schema_registry_validation_failures_total` - Validation failures

### Service Metrics (Spring Boot Actuator)
- `http_server_requests_seconds` - HTTP request duration
- `jvm_memory_used_bytes` - JVM memory usage
- `kafka_consumer_records_consumed_total` - Events consumed
- `kafka_producer_record_send_total` - Events produced
- `dlq_messages_sent_total` - Custom: DLQ messages sent
- `schema_validation_failures_total` - Custom: Schema validation failures

---

## Testing Strategy

### Monitoring Tests
- Deploy full stack with monitoring
- Verify all metrics endpoints accessible
- Confirm Prometheus scraping all targets
- Validate dashboards display real-time data
- Test dashboard auto-refresh

### Alert Tests
- Trigger safety-critical event failure
- Verify alert fires within 1 minute
- Confirm alert delivered to all channels
- Test alert escalation timing
- Verify alert includes correct context

### Failure Scenarios
- Stop Schema Registry → verify alert
- Stop consumer service → verify lag alert
- Publish invalid event → verify DLQ alert
- Fill DLQ with old messages → verify aging alert

---

## Definition of Done

- [ ] Prometheus deployed and collecting metrics from all targets
- [ ] Grafana deployed with data source configured
- [ ] At least 4 dashboards created (system health, DLQ, schema, services)
- [ ] Alert rules configured for safety-critical events
- [ ] Alerts integrated with at least 2 channels (email, Slack)
- [ ] All alert rules tested and firing correctly
- [ ] Dashboard JSON exported and checked into repository
- [ ] Monitoring runbook created (how to interpret dashboards)
- [ ] Alert response procedures documented
- [ ] Monitoring validated with stakeholder walkthrough

---

## Documentation Deliverables

- Monitoring architecture diagram
- Grafana dashboard user guide
- Alert response runbook
- Metrics reference guide
- Troubleshooting guide for monitoring issues
- Alert escalation procedures

---

## Dashboard Design Mockup

```
┌─────────────────────────────────────────────────────────────┐
│ Event Governance System Health                    🔴 2 ALERTS │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│ │  Kafka   │ │ Schema   │ │  DLQ     │ │ Services │        │
│ │    🟢    │ │ Registry │ │   🔴     │ │   🟢     │        │
│ │  Healthy │ │   🟢     │ │ 2 msgs   │ │ 3/3 up   │        │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────────────────┤
│ Active Alerts                                                │
│ 🔴 CRITICAL: QuarantineEvent in DLQ (2m ago)                │
│ 🟡 WARNING: Consumer lag >1000 on collections-service       │
├─────────────────────────────────────────────────────────────┤
│ Event Flow (last 5 minutes)                                 │
│ Orders: ████████░░ 850 events/min                           │
│ Collections: ███████░░░ 720 events/min                      │
│ Manufacturing: ████░░░░░░ 420 events/min                    │
├─────────────────────────────────────────────────────────────┤
│ DLQ Status                                                   │
│ biopro.orders.events.DLT: 0 messages                        │
│ biopro.collections.events.DLT: 0 messages                   │
│ biopro.quarantine.events.DLT: 2 messages 🔴                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Risk & Mitigation

**Risk**: Monitoring overhead impacts POC performance
- **Mitigation**: Use sampling for high-frequency metrics
- **Mitigation**: Configure appropriate scrape intervals (30s default)

**Risk**: Alert fatigue from false positives
- **Mitigation**: Tune alert thresholds based on POC behavior
- **Mitigation**: Use alert grouping to reduce noise

**Risk**: Monitoring data storage fills disk
- **Mitigation**: Configure retention policy (7 days for POC)
- **Mitigation**: Monitor disk usage with alerts

**Risk**: Alerts not reaching on-call engineer
- **Mitigation**: Test alert delivery end-to-end
- **Mitigation**: Multiple alert channels (email, Slack, PagerDuty)

---

## Future Enhancements

- Distributed tracing with Jaeger
- Log correlation between services
- Anomaly detection with ML models
- Capacity planning dashboards
- SLA/SLO tracking
- Cost monitoring (cloud environments)

---

**Labels**: monitoring, observability, alerting, patient-safety, proof-of-concept
**Created By**: Melvin Jones
