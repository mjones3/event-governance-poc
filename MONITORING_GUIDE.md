# BioPro Event Governance - Monitoring Guide

Complete guide for monitoring with Prometheus (local dev) or Dynatrace (production).

---

## 🎯 Overview

The BioPro Event Governance Framework supports **two monitoring backends**:

1. **Prometheus + Grafana** - For local development
2. **Dynatrace** - For production/enterprise

Switch between them with a single property!

---

## 🚀 Quick Start

### Prometheus (Default - Local Dev)

```bash
# Start infrastructure
tilt up
# OR
docker-compose up -d

# Access Grafana dashboards
open http://localhost:3000

# View raw Prometheus metrics
curl http://localhost:8080/actuator/prometheus
```

### Dynatrace (Production)

```yaml
# application.yml
biopro:
  monitoring:
    type: dynatrace  # Switch to Dynatrace

management:
  metrics:
    export:
      prometheus:
        enabled: false  # Disable Prometheus
      dynatrace:
        enabled: true   # Enable Dynatrace
        uri: ${DYNATRACE_URI}
        api-token: ${DYNATRACE_API_TOKEN}
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  BioPro Services                              │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │Collections│  │  Orders   │  │ Manufact. │               │
│  │   :8081   │  │  :8080    │  │   :8082   │               │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘               │
│        │              │              │                       │
│        │ Micrometer   │              │                       │
│        └──────────────┴──────────────┘                       │
│                       │                                       │
└───────────────────────┼───────────────────────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
    ┌────▼────┐                   ┌────▼────┐
    │Prometheus│                   │Dynatrace│
    │  :9090   │                   │ OneAgent│
    └────┬────┘                   └─────────┘
         │
    ┌────▼────┐
    │ Grafana │
    │  :3000  │
    └─────────┘
```

---

## 📈 Custom BioPro Metrics

All metrics use the `biopro.` prefix for easy filtering.

### DLQ Metrics

**`biopro.dlq.events.total`** - Counter
- Tags: `module`, `eventType`, `errorType`
- Description: Total events routed to DLQ

**`biopro.dlq.reprocessing.success`** - Counter
- Tags: `module`, `eventType`
- Description: Successfully reprocessed events

**`biopro.dlq.reprocessing.failure`** - Counter
- Tags: `module`, `eventType`, `reason`
- Description: Failed reprocessing attempts

### Event Processing Metrics

**`biopro.event.processing.duration`** - Timer
- Tags: `module`, `eventType`
- Description: Event processing duration (histogram)
- Quantiles: p50, p95, p99

### Schema Metrics

**`biopro.schema.validation`** - Counter
- Tags: `module`, `result` (success/failure)
- Description: Schema validation results

**`biopro.schema.operations`** - Counter
- Tags: `module`, `operation`, `result`
- Description: Schema registry operations

### Circuit Breaker Metrics

**`biopro.circuit.breaker.state`** - Gauge
- Tags: `circuit`, `state`
- Description: Circuit breaker state (0=CLOSED, 0.5=HALF_OPEN, 1=OPEN)

### Retry Metrics

**`biopro.retry.attempts`** - Counter
- Tags: `module`, `eventType`, `attemptNumber`
- Description: Retry attempt counts

---

## 🖥️ Prometheus Setup

### Local Development (Docker Compose)

**1. Start Infrastructure**

```bash
cd C:\Users\MelvinJones\work\event-governance\poc
docker-compose up -d
```

This starts:
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3000)
- ✅ Pre-configured scrape targets
- ✅ Pre-loaded BioPro dashboards

**2. Verify Scraping**

```bash
# Check Prometheus targets
open http://localhost:9090/targets

# Should show 3 targets (all UP):
# - biopro-orders (localhost:8080)
# - biopro-collections (localhost:8081)
# - biopro-manufacturing (localhost:8082)
```

**3. View Metrics**

```bash
# Collections service metrics
curl http://localhost:8081/actuator/prometheus | grep biopro

# Orders service metrics
curl http://localhost:8080/actuator/prometheus | grep biopro

# Manufacturing service metrics
curl http://localhost:8082/actuator/prometheus | grep biopro
```

**4. Access Grafana**

```
URL: http://localhost:3000
Username: admin
Password: admin (or anonymous access enabled)
```

Pre-loaded dashboards:
- **BioPro Event Governance - DLQ Metrics**
  - DLQ events by module
  - Schema validation success rate
  - Processing duration (p95)
  - Reprocessing success vs failure
  - Circuit breaker states
  - Retry attempts

---

### Kubernetes (with Tilt)

**1. Start Tilt**

```bash
tilt up
```

**2. Verify Resources**

```bash
kubectl get pods -n biopro-kafka | grep -E "prometheus|grafana"

# Should show:
# prometheus-xxx    1/1   Running
# grafana-xxx       1/1   Running
```

**3. Access via Port Forwarding**

Tilt automatically forwards:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

