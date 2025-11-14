# BioPro Event Governance - Testing Guide

Complete guide for testing the BioPro Event Governance Framework in both Docker Compose and Kubernetes environments.

---

## 📍 Deployment Overview

### Docker Compose Deployment

```
C:\Users\MelvinJones\work\event-governance\poc
├── docker-compose.yml          # Complete stack definition
├── prometheus.yml              # Prometheus scrape config
└── grafana/provisioning/       # Grafana auto-config
```

**Start command:**
```bash
docker-compose up -d --build
```

### Kubernetes Deployment

```
C:\Users\MelvinJones\work\event-governance\poc
├── Tiltfile                    # Tilt configuration
└── k8s/                        # Kubernetes manifests
    ├── common/                 # Infrastructure
    ├── orders/                 # Orders service
    ├── collections/            # Collections service
    └── manufacturing/          # Manufacturing service
```

**Start command:**
```bash
tilt up
```

---

## 🌐 URLs and Ports

### Both Environments (Same Ports)

| Component | Port | URL | Purpose |
|-----------|------|-----|---------|
| **BioPro Services** |
| Orders Service | 8080 | http://localhost:8080 | Main order processing service |
| Collections Service | 8081 | http://localhost:8081 | Blood collection tracking |
| Manufacturing Service | 8082 | http://localhost:8082 | Plasma product manufacturing |
| **Infrastructure** |
| Kafka | 9092 | localhost:9092 | Kafka broker |
| Zookeeper | 2181 | localhost:2181 | Zookeeper coordination |
| Schema Registry | 8081 | http://localhost:8081 | Avro schema management |
| Kafka UI | 8090 | http://localhost:8090 | Web UI for Kafka |
| **Monitoring** |
| Prometheus | 9090 | http://localhost:9090 | Metrics database |
| Grafana | 3000 | http://localhost:3000 | Dashboards and visualization |

---

## ✅ Step-by-Step Testing

### 1. Start the Stack

**Docker Compose:**
```bash
cd C:\Users\MelvinJones\work\event-governance\poc
docker-compose up -d --build

# Wait for services to start (2-3 minutes)
docker-compose ps
```

**Kubernetes:**
```bash
cd C:\Users\MelvinJones\work\event-governance\poc
tilt up

# Watch the Tilt UI at http://localhost:10350
```

---

### 2. Verify Infrastructure

#### Check Zookeeper
```bash
# Docker Compose
docker exec -it biopro-zookeeper zkServer.sh status

# Kubernetes
kubectl exec -it -n biopro-kafka deployment/zookeeper -- zkServer.sh status
```

**Expected output:** `Mode: standalone`

#### Check Kafka
```bash
# Docker Compose
docker exec -it biopro-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Kubernetes
kubectl exec -it -n biopro-kafka deployment/kafka -- kafka-topics --bootstrap-server localhost:9092 --list
```

**Expected output:** List of topics (may be empty initially)

#### Check Schema Registry
```bash
curl http://localhost:8081/subjects
```

**Expected output:** `[]` (empty array - no schemas registered yet)

#### Check Kafka UI
```bash
# Open browser
start http://localhost:8090
```

**Expected:** Web UI showing Kafka cluster "biopro-local"

---

### 3. Verify BioPro Services

#### Health Checks

**Orders Service:**
```bash
curl http://localhost:8080/actuator/health
```

**Collections Service:**
```bash
curl http://localhost:8081/actuator/health
```

**Manufacturing Service:**
```bash
curl http://localhost:8082/actuator/health
```

**Expected output (all services):**
```json
{
  "status": "UP"
}
```

#### Actuator Info

```bash
curl http://localhost:8080/actuator/info
curl http://localhost:8081/actuator/info
curl http://localhost:8082/actuator/info
```

---

### 4. Verify Prometheus Metrics

#### Check Metrics Endpoints

**Orders Service:**
```bash
curl http://localhost:8080/actuator/prometheus | grep biopro
```

**Collections Service:**
```bash
curl http://localhost:8081/actuator/prometheus | grep biopro
```

**Manufacturing Service:**
```bash
curl http://localhost:8082/actuator/prometheus | grep biopro
```

