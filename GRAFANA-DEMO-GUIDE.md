# BioPro DLQ Framework - Grafana Monitoring Demo Guide

**Visualizing Event Governance Metrics for Maximum Impact**

## Table of Contents
- [Overview](#overview)
- [Quick Setup](#quick-setup)
- [Key Metrics](#key-metrics)
- [Dashboard Panels](#dashboard-panels)
- [Creating the Dashboard](#creating-the-dashboard)
- [Demo Scenario](#demo-scenario)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide shows you how to create compelling Grafana dashboards that visualize the BioPro Event Governance Framework in action. These visualizations are perfect for demos, showcasing the framework's error handling, DLQ routing, and system health.

### What You'll Visualize
- **Event throughput** - Total events processed per second
- **DLQ routing rate** - Percentage of events going to DLQ
- **Error distribution** - Breakdown by error type
- **Circuit breaker state** - Real-time resilience status
- **Schema validation metrics** - Success vs failure rates
- **Processing latency** - p50, p95, p99 percentiles

---

## Quick Setup

### 1. Access Grafana

Open Grafana in your browser:
```
http://localhost:3000
```

**Default Credentials:**
- Username: `admin`
- Password: `admin` (or set to auto-login in docker-compose.yml)

### 2. Verify Prometheus Data Source

1. Navigate to **Configuration** → **Data Sources**
2. Confirm **Prometheus** is listed
3. Test the connection (should see "Data source is working")

If not configured:
1. Click **Add data source**
2. Select **Prometheus**
3. URL: `http://prometheus:9090`
4. Click **Save & Test**

---

## Key Metrics

### Available Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `biopro_dlq_events_total` | Counter | Total DLQ events by module and error type |
| `biopro_schema_validation_errors_total` | Counter | Schema validation failures by module |
| `biopro_schema_validation_success_total` | Counter | Schema validation successes by module |
| `biopro_circuit_breaker_state` | Gauge | Circuit breaker state (0=Closed, 1=Open, 2=HalfOpen) |
| `biopro_dlq_processing_duration_seconds` | Histogram | DLQ processing duration with quantiles |
| `biopro_event_processing_duration_seconds` | Histogram | End-to-end event processing time |
| `biopro_kafka_publish_errors_total` | Counter | Kafka publish failures |
| `biopro_retry_attempts_total` | Counter | Retry attempt counts |

### Query Examples

**Total DLQ Events per Module:**
```promql
sum by(module) (biopro_dlq_events_total)
```

**DLQ Rate (percentage of events going to DLQ):**
```promql
100 * (
  rate(biopro_dlq_events_total[5m])
  /
  (rate(biopro_schema_validation_success_total[5m]) + rate(biopro_dlq_events_total[5m]))
)
```

**Error Distribution by Type:**
```promql
sum by(error_type) (rate(biopro_dlq_events_total[5m]))
```

**Circuit Breaker Status:**
```promql
biopro_circuit_breaker_state{module="orders"}
```

**P95 Processing Latency:**
```promql
histogram_quantile(0.95, rate(biopro_event_processing_duration_seconds_bucket[5m]))
```

---

## Dashboard Panels

### Panel 1: Event Throughput (Graph)

**Visualization Type:** Time series graph

**Query:**
```promql
sum(rate(biopro_schema_validation_success_total[1m])) by (module)
```

**Configuration:**
- **Title:** Event Throughput by Module
- **Y-Axis:** Events/second
- **Legend:** Show, Bottom
- **Colors:** Green for success
- **Time range:** Last 15 minutes
- **Refresh:** 5s

**Why This Matters:** Shows real-time event processing across all modules. During demo, you'll see spikes when running the load generation script.

---

### Panel 2: DLQ Rate (Stat + Gauge)

**Visualization Type:** Gauge

**Query:**
```promql
100 * (
  sum(rate(biopro_dlq_events_total{module="orders"}[5m]))
  /
  (sum(rate(biopro_schema_validation_success_total{module="orders"}[5m])) + sum(rate(biopro_dlq_events_total{module="orders"}[5m])))
)
```

**Configuration:**
- **Title:** Orders DLQ Rate
- **Unit:** Percent (0-100)
- **Thresholds:**
  - Green: 0-5%
  - Yellow: 5-15%
  - Red: >15%
- **Display:** Gauge with percentage

**Why This Matters:** Critical health metric. Low DLQ rate = healthy system. Sudden spikes indicate issues.

---

### Panel 3: Error Type Distribution (Pie Chart)

**Visualization Type:** Pie chart

**Query:**
```promql
sum by(error_type) (biopro_dlq_events_total)
```

**Configuration:**
- **Title:** DLQ Events by Error Type
- **Legend:** Show values
- **Colors:**
  - SCHEMA_VALIDATION: Red
  - TIMEOUT: Orange
  - PROCESSING_ERROR: Yellow
  - DESERIALIZATION_ERROR: Purple

**Why This Matters:** Quickly identifies the most common failure types. Schema validation errors should dominate during your invalid event demos.

---

### Panel 4: Circuit Breaker State (Stat)

**Visualization Type:** Stat panel

**Query:**
```promql
biopro_circuit_breaker_state{module="orders"}
```

**Configuration:**
- **Title:** Circuit Breaker State - Orders
- **Value mappings:**
  - 0 → "CLOSED" (Green)
  - 1 → "OPEN" (Red)
  - 2 → "HALF-OPEN" (Yellow)
- **Display:** Large number with color

**Why This Matters:** Shows resilience in action. Should stay green (CLOSED) during normal operation.

---

### Panel 5: Schema Validation Success vs Failure (Graph)

**Visualization Type:** Stacked area chart

**Queries:**
- Success: `sum(rate(biopro_schema_validation_success_total{module="orders"}[1m]))`
- Failure: `sum(rate(biopro_schema_validation_errors_total{module="orders"}[1m]))`

**Configuration:**
- **Title:** Schema Validation - Success vs Failure Rate
- **Y-Axis:** Events/second
- **Stack:** On
- **Colors:**
  - Success: Green
  - Failure: Red

**Why This Matters:** Visual contrast between good and bad events. When you send invalid payloads, red area will spike.

---

### Panel 6: Processing Latency (Graph)

**Visualization Type:** Time series graph

**Queries:**
- P50: `histogram_quantile(0.50, rate(biopro_event_processing_duration_seconds_bucket[5m]))`
- P95: `histogram_quantile(0.95, rate(biopro_event_processing_duration_seconds_bucket[5m]))`
- P99: `histogram_quantile(0.99, rate(biopro_event_processing_duration_seconds_bucket[5m]))`

**Configuration:**
- **Title:** Event Processing Latency (Percentiles)
- **Y-Axis:** Seconds
- **Legend:** Show, Right
- **Colors:**
  - P50: Green
  - P95: Yellow
  - P99: Red

**Why This Matters:** Shows performance characteristics. DLQ routing is fast (<50ms), even under load.

---

### Panel 7: DLQ Events Timeline (Table)

**Visualization Type:** Table

**Query:**
```promql
biopro_dlq_events_total
```

**Configuration:**
- **Title:** DLQ Event Counts by Module and Error Type
- **Columns:** Module, Error Type, Count
- **Sort:** By count (descending)

**Why This Matters:** Summary table for quick triage. Shows which modules and error types are most problematic.

---

### Panel 8: Retry Attempts (Counter)

**Visualization Type:** Stat

**Query:**
```promql
sum(biopro_retry_attempts_total{module="orders"})
```

**Configuration:**
- **Title:** Total Retry Attempts - Orders
- **Display:** Large number
- **Color:** Blue

**Why This Matters:** Shows how often the retry logic is engaged. Higher numbers indicate transient failures being handled.

---

## Creating the Dashboard

### Method 1: Import JSON (Fastest)

1. In Grafana, click **+** → **Import**
2. Paste the JSON below (see [Complete Dashboard JSON](#complete-dashboard-json))
3. Select **Prometheus** as data source
4. Click **Import**

### Method 2: Manual Creation

1. **Create New Dashboard:**
   - Click **+** → **Dashboard**
   - Click **Add new panel**

2. **For Each Panel:**
   - Select visualization type
   - Enter query from sections above
   - Configure display options
   - Set title and legend
   - Click **Apply**

3. **Arrange Panels:**
   - Drag panels to desired layout
   - Resize as needed
   - Typical layout:
     ```
     [Event Throughput - Full Width]
     [DLQ Rate] [Circuit Breaker] [Retry Attempts]
     [Success vs Failure - Half Width] [Error Distribution - Half Width]
     [Latency Graph - Full Width]
     [DLQ Events Table - Full Width]
     ```

4. **Save Dashboard:**
   - Click **Save** icon (top right)
   - Name: "BioPro Event Governance - DLQ Monitoring"
   - Click **Save**

---

## Complete Dashboard JSON

```json
{
  "dashboard": {
    "title": "BioPro Event Governance - DLQ Monitoring",
    "panels": [
      {
        "id": 1,
        "type": "graph",
        "title": "Event Throughput by Module",
        "targets": [
          {
            "expr": "sum(rate(biopro_schema_validation_success_total[1m])) by (module)",
            "legendFormat": "{{module}}"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "type": "gauge",
        "title": "Orders DLQ Rate",
        "targets": [
          {
            "expr": "100 * (sum(rate(biopro_dlq_events_total{module=\"orders\"}[5m])) / (sum(rate(biopro_schema_validation_success_total{module=\"orders\"}[5m])) + sum(rate(biopro_dlq_events_total{module=\"orders\"}[5m]))))"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 5, "color": "yellow"},
                {"value": 15, "color": "red"}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 8, "x": 0, "y": 8}
      },
      {
        "id": 3,
        "type": "stat",
        "title": "Circuit Breaker State",
        "targets": [
          {
            "expr": "biopro_circuit_breaker_state{module=\"orders\"}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [
              {"value": 0, "text": "CLOSED", "color": "green"},
              {"value": 1, "text": "OPEN", "color": "red"},
              {"value": 2, "text": "HALF-OPEN", "color": "yellow"}
            ]
          }
        },
        "gridPos": {"h": 8, "w": 8, "x": 8, "y": 8}
      },
      {
        "id": 4,
        "type": "stat",
        "title": "Total Retry Attempts",
        "targets": [
          {
            "expr": "sum(biopro_retry_attempts_total{module=\"orders\"})"
          }
        ],
        "gridPos": {"h": 8, "w": 8, "x": 16, "y": 8}
      },
      {
        "id": 5,
        "type": "graph",
        "title": "Schema Validation - Success vs Failure",
        "targets": [
          {
            "expr": "sum(rate(biopro_schema_validation_success_total{module=\"orders\"}[1m]))",
            "legendFormat": "Success"
          },
          {
            "expr": "sum(rate(biopro_schema_validation_errors_total{module=\"orders\"}[1m]))",
            "legendFormat": "Failure"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "custom": {
              "fillOpacity": 30,
              "stacking": {"mode": "normal"}
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
      },
      {
        "id": 6,
        "type": "piechart",
        "title": "DLQ Events by Error Type",
        "targets": [
          {
            "expr": "sum by(error_type) (biopro_dlq_events_total)"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
      },
      {
        "id": 7,
        "type": "graph",
        "title": "Event Processing Latency (Percentiles)",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(biopro_event_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(biopro_event_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(biopro_event_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s"
          }
        },
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 24}
      },
      {
        "id": 8,
        "type": "table",
        "title": "DLQ Event Summary",
        "targets": [
          {
            "expr": "biopro_dlq_events_total",
            "format": "table"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 32}
      }
    ],
    "refresh": "5s",
    "time": {
      "from": "now-15m",
      "to": "now"
    }
  }
}
```

**To Import:**
1. Copy the JSON above
2. Grafana → **+** → **Import**
3. Paste JSON
4. Select Prometheus data source
5. Click **Import**

---

## Demo Scenario

### Pre-Demo Setup (5 minutes before)

1. **Start Services:**
   ```bash
   cd <project-root>/event-governance/poc
   ./start-all.sh
   ```

2. **Open Grafana:**
   ```
   http://localhost:3000
   ```

3. **Load Dashboard:**
   - Import the JSON dashboard (if not already)
   - Set time range to **Last 15 minutes**
   - Enable **Auto-refresh: 5s**

4. **Verify Baseline:**
   - All panels should show minimal/zero activity
   - Circuit breaker should be CLOSED (green)
   - DLQ rate should be 0%

---

### Demo Flow (15 minutes)

#### Part 1: Normal Operation (2 minutes)

**Action:** Send a few valid events manually
```bash
# Send 5 valid events
for i in {1..5}; do
  docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
    -H "Content-Type: application/json" \
    -d "{\"orderId\":\"ORD-DEMO-$i\",\"bloodType\":\"O_NEGATIVE\",\"quantity\":$i,\"priority\":\"ROUTINE\",\"facilityId\":\"FAC-001\",\"requestedBy\":\"DR-DEMO\"}"
  sleep 1
done
```

**What to Show:**
- Event Throughput panel shows small spikes
- Schema Validation shows all green (success)
- DLQ Rate stays at 0%
- Latency remains low (<50ms)

**Talking Point:** "This is normal operation - all events pass validation and are published successfully."

---

#### Part 2: Mixed Load with Errors (5 minutes)

**Action:** Run the load generation script
```bash
python generate_demo_orders.py --count 100 --invalid-rate 30
```

**What to Show:**
1. **Event Throughput** - Sharp spike to ~20-30 events/second
2. **DLQ Rate Gauge** - Rises to ~30% (yellow zone)
3. **Success vs Failure Graph** - Red area appears, showing validation failures
4. **Error Distribution Pie Chart** - SCHEMA_VALIDATION dominates
5. **Latency Graph** - Stays low, showing DLQ is fast
6. **Circuit Breaker** - Stays CLOSED (green) - resilience working

**Talking Points:**
- "Notice the DLQ rate jumped to 30% - that's our intentionally invalid events"
- "The system handles 100 events in ~3-5 seconds, even with failures"
- "Error distribution shows schema validation is the primary failure type"
- "Circuit breaker stays closed - the framework handles failures gracefully"
- "Latency remains low - DLQ routing doesn't slow down the system"

---

#### Part 3: Error Type Breakdown (3 minutes)

**Action:** Point to specific panels

**Error Distribution Panel:**
- SCHEMA_VALIDATION: ~30 events (missing fields, type mismatches)
- PROCESSING_ERROR: ~5 events (simulated processing failures)
- Total DLQ: ~35 events out of 100

**DLQ Events Table:**
- Show breakdown by module and error type
- Orders module has highest count
- SCHEMA_VALIDATION is most common

**Talking Point:** "The framework categorizes errors automatically. Schema validation errors are prioritized as HIGH because they usually indicate integration issues."

---

#### Part 4: Zoom In on Details (2 minutes)

**Action:** Adjust time range to "Last 5 minutes"

**Show:**
- Precise timing of the load burst
- Recovery to normal after script completes
- No lingering errors or degraded performance

**Talking Point:** "The system recovered immediately after the load test. No cascading failures, no performance degradation."

---

#### Part 5: Show Historical Context (3 minutes)

**Action:** Expand time range to "Last 1 hour"

**Show:**
- Baseline before demo (flat lines)
- The spike from the load test
- Return to baseline

**Talking Point:** "This is what operators see - anomalies stand out clearly. You can set alerts for when DLQ rate exceeds 10% for more than 5 minutes."

---

### Post-Demo Discussion

**Key Metrics to Highlight:**

1. **DLQ Rate (30%)** - "In production, this would trigger an alert. It's intentionally high for demo purposes."

2. **Processing Latency (<50ms)** - "Even with 30% failures, the system remains fast. DLQ routing doesn't create backpressure."

3. **Error Distribution** - "Schema validation errors are the most common, which aligns with integration bugs being more frequent than infrastructure failures."

4. **Circuit Breaker State (CLOSED)** - "The circuit breaker didn't trip because failures were distributed. If 50% of consecutive calls failed, it would open to prevent cascade."

5. **Total Events (100 in ~5 seconds)** - "This is a small demo load. The framework handles thousands of events per second in production."

---

## Troubleshooting

### No Data Showing in Panels

**Problem:** Grafana shows "No data"

**Solutions:**
1. Check Prometheus data source: Configuration → Data Sources → Prometheus → Test
2. Verify metrics are being scraped: http://localhost:9090/targets (all should be UP)
3. Check if services are running: `docker ps`
4. Verify metrics endpoint: `curl http://localhost:8080/actuator/prometheus`

---

### Metrics Not Updating

**Problem:** Dashboard shows stale data

**Solutions:**
1. Check refresh rate: Dashboard settings → Auto-refresh → Set to 5s
2. Verify time range: Top right → Select "Last 15 minutes"
3. Force refresh: Click refresh icon (top right)

---

### Circuit Breaker Always Shows 0

**Problem:** Circuit breaker metric not visible

**Solutions:**
1. This metric only appears when the circuit breaker module is active
2. Check if DLQ processor is initialized: `docker logs biopro-orders-service | grep "BioPro Event Governance"`
3. Ensure circuit breaker is enabled in config: `biopro.dlq.circuit-breaker.enabled=true`

---

### Queries Return No Results

**Problem:** Prometheus queries return empty results

**Solutions:**
1. Check metric names: http://localhost:9090/api/v1/label/__name__/values
2. Verify labels: http://localhost:9090/api/v1/series?match[]={__name__=~"biopro.*"}
3. Adjust time range: Metrics might be outside current time window

---

## Advanced Queries

### DLQ Rate Trend (Last Hour)
```promql
avg_over_time(
  (
    rate(biopro_dlq_events_total{module="orders"}[5m])
    /
    (rate(biopro_schema_validation_success_total{module="orders"}[5m]) + rate(biopro_dlq_events_total{module="orders"}[5m]))
  )[1h:5m]
)
```

### Events by Hour
```promql
sum(increase(biopro_schema_validation_success_total[1h])) by (module)
```

### Error Rate Spike Detection
```promql
deriv(biopro_dlq_events_total[5m]) > 10
```

### Top Error Types
```promql
topk(5, sum by(error_type) (rate(biopro_dlq_events_total[5m])))
```

---

## Alert Rules (Bonus)

Create alerts for production use:

### High DLQ Rate Alert
```yaml
groups:
  - name: biopro_dlq_alerts
    rules:
      - alert: HighDLQRate
        expr: |
          100 * (
            rate(biopro_dlq_events_total{module="orders"}[5m])
            /
            (rate(biopro_schema_validation_success_total{module="orders"}[5m]) + rate(biopro_dlq_events_total{module="orders"}[5m]))
          ) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High DLQ rate for {{ $labels.module }}"
          description: "DLQ rate is {{ $value }}% for the last 5 minutes"
```

### Circuit Breaker Open Alert
```yaml
      - alert: CircuitBreakerOpen
        expr: biopro_circuit_breaker_state{module="orders"} == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Circuit breaker open for {{ $labels.module }}"
          description: "Circuit breaker has been open for 1 minute - indicating persistent failures"
```

---

## Tips for Maximum Demo Impact

1. **Use Full Screen Mode:** Click the expand icon on key panels during explanation

2. **Use Dashboard Variables:** Create a `$module` variable to switch between modules dynamically

3. **Set Thresholds:** Use color thresholds (green/yellow/red) for visual impact

4. **Add Annotations:** Mark events on timeline (e.g., "Load test started")

5. **Save Dashboard State:** Create multiple dashboard versions for different scenarios

6. **Use Table Transformations:** Sort DLQ events table by most recent first

7. **Enable Panel Links:** Link panels to drill-down dashboards for deeper analysis

8. **Custom Time Ranges:** Use relative time ranges ("Last 5 minutes") for consistent views

9. **Share Snapshots:** Create shareable dashboard snapshots for stakeholders

10. **Record Screen:** Consider recording the dashboard during load test for async demos

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Companion Scripts**: `generate_demo_orders.py`
**Related Docs**: `DEMO-SCRIPT.md`, `DEMO-TECHNICAL-DEEP-DIVE.md`