**4. Check Scrape Configuration**

```bash
# View Prometheus config
kubectl get configmap prometheus-config -n biopro-kafka -o yaml
```

---

## 📊 Grafana Dashboards

### Pre-Loaded Dashboard: BioPro DLQ Metrics

**Panels**:

1. **DLQ Events Total (by Module)**
   - Query: `rate(biopro_dlq_events_total[5m])`
   - Type: Time series graph
   - Shows: Event rates by module and type

2. **Schema Validation Success Rate**
   - Query: `rate(biopro_schema_validation{result="success"}[5m]) / rate(biopro_schema_validation[5m]) * 100`
   - Type: Time series graph
   - Shows: Validation success percentage

3. **Event Processing Duration (p95)**
   - Query: `histogram_quantile(0.95, rate(biopro_event_processing_duration_bucket[5m]))`
   - Type: Time series graph
   - Shows: 95th percentile processing time

4. **Reprocessing Success vs Failure**
   - Queries:
     - Success: `rate(biopro_dlq_reprocessing_success[5m])`
     - Failure: `rate(biopro_dlq_reprocessing_failure[5m])`
   - Type: Time series graph
   - Shows: Reprocessing outcomes

5. **Circuit Breaker State**
   - Query: `biopro_circuit_breaker_state`
   - Type: Stat panel
   - Shows: Current circuit breaker state

6. **Retry Attempts**
   - Query: `rate(biopro_retry_attempts[5m])`
   - Type: Time series graph
   - Shows: Retry rates by attempt number

### Creating Custom Dashboards

**Example: Track Collections Events**

```promql
# Total collection events (last 1h)
sum(increase(biopro_dlq_events_total{module="collections"}[1h]))

# Collection error rate
rate(biopro_dlq_events_total{module="collections",errorType!=""}[5m])

# Average collection processing time
avg(rate(biopro_event_processing_duration_sum{module="collections"}[5m]) /
    rate(biopro_event_processing_duration_count{module="collections"}[5m]))
```

**Steps**:
1. Go to http://localhost:3000
2. Click "+" → "Dashboard"
3. Click "Add new panel"
4. Enter PromQL query
5. Save dashboard

---

## 🔧 Dynatrace Setup

### Configuration

**1. Update application.yml**

```yaml
biopro:
  monitoring:
    type: dynatrace

management:
  metrics:
    export:
      prometheus:
        enabled: false
      dynatrace:
        enabled: true
        uri: ${DYNATRACE_URI}  # e.g., https://YOUR_ENV.live.dynatrace.com/api/v2/metrics/ingest
        api-token: ${DYNATRACE_API_TOKEN}
        v2:
          metric-key-prefix: biopro
          enrich-with-dynatrace-metadata: true
```

**2. Environment Variables**

```bash
export DYNATRACE_URI="https://YOUR_ENV.live.dynatrace.com/api/v2/metrics/ingest"
export DYNATRACE_API_TOKEN="your-api-token"
```

**3. With OneAgent (Recommended)**

If Dynatrace OneAgent is installed:

```yaml
management:
  metrics:
    export:
      dynatrace:
        uri: http://localhost:14499/metrics/ingest  # Local OneAgent
        api-token: not-required-with-oneagent
```

### Custom Business Events

The framework automatically sends custom business events to Dynatrace:

```java
// Usage in your code
@Autowired
private DynatraceCustomMetricsService dynatraceService;

// Record DLQ event
dynatraceService.recordDlqBusinessEvent(
    DlqBusinessEvent.builder()
        .module("orders")
        .eventType("OrderCreatedEvent")
        .priority("HIGH")
        .errorCategory("SCHEMA_VALIDATION")
        .environment("production")
        .build()
);
```

### Dynatrace Dashboards

Create dashboards in Dynatrace using these metrics:

**Custom Metrics**:
- `biopro.dlq.events.total`
- `biopro.dlq.reprocessing`
- `biopro.event.processing.duration`
- `biopro.schema.validation`
- `biopro.circuit.breaker.state`

**Dimensions**:
- `module` - Which BioPro module
- `eventType` - Type of event
- `result` - Success/failure
- `environment` - dev/staging/production

---

## 🔄 Switching Between Prometheus and Dynatrace

### Switch to Prometheus

```yaml
biopro:
  monitoring:
    type: prometheus

management:
  metrics:
    export:
      prometheus:
        enabled: true
      dynatrace:
        enabled: false
```

### Switch to Dynatrace

```yaml
biopro:
  monitoring:
    type: dynatrace

management:
  metrics:
    export:
      prometheus:
        enabled: false
      dynatrace:
        enabled: true
        uri: ${DYNATRACE_URI}
        api-token: ${DYNATRACE_API_TOKEN}
```

### Use Both (Advanced)

```yaml
biopro:
  monitoring:
    type: prometheus  # Primary for logging

management:
  metrics:
    export:
      prometheus:
        enabled: true
      dynatrace:
        enabled: true  # Also export to Dynatrace
```