**Expected output:** BioPro custom metrics like:
```
biopro_dlq_events_total{...} 0.0
biopro_schema_validation_total{...} 0.0
biopro_event_processing_duration_seconds_count{...} 0.0
```

#### Check Prometheus Targets

```bash
# Open Prometheus
start http://localhost:9090/targets
```

**Expected:** All 3 targets showing as **UP**:
- `biopro-orders (1/1 up)`
- `biopro-collections (1/1 up)`
- `biopro-manufacturing (1/1 up)`

#### Query Metrics in Prometheus

1. Open http://localhost:9090
2. Go to **Graph** tab
3. Try these queries:

```promql
# All BioPro metrics
{__name__=~"biopro.*"}

# DLQ event rate
rate(biopro_dlq_events_total[5m])

# Schema validation
biopro_schema_validation_total

# Processing duration
biopro_event_processing_duration_seconds_count
```

---

### 5. Verify Grafana Dashboards

#### Access Grafana

```bash
start http://localhost:3000
```

**No login required** (anonymous access enabled)

#### View Pre-loaded Dashboard

1. Click **Dashboards** (left sidebar)
2. Navigate to **BioPro** folder
3. Click **BioPro Event Governance - DLQ Metrics**

**Expected panels:**
- DLQ Events Total (by Module)
- Schema Validation Success Rate
- Event Processing Duration (p95)
- Reprocessing Success vs Failure
- Circuit Breaker State
- Retry Attempts

*Note: Panels may be empty initially if no events have been processed yet*

#### Test Prometheus Datasource

1. Go to **Configuration** → **Data sources**
2. Click **Prometheus**
3. Scroll down and click **Save & Test**

**Expected:** ✅ "Data source is working"

---

### 6. Test Event Processing

#### Publish Test Events

**Orders Service - Create Order Event:**
```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderNumber": 12345,
    "customerId": "CUST-001",
    "status": "PENDING"
  }'
```

**Collections Service - Collection Event:**
```bash
curl -X POST http://localhost:8081/api/collections \
  -H "Content-Type: application/json" \
  -d '{
    "unitNumber": "UNIT-12345",
    "donationType": "ALLOGENEIC",
    "status": "RECEIVED"
  }'
```

**Manufacturing Service - Product Event:**
```bash
curl -X POST http://localhost:8082/api/manufacturing/products \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "PROD-12345",
    "productType": "APHERESIS_PLASMA",
    "status": "CREATED"
  }'
```

**Expected response (all):** `200 OK` with event confirmation

---

### 7. Verify Events in Kafka

#### Using Kafka UI

1. Open http://localhost:8090
2. Click on **Topics**
3. Look for BioPro topics:
   - `biopro.orders.events`
   - `biopro.collections.events`
   - `biopro.manufacturing.events`
4. Click on a topic → **Messages** to view events

#### Using Kafka CLI

**List topics:**
```bash
# Docker Compose
docker exec -it biopro-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Kubernetes
kubectl exec -it -n biopro-kafka deployment/kafka -- kafka-topics --bootstrap-server localhost:9092 --list
```

**Consume messages:**
```bash
# Docker Compose - Orders topic
docker exec -it biopro-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic biopro.orders.events \
  --from-beginning

# Kubernetes - Orders topic
kubectl exec -it -n biopro-kafka deployment/kafka -- kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic biopro.orders.events \
  --from-beginning
```

---

### 8. Verify Schema Registration

#### List Registered Schemas

```bash
curl http://localhost:8081/subjects
```

**Expected output (after events published):**
```json
[
  "biopro.orders.events-value",
  "biopro.collections.events-value",
  "biopro.manufacturing.events-value"
]
```

#### Get Specific Schema

```bash
# Orders schema
curl http://localhost:8081/subjects/biopro.orders.events-value/versions/latest

# Collections schema
curl http://localhost:8081/subjects/biopro.collections.events-value/versions/latest

# Manufacturing schema
curl http://localhost:8081/subjects/biopro.manufacturing.events-value/versions/latest
```

**Expected:** Full Avro schema definition in JSON format

---

