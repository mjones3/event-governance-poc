# BioPro Event Governance - Quick Reference

One-page reference for all URLs, ports, and common commands.

---

## 🚀 Start Commands

```bash
# Docker Compose (recommended for local dev)
docker-compose up -d --build

# Kubernetes with Tilt
tilt up
```

---

## 🌐 Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Services** |
| Orders API | http://localhost:8080 | N/A |
| Collections API | http://localhost:8081 | N/A |
| Manufacturing API | http://localhost:8082 | N/A |
| **Infrastructure** |
| Kafka UI | http://localhost:8090 | N/A |
| Schema Registry | http://localhost:8081 | N/A |
| **Monitoring** |
| Prometheus | http://localhost:9090 | N/A |
| Grafana | http://localhost:3000 | Anonymous (no login) |

---

## ✅ Health Checks (Copy/Paste)

```bash
# All services in one command
curl http://localhost:8080/actuator/health && \
curl http://localhost:8081/actuator/health && \
curl http://localhost:8082/actuator/health

# Check metrics are exposed
curl http://localhost:8080/actuator/prometheus | grep biopro
curl http://localhost:8081/actuator/prometheus | grep biopro
curl http://localhost:8082/actuator/prometheus | grep biopro
```

---

## 📊 View Metrics

```bash
# Prometheus targets (should show 3/3 UP)
open http://localhost:9090/targets

# Grafana BioPro dashboard
open http://localhost:3000
# Navigate to: Dashboards → BioPro → BioPro Event Governance - DLQ Metrics

# Kafka UI (view topics and messages)
open http://localhost:8090
```

---

## 🧪 Test Event Publishing

```bash
# Orders Service
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderNumber": 12345, "customerId": "CUST-001", "status": "PENDING"}'

# Collections Service
curl -X POST http://localhost:8081/api/collections \
  -H "Content-Type: application/json" \
  -d '{"unitNumber": "UNIT-001", "donationType": "ALLOGENEIC", "status": "RECEIVED"}'

# Manufacturing Service
curl -X POST http://localhost:8082/api/manufacturing/products \
  -H "Content-Type: application/json" \
  -d '{"productId": "PROD-001", "productType": "APHERESIS_PLASMA", "status": "CREATED"}'
```

---

## 📦 BioPro Avro Schemas

Real production schemas extracted from BioPro backend services:

### Available Schemas

| Schema | Source | Fields | Location |
|--------|--------|--------|----------|
| **CollectionReceivedEvent** | biopro-interface/collections | 14 fields + nested Volume | `biopro-common-integration/src/main/resources/avro/CollectionReceivedEvent.avsc` |
| **CollectionUpdatedEvent** | biopro-interface/collections | 14 fields + nested Volume | `biopro-common-integration/src/main/resources/avro/CollectionUpdatedEvent.avsc` |
| **OrderCreatedEvent** | biopro-distribution/orders | Envelope pattern (eventId + payload with 23 fields) | `biopro-common-integration/src/main/resources/avro/OrderCreatedEvent.avsc` |
| **ApheresisPlasmaProductCreatedEvent** | biopro-manufacturing | 45+ fields with complex nesting | `biopro-common-integration/src/main/resources/avro/ApheresisPlasmaProductCreatedEvent.avsc` |

### Schema Details

**CollectionReceivedEvent:**
- Blood collection events (ALLOGENEIC or AUTOLOGOUS)
- Volume measurements (PLASMA, RBC, PLATELET, etc.)
- Timezone support for temporal fields

**OrderCreatedEvent:**
- Order processing events with envelope pattern
- Full order details with line items
- UUID-based event tracking

**ApheresisPlasmaProductCreatedEvent:**
- Complex manufacturing events
- Product lifecycle tracking
- Weight, volume, and input product tracking

---

## 🔐 Schema Registration

### Check Registered Schemas

```bash
# List all registered schemas
curl http://localhost:8081/subjects

# Expected output when schemas are registered:
# ["biopro.orders.events-value","biopro.collections.events-value","biopro.manufacturing.events-value"]
```

### Register a Schema Manually

If schemas aren't auto-registered, use this:

**1. Register OrderCreatedEvent:**
```bash
curl -X POST http://localhost:8081/subjects/biopro.orders.events-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @- << 'EOF'
{
  "schema": "{\"type\":\"record\",\"name\":\"OrderCreatedEvent\",\"namespace\":\"com.biopro.events.orders\",\"fields\":[{\"name\":\"eventId\",\"type\":{\"type\":\"string\",\"logicalType\":\"uuid\"}},{\"name\":\"occurredOn\",\"type\":{\"type\":\"long\",\"logicalType\":\"timestamp-millis\"}},{\"name\":\"eventType\",\"type\":\"string\"},{\"name\":\"eventVersion\",\"type\":\"string\"},{\"name\":\"payload\",\"type\":{\"type\":\"record\",\"name\":\"OrderCreatedPayload\",\"fields\":[{\"name\":\"orderNumber\",\"type\":\"long\"},{\"name\":\"customerId\",\"type\":\"string\"},{\"name\":\"status\",\"type\":\"string\"}]}}]}"
}
EOF
```

**2. Register CollectionReceivedEvent:**
```bash
curl -X POST http://localhost:8081/subjects/biopro.collections.events-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @- << 'EOF'
{
  "schema": "{\"type\":\"record\",\"name\":\"CollectionReceivedEvent\",\"namespace\":\"com.biopro.events.collections\",\"fields\":[{\"name\":\"unitNumber\",\"type\":\"string\"},{\"name\":\"donationType\",\"type\":{\"type\":\"enum\",\"name\":\"DonationType\",\"symbols\":[\"ALLOGENEIC\",\"AUTOLOGOUS\"]}},{\"name\":\"status\",\"type\":\"string\"}]}"
}
EOF
```

**3. Register ApheresisPlasmaProductCreatedEvent:**
```bash
curl -X POST http://localhost:8081/subjects/biopro.manufacturing.events-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @- << 'EOF'
{
  "schema": "{\"type\":\"record\",\"name\":\"ApheresisPlasmaProductCreatedEvent\",\"namespace\":\"com.biopro.events.manufacturing\",\"fields\":[{\"name\":\"productId\",\"type\":\"string\"},{\"name\":\"productType\",\"type\":\"string\"},{\"name\":\"status\",\"type\":\"string\"}]}"
}
EOF
```

**Verify registration:**
```bash
curl http://localhost:8081/subjects
# Should now show all three schemas
```

---

## ✅ Test Schema Validation

### Send Valid Event (Should Pass Validation)

```bash
# Valid order event
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderNumber": 12345,
    "customerId": "CUST-001",
    "status": "PENDING"
  }'

# Check logs for validation success
docker-compose logs orders-service | grep "Schema validation"
# Expected: "Schema validation succeeded" or similar
```

### Send Invalid Event (Should Fail Validation → Go to DLQ)

```bash
# Invalid event - missing required fields
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "invalidField": "bad data"
  }'

# Check logs for validation failure
docker-compose logs orders-service | grep "validation failed"
# Expected: "Schema validation failed" message
```

### Verify Validation in Service Logs

```bash
# Watch logs in real-time
docker-compose logs -f orders-service

# Look for these messages:
# ✅ Valid:   "Schema validation succeeded"
# ❌ Invalid: "Schema validation failed: [error details]"
# ❌ Invalid: "Routing event to DLQ"
```

---

## 📊 View Validation Metrics in Prometheus

### Access Prometheus

Open: http://localhost:9090/graph

### Key Queries for Schema Validation

**1. Total Schema Validations (Success + Failure):**
```promql
biopro_schema_validation_total
```

**2. Schema Validation Success Count:**
```promql
biopro_schema_validation_total{result="success"}
```

**3. Schema Validation Failure Count:**
```promql
biopro_schema_validation_total{result="failure"}
```

**4. Schema Validation Success Rate (%):**
```promql
(rate(biopro_schema_validation_total{result="success"}[5m]) /
rate(biopro_schema_validation_total[5m])) * 100
```

**5. Validation by Module:**
```promql
sum by (module, result) (rate(biopro_schema_validation_total[5m]))
```

**6. DLQ Events (Failed Validations):**
```promql
rate(biopro_dlq_events_total{errorType="SCHEMA_VALIDATION"}[5m])
```

**7. Validation Failures Over Time:**
```promql
increase(biopro_schema_validation_total{result="failure"}[1h])
```

### Quick Test in Prometheus

1. Send a valid event (see above)
2. Wait 15 seconds (Prometheus scrape interval)
3. Run query: `biopro_schema_validation_total{result="success"}`
4. Should see counter increase by 1

---

## 📈 View Validation Metrics in Grafana

### Access Grafana Dashboard

Open: http://localhost:3000 (anonymous login, no credentials needed)

Navigate to: **Dashboards → BioPro → BioPro Event Governance - DLQ Metrics**

### Pre-Built Panels

The dashboard includes these validation-related panels:

**1. Schema Validation Success Rate**
- Shows percentage of successful validations
- Query: `rate(biopro_schema_validation{result="success"}[5m]) / rate(biopro_schema_validation[5m]) * 100`
- Green = Good (>95%), Yellow = Warning (<95%), Red = Critical (<90%)

**2. DLQ Events Total (by Module)**
- Shows events routed to DLQ (including schema validation failures)
- Broken down by module (orders, collections, manufacturing)
- Query: `rate(biopro_dlq_events_total[5m])`

**3. Schema Validation by Result**
- Bar chart showing success vs failure counts
- Query: `sum by (result) (biopro_schema_validation_total)`

### Create Custom Panel for Validation

Click **"Add panel"** and use these queries:

**Validation Failures by Event Type:**
```promql
sum by (module, eventType) (
  rate(biopro_schema_validation_total{result="failure"}[5m])
)
```

**Recent Validation Errors (last 1 hour):**
```promql
increase(biopro_schema_validation_total{result="failure"}[1h])
```

### Real-Time Validation Testing

1. Set Grafana refresh to **5 seconds** (top right dropdown)
2. Send test events (valid and invalid)
3. Watch panels update in real-time:
   - Success rate should change
   - DLQ events should increase for failures
   - Validation counters should increment

### Validation Alert Example

Create an alert for high validation failure rate:

```
Alert: High Schema Validation Failures
Query: rate(biopro_schema_validation_total{result="failure"}[5m])
Threshold: > 1 (more than 1 failure per second)
Duration: 5 minutes
```

---

## 🧪 Complete Validation Test Workflow

### Step-by-Step Test

```bash
# 1. Check current validation metrics (baseline)
curl http://localhost:8080/actuator/prometheus | grep biopro_schema_validation

# 2. Send a VALID event
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderNumber": 12345, "customerId": "CUST-001", "status": "PENDING"}'

# 3. Check logs immediately
docker-compose logs orders-service | tail -20
# Look for: "Schema validation succeeded" or "Successfully published"

# 4. Wait 15 seconds for Prometheus scrape

# 5. Check Prometheus metrics again
curl http://localhost:8080/actuator/prometheus | grep biopro_schema_validation
# Should see success counter increased

# 6. Send an INVALID event
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"badField": "invalid"}'

# 7. Check logs for failure
docker-compose logs orders-service | tail -20
# Look for: "Schema validation failed" and "Routing event to DLQ"

# 8. Check Prometheus after 15 seconds
curl http://localhost:8080/actuator/prometheus | grep biopro_schema_validation
# Should see failure counter increased

# 9. View in Grafana
open http://localhost:3000
# Navigate to BioPro dashboard and see metrics update
```

### Expected Results

After sending 1 valid and 1 invalid event:

**In Prometheus:**
```
biopro_schema_validation_total{module="orders",result="success"} 1
biopro_schema_validation_total{module="orders",result="failure"} 1
biopro_dlq_events_total{module="orders",errorType="SCHEMA_VALIDATION"} 1
```

**In Grafana:**
- Schema Validation Success Rate: ~50% (1 success, 1 failure)
- DLQ Events: 1 event
- Recent activity graph shows spike