---

## 📋 Common Queries

### Prometheus PromQL

```promql
# Total DLQ events per module (rate over 5m)
rate(biopro_dlq_events_total[5m])

# Schema validation failure rate
rate(biopro_schema_validation{result="failure"}[5m]) / rate(biopro_schema_validation[5m])

# P99 event processing duration
histogram_quantile(0.99, rate(biopro_event_processing_duration_bucket[5m]))

# Circuit breaker open count
count(biopro_circuit_breaker_state{state="OPEN"})

# Top error types
topk(5, sum by (errorType) (rate(biopro_dlq_events_total[1h])))

# Reprocessing success rate
rate(biopro_dlq_reprocessing_success[5m]) /
  (rate(biopro_dlq_reprocessing_success[5m]) + rate(biopro_dlq_reprocessing_failure[5m]))
```

### Dynatrace DQL

```
// Total DLQ events
timeseries avg(biopro.dlq.events.total), by:{module}

// Schema validation by module
timeseries sum(biopro.schema.validation), by:{module, result}

// Processing duration percentiles
timeseries percentile(biopro.event.processing.duration, 95), by:{module}
```

---

## 🚨 Alerting

### Prometheus Alerts (alerting.yml)

```yaml
groups:
  - name: biopro_dlq_alerts
    interval: 1m
    rules:
      # High DLQ rate
      - alert: HighDLQRate
        expr: rate(biopro_dlq_events_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High DLQ event rate on {{ $labels.module }}"
          description: "DLQ rate is {{ $value }} events/sec"

      # Schema validation failures
      - alert: SchemaValidationFailures
        expr: rate(biopro_schema_validation{result="failure"}[5m]) > 1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Schema validation failures on {{ $labels.module }}"

      # Circuit breaker open
      - alert: CircuitBreakerOpen
        expr: biopro_circuit_breaker_state == 1
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Circuit breaker {{ $labels.circuit }} is OPEN"

      # High processing latency
      - alert: HighProcessingLatency
        expr: histogram_quantile(0.95, rate(biopro_event_processing_duration_bucket[5m])) > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High processing latency on {{ $labels.module }}"
          description: "P95 latency is {{ $value }}ms"
```

### Dynatrace Alerts

Configure in Dynatrace UI:
1. Settings → Anomaly detection → Custom events for alerting
2. Create custom events based on metric thresholds
3. Set up problem notifications (email, Slack, PagerDuty)

---

## 🎓 Best Practices

### 1. Tag Consistently

Always include these tags:
- `module` - BioPro module name
- `environment` - dev/staging/production
- `eventType` - Specific event type

### 2. Use Appropriate Metric Types

- **Counters**: Events, errors, retries (always increasing)
- **Gauges**: Circuit breaker state, queue size
- **Histograms**: Processing duration, payload size

### 3. Monitor Key Metrics

Essential metrics to track:
- ✅ DLQ event rate
- ✅ Schema validation success rate
- ✅ Processing duration (p95, p99)
- ✅ Circuit breaker state
- ✅ Retry success rate

### 4. Set Up Alerts

Critical alerts:
- High DLQ rate (> threshold)
- Schema validation failures
- Circuit breaker open
- High latency (> SLA)

### 5. Dashboard Organization

Group dashboards by:
- **Overview**: High-level metrics for all modules
- **Per-Module**: Detailed metrics for each module
- **Troubleshooting**: Error rates, retries, circuit breakers

---

## 🔍 Troubleshooting

### Prometheus Not Scraping

**Check targets**:
```bash
curl http://localhost:9090/targets
```

**Common issues**:
- Service not exposing /actuator/prometheus
- Firewall blocking port
- Incorrect scrape configuration

**Fix**:
```bash
# Verify endpoint exists
curl http://localhost:8080/actuator/prometheus

# Check application.yml
management:
  endpoints:
    web:
      exposure:
        include: prometheus
```

### Grafana Not Showing Metrics

**Check datasource**:
1. Grafana → Configuration → Data sources
2. Verify Prometheus URL: `http://prometheus:9090`
3. Click "Test" button

**Check queries**:
- Use "Explore" to test PromQL queries
- Verify metric names match exactly

### Dynatrace Metrics Not Appearing

**Verify configuration**:
```bash
# Check application logs
kubectl logs -f deployment/orders-service -n biopro-dlq | grep -i dynatrace
```

**Common issues**:
- Invalid API token
- Incorrect URI
- OneAgent not installed

---

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Dynatrace Metrics API](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2)
- [Micrometer Documentation](https://micrometer.io/docs)
- Main [README.md](README.md)
- [K8S_DEPLOYMENT_GUIDE.md](K8S_DEPLOYMENT_GUIDE.md)

---

**Document Version**: 1.0
**Last Updated**: November 4, 2025
**Author**: Event Governance Team