### 9. Test DLQ Functionality

#### Trigger Schema Validation Failure

**Send invalid event (missing required fields):**
```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "invalidField": "bad data"
  }'
```

**Expected:** Event routed to DLQ

#### Check DLQ Topic

```bash
# Using Kafka UI
# 1. Open http://localhost:8090
# 2. Navigate to Topics → biopro.dlq

# Using CLI (Docker Compose)
docker exec -it biopro-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic biopro.dlq \
  --from-beginning

# Using CLI (Kubernetes)
kubectl exec -it -n biopro-kafka deployment/kafka -- kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic biopro.dlq \
  --from-beginning
```

#### Verify DLQ Metrics

```bash
# Check DLQ counter increased
curl http://localhost:8080/actuator/prometheus | grep biopro_dlq_events_total
```

**Expected:** Counter > 0

---

### 10. Monitor Metrics in Real-Time

#### Watch Prometheus Metrics

Open http://localhost:9090/graph and query:

```promql
# DLQ event rate (events per second)
rate(biopro_dlq_events_total[1m])

# Schema validation by result
sum by (result) (biopro_schema_validation_total)

# Event processing duration (average)
rate(biopro_event_processing_duration_seconds_sum[5m]) /
rate(biopro_event_processing_duration_seconds_count[5m])
```

#### Watch Grafana Dashboard

1. Open http://localhost:3000
2. Navigate to BioPro DLQ dashboard
3. Set refresh interval: **5s** (top right)
4. Publish events and watch panels update in real-time

---

## 🔍 Troubleshooting Tests

### Services Not Responding

**Check service logs:**

**Docker Compose:**
```bash
docker-compose logs orders-service
docker-compose logs collections-service
docker-compose logs manufacturing-service
```

**Kubernetes:**
```bash
kubectl logs -f deployment/orders-service -n biopro-dlq
kubectl logs -f deployment/collections-service -n biopro-dlq
kubectl logs -f deployment/manufacturing-service -n biopro-dlq
```

### Prometheus Not Scraping

**Check Prometheus logs:**

**Docker Compose:**
```bash
docker-compose logs prometheus
```

**Kubernetes:**
```bash
kubectl logs -f deployment/prometheus -n biopro-kafka
```

**Verify targets are reachable:**
```bash
# Test from Prometheus container (Docker Compose)
docker exec -it biopro-prometheus wget -qO- http://orders-service:8080/actuator/prometheus

# Test from Prometheus pod (Kubernetes)
kubectl exec -it -n biopro-kafka deployment/prometheus -- wget -qO- http://orders-service.biopro-dlq.svc.cluster.local:8080/actuator/prometheus
```

### Schema Registry Issues

**Check connectivity:**
```bash
# From service container (Docker Compose)
docker exec -it biopro-orders-service wget -qO- http://schema-registry:8081/subjects

# From service pod (Kubernetes)
kubectl exec -it -n biopro-dlq deployment/orders-service -- wget -qO- http://schema-registry.biopro-kafka.svc.cluster.local:8081/subjects
```

---

## 📊 Test Scenarios

### Scenario 1: Happy Path - Valid Event Flow

**Steps:**
1. Publish valid order event
2. Verify event appears in Kafka topic
3. Verify schema was validated successfully
4. Check metrics show successful processing
5. Confirm no DLQ events

**Commands:**
```bash
# 1. Publish event
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderNumber": 12345, "customerId": "CUST-001", "status": "PENDING"}'

# 2. Check Kafka topic (Kafka UI)
open http://localhost:8090

# 3. Check schema validation metric
curl http://localhost:8080/actuator/prometheus | grep 'biopro_schema_validation.*success'

# 4. Check processing metrics
curl http://localhost:8080/actuator/prometheus | grep biopro_event_processing_duration_seconds_count

# 5. Verify no DLQ events
curl http://localhost:8080/actuator/prometheus | grep biopro_dlq_events_total
```

**Expected:** All metrics increment, no errors

---

### Scenario 2: Schema Validation Failure

**Steps:**
1. Publish invalid event (bad schema)
2. Verify event routed to DLQ
3. Check DLQ metrics incremented
4. View DLQ event details in Kafka UI
5. Verify error categorization