**In Kafka UI (http://localhost:8090):**
- Valid event appears in `biopro.orders.events` topic
- Invalid event appears in `biopro.dlq` topic

---

## 🔍 View Logs

### Docker Compose
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f orders-service
docker-compose logs -f collections-service
docker-compose logs -f manufacturing-service

# Infrastructure
docker-compose logs -f kafka
docker-compose logs -f prometheus
```

### Kubernetes
```bash
# All logs
kubectl logs -f -n biopro-dlq deployment/orders-service
kubectl logs -f -n biopro-dlq deployment/collections-service
kubectl logs -f -n biopro-dlq deployment/manufacturing-service

# Infrastructure
kubectl logs -f -n biopro-kafka deployment/kafka
kubectl logs -f -n biopro-kafka deployment/prometheus
```

---

## 🛑 Stop/Clean Up

### Docker Compose
```bash
# Stop (keep data)
docker-compose down

# Stop and remove all data
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build
```

### Kubernetes
```bash
# Stop Tilt
tilt down

# Clean up Kubernetes resources
kubectl delete namespace biopro-dlq
kubectl delete namespace biopro-kafka
```

---

## 📈 Useful Prometheus Queries

Open http://localhost:9090/graph and try:

```promql
# All BioPro metrics
{__name__=~"biopro.*"}

# DLQ event rate (events/second)
rate(biopro_dlq_events_total[5m])

# Schema validation success rate (%)
rate(biopro_schema_validation_total{result="success"}[5m]) /
rate(biopro_schema_validation_total[5m]) * 100

# P95 event processing duration
histogram_quantile(0.95, rate(biopro_event_processing_duration_seconds_bucket[5m]))

# Circuit breaker state (0=CLOSED, 1=OPEN)
biopro_circuit_breaker_state

# Events by module
sum by (module) (rate(biopro_dlq_events_total[5m]))
```

---

## 🎯 Kafka Commands

### Docker Compose
```bash
# List topics
docker exec -it biopro-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Consume messages from orders topic
docker exec -it biopro-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic biopro.orders.events \
  --from-beginning

# View DLQ topic
docker exec -it biopro-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic biopro.dlq \
  --from-beginning
```

### Kubernetes
```bash
# List topics
kubectl exec -it -n biopro-kafka deployment/kafka -- \
  kafka-topics --bootstrap-server localhost:9092 --list

# Consume messages
kubectl exec -it -n biopro-kafka deployment/kafka -- \
  kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic biopro.orders.events --from-beginning
```

---

## 📋 Schema Registry Commands

```bash
# List all registered schemas
curl http://localhost:8081/subjects

# Get latest version of orders schema
curl http://localhost:8081/subjects/biopro.orders.events-value/versions/latest

# Get all versions
curl http://localhost:8081/subjects/biopro.orders.events-value/versions

# Check schema compatibility
curl -X POST http://localhost:8081/compatibility/subjects/biopro.orders.events-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "..."}'
```

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check container status
docker-compose ps  # or kubectl get pods -n biopro-dlq

# Check logs for errors
docker-compose logs orders-service | grep -i error
```

### Prometheus not showing targets
```bash
# Verify Prometheus config
docker exec -it biopro-prometheus cat /etc/prometheus/prometheus.yml

# Test connectivity from Prometheus to service
docker exec -it biopro-prometheus wget -qO- http://orders-service:8080/actuator/prometheus
```

### Metrics not appearing
```bash
# Verify metrics endpoint is exposed
curl http://localhost:8080/actuator/prometheus | head -20

# Check if Prometheus is scraping
open http://localhost:9090/targets
```

### Kafka connection issues
```bash
# Test Kafka from service container
docker exec -it biopro-orders-service \
  nc -zv kafka 29092  # Should show "open"

# Check Kafka broker
docker exec -it biopro-kafka kafka-broker-api-versions \
  --bootstrap-server localhost:9092
```

---

## 📁 Project Structure

```
poc/
├── docker-compose.yml              # Complete stack (Docker Compose)
├── Tiltfile                        # K8s deployment config
├── prometheus.yml                  # Prometheus scrape config
├── grafana/provisioning/           # Grafana auto-config
│
├── biopro-demo-orders/             # Orders service
├── biopro-demo-collections/        # Collections service
├── biopro-demo-manufacturing/      # Manufacturing service
│
├── biopro-common-core/             # Core utilities
├── biopro-common-config/           # Auto-configuration
├── biopro-common-integration/      # Kafka + Avro schemas
├── biopro-common-monitoring/       # Metrics (Prometheus/Dynatrace)
├── biopro-dlq-spring-boot-starter/ # Aggregating starter
│
└── k8s/                            # Kubernetes manifests
    ├── common/                     # Kafka, Prometheus, Grafana
    ├── orders/
    ├── collections/
    └── manufacturing/
```

---

## 🎓 Full Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview and architecture |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Complete testing procedures |
| [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md) | Docker Compose deployment |
| [K8S_DEPLOYMENT_GUIDE.md](K8S_DEPLOYMENT_GUIDE.md) | Kubernetes deployment |
| [MONITORING_GUIDE.md](MONITORING_GUIDE.md) | Prometheus & Grafana setup |
| [SCHEMA_REGISTRATION_GUIDE.md](SCHEMA_REGISTRATION_GUIDE.md) | Schema Registry usage |
| [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md) | Integration summary |

---

## ⚡ Most Common Commands

```bash
# Start everything
docker-compose up -d --build

# Check everything is running
docker-compose ps
curl http://localhost:8080/actuator/health

# View logs
docker-compose logs -f orders-service

# Test event publishing
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderNumber": 999, "customerId": "TEST", "status": "PENDING"}'

# View in Grafana
open http://localhost:3000

# Stop everything
docker-compose down
```

---

**Keep this reference handy for daily development!** 🚀

**Last Updated**: November 5, 2025