**Commands:**
```bash
# 1. Publish invalid event
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"invalidField": 123}'

# 2. Check DLQ topic
open http://localhost:8090  # Navigate to biopro.dlq topic

# 3. Check DLQ metrics
curl http://localhost:8080/actuator/prometheus | grep biopro_dlq_events_total

# 4. Check schema validation failures
curl http://localhost:8080/actuator/prometheus | grep 'biopro_schema_validation.*failure'
```

**Expected:** DLQ counter increases, validation failure recorded

---

### Scenario 3: High Load Testing

**Steps:**
1. Publish 100 events rapidly
2. Monitor processing duration (p95, p99)
3. Check for circuit breaker activation
4. Verify all events processed
5. Check Grafana for latency spikes

**Commands:**
```bash
# Publish 100 events
for i in {1..100}; do
  curl -X POST http://localhost:8080/api/orders \
    -H "Content-Type: application/json" \
    -d "{\"orderNumber\": $i, \"customerId\": \"CUST-$i\", \"status\": \"PENDING\"}" &
done
wait

# Check processing duration
curl http://localhost:8080/actuator/prometheus | grep biopro_event_processing_duration_seconds

# Check circuit breaker state
curl http://localhost:8080/actuator/prometheus | grep biopro_circuit_breaker_state

# View in Grafana
open http://localhost:3000  # Check p95 latency panel
```

---

### Scenario 4: DLQ Reprocessing

**Steps:**
1. Create DLQ event (schema validation failure)
2. View DLQ events via API
3. Trigger reprocessing
4. Verify reprocessing success/failure metrics
5. Check event removed from DLQ

**Commands:**
```bash
# 1. Create DLQ event
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"bad": "data"}'

# 2. View DLQ events (if API available)
curl http://localhost:8080/api/dlq/events

# 3. Trigger reprocessing (if API available)
curl -X POST http://localhost:8080/api/dlq/reprocess

# 4. Check reprocessing metrics
curl http://localhost:8080/actuator/prometheus | grep biopro_dlq_reprocessing
```

---

## 🎯 Quick Validation Checklist

Use this checklist to verify complete deployment:

### Infrastructure ✅
- [ ] Zookeeper running and healthy
- [ ] Kafka running and healthy
- [ ] Schema Registry accessible at http://localhost:8081
- [ ] Kafka UI accessible at http://localhost:8090

### Services ✅
- [ ] Orders service health check passes (http://localhost:8080/actuator/health)
- [ ] Collections service health check passes (http://localhost:8081/actuator/health)
- [ ] Manufacturing service health check passes (http://localhost:8082/actuator/health)

### Monitoring ✅
- [ ] Prometheus accessible at http://localhost:9090
- [ ] Prometheus showing 3/3 targets UP
- [ ] Grafana accessible at http://localhost:3000
- [ ] BioPro dashboard visible in Grafana
- [ ] All services exposing `biopro.*` metrics

### Event Processing ✅
- [ ] Can publish events to all services
- [ ] Events appear in Kafka topics
- [ ] Schemas auto-registered in Schema Registry
- [ ] Invalid events routed to DLQ
- [ ] DLQ metrics incrementing correctly

### End-to-End ✅
- [ ] Publish event → See in Kafka → See metrics in Prometheus → See in Grafana dashboard
- [ ] Schema validation working (valid events pass, invalid events go to DLQ)
- [ ] All custom BioPro metrics appearing in Prometheus

---

## 📚 Additional Resources

- **Docker Compose Guide**: [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md)
- **Kubernetes Guide**: [K8S_DEPLOYMENT_GUIDE.md](K8S_DEPLOYMENT_GUIDE.md)
- **Monitoring Guide**: [MONITORING_GUIDE.md](MONITORING_GUIDE.md)
- **Schema Registration**: [SCHEMA_REGISTRATION_GUIDE.md](SCHEMA_REGISTRATION_GUIDE.md)
- **Main README**: [README.md](README.md)

---

**Document Version**: 1.0
**Last Updated**: November 4, 2025
**Author**: Event Governance Team
