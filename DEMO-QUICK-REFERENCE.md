# BioPro Event Governance Demo - Quick Reference

**Copy-Paste Commands for Live Demo**

## Environment Setup

### Start Everything
```bash
cd /c/Users/MelvinJones/work/event-governance/poc
./start-all.sh
```

### Verify Services
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Open Monitoring
```bash
# Terminal 2: kcat UI
./kafka-ui.sh
# Select [4] - Monitor DLQ in Real-Time
```

---

## Schema Commands

### View OrderCreatedEvent Schema
```bash
curl http://localhost:8081/subjects/OrderCreatedEvent/versions/latest | jq
```

### List All Schemas
```bash
curl http://localhost:8081/subjects | jq
```

### View Schema Version History
```bash
curl http://localhost:8081/subjects/OrderCreatedEvent/versions | jq
```

---

## Test Event Payloads

### ✅ Test 1: Valid Order Event

**Description**: All required fields present, correct types

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-2025-001",
    "bloodType": "O_NEGATIVE",
    "quantity": 3,
    "priority": "URGENT",
    "facilityId": "FAC-001",
    "requestedBy": "DR-SMITH"
  }'
```

**Expected**: Event published to `biopro.orders.events`, no DLQ entry

---

### ❌ Test 2: Invalid Event - Unknown Fields

**Description**: Fields that don't exist in schema

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "invalidField": "bad data",
    "unknownProperty": "this should not be here"
  }'
```

**Expected Error**:
```
errorMessage: "Error serializing Avro message | Cause: Field orderNumber type:LONG pos:0 not set and has no default value"
```

---

### ❌ Test 3: Invalid Event - Missing Required Fields

**Description**: Missing facilityId and requestedBy

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-2025-002",
    "bloodType": "A_POSITIVE",
    "quantity": 2
  }'
```

**Expected Error**:
```
errorMessage: "Failed to convert event to Avro GenericRecord | Cause: Field 'locationCode' is required but was null | Cause: Cannot build record with null required field"
```

---

### ❌ Test 4: Invalid Event - Type Mismatch

**Description**: quantity is string instead of integer

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-2025-003",
    "bloodType": "O_NEGATIVE",
    "quantity": "not-a-number",
    "priority": "URGENT",
    "facilityId": "FAC-001",
    "requestedBy": "DR-JONES"
  }'
```

**Expected Error**:
```
errorMessage: "Type mismatch for field 'quantity': expected int, got string"
```

---

### ❌ Test 5: Invalid Event - Null Required Field

**Description**: bloodType is null when it shouldn't be

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-2025-004",
    "bloodType": null,
    "quantity": 1,
    "priority": "ROUTINE",
    "facilityId": "FAC-002",
    "requestedBy": "DR-WILSON"
  }'
```

**Expected Error**:
```
errorMessage: "Field 'bloodType' cannot be null"
```

---

### ❌ Test 6: Invalid Event - Wrong Enum Value

**Description**: Invalid priority value

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-2025-005",
    "bloodType": "AB_POSITIVE",
    "quantity": 5,
    "priority": "SUPER_URGENT_PLEASE",
    "facilityId": "FAC-003",
    "requestedBy": "DR-DAVIS"
  }'
```

**Expected**: May pass or fail depending on schema constraints

---

## Monitoring Commands

### View Main Orders Topic
```bash
./kcat.sh -C -t biopro.orders.events -e -f 'Offset %o | Key: %k\nPayload: %s\n\n'
```

### View DLQ Topic (Last 10 Messages)
```bash
./kcat.sh -C -t biopro.orders.dlq -e -o -10 -f 'DLQ Event %o\nKey: %k\nValue: %s\n\n'
```

### Monitor DLQ in Real-Time
```bash
./kcat.sh -C -t biopro.orders.dlq -f 'DLQ Event at %T\nError: %s\n\n'
```

### Pretty-Print DLQ Message
```bash
./kcat.sh -C -t biopro.orders.dlq -c 1 -e | jq
```

### Count DLQ Messages
```bash
./kcat.sh -C -t biopro.orders.dlq -e -f '%o\n' | wc -l
```

---

## Service Health Checks

### Orders Service
```bash
curl http://localhost:8080/actuator/health | jq
```

### Schema Registry
```bash
curl http://localhost:8081/subjects | jq
```

### Redpanda/Kafka
```bash
./kcat.sh -L
```

---

## Log Commands

### View Orders Service Logs
```bash
docker logs biopro-orders-service --tail 50 -f
```

### View Schema Registry Logs
```bash
docker logs biopro-schema-registry --tail 50 -f
```

### View Redpanda Logs
```bash
docker logs biopro-redpanda --tail 50 -f
```

---

## Prometheus Metrics

### DLQ Event Count
```
http://localhost:9090/graph?g0.expr=biopro_dlq_events_total
```

### Schema Validation Errors
```
http://localhost:9090/graph?g0.expr=biopro_schema_validation_errors_total
```

### Circuit Breaker State
```
http://localhost:9090/graph?g0.expr=biopro_circuit_breaker_state
```

---

## Advanced kcat Commands

### Produce Test DLQ Event
```bash
echo '{"test":"message"}' | ./kcat.sh -P -t biopro.orders.dlq -k "test-key"
```

### Consume with Offset
```bash
./kcat.sh -C -t biopro.orders.dlq -p 0 -o 5 -c 1
```

### List Topics
```bash
./kcat.sh -L -t biopro.orders.dlq
```

### Show Broker Metadata
```bash
./kcat.sh -L | head -20
```

---

## Cleanup Commands

### Stop All Services
```bash
docker-compose down
```

### Stop and Remove Volumes (Full Reset)
```bash
docker-compose down -v
```

### Restart Single Service
```bash
docker-compose restart orders-service
```

### Rebuild Single Service
```bash
docker-compose build orders-service
docker-compose up -d orders-service
```

---

## Demo Flow Checklist

**Before Demo**
```bash
# 1. Start everything
./start-all.sh

# 2. Verify services
docker ps

# 3. Open monitoring
./kafka-ui.sh
```

**During Demo**
```bash
# 1. Show schema
curl http://localhost:8081/subjects/OrderCreatedEvent/versions/latest | jq

# 2. Valid event
<paste Test 1 command>

# 3. Invalid events
<paste Test 2, 3, 4 commands>

# 4. View DLQ
./kcat.sh -C -t biopro.orders.dlq -e | jq
```

**After Demo**
```bash
# Optional: Clean up
docker-compose down
```

---

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker logs biopro-orders-service

# Restart service
docker-compose restart orders-service
```

### Can't Connect to Kafka
```bash
# Verify Redpanda is healthy
docker ps | grep redpanda

# Check Redpanda logs
docker logs biopro-redpanda --tail 100
```

### Schema Registry Issues
```bash
# Test connectivity
curl http://localhost:8081/subjects

# Restart schema registry
docker-compose restart schema-registry
```

### DLQ Not Receiving Messages
```bash
# 1. Check topic exists
./kcat.sh -L | grep dlq

# 2. Check service logs
docker logs biopro-orders-service | grep DLQ

# 3. Verify DLQ processor is active
docker logs biopro-orders-service | grep "BioPro Event Governance Framework Initialized"
```

---

## URLs Quick Access

| Service | URL |
|---------|-----|
| Orders Service | http://localhost:8080/actuator/health |
| Collections Service | http://localhost:8083/actuator/health |
| Manufacturing Service | http://localhost:8082/actuator/health |
| Schema Registry | http://localhost:8081/subjects |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

---

## JSON Response Examples

### Successful Order Response
```json
{
  "status": "success",
  "message": "Order created successfully",
  "orderId": "ORD-2025-001",
  "eventId": "88d19d16-6550-4793-9723-6bd84b07b3aa"
}
```

### DLQ Event Structure
```json
{
  "dlqEventId": "928462db-3ab0-466a-a7e7-7c815125c00c",
  "originalEventId": "88d19d16-6550-4793-9723-6bd84b07b3aa",
  "module": "orders",
  "eventType": "OrderCreatedEvent",
  "originalTopic": "biopro.orders.events",
  "originalPayload": "",
  "errorType": "SCHEMA_VALIDATION",
  "errorMessage": "Error serializing Avro message | Cause: Field orderNumber type:LONG pos:0 not set and has no default value",
  "stackTrace": "...",
  "retryCount": 0,
  "priority": "HIGH",
  "originalTimestamp": 1763080403.457581,
  "dlqTimestamp": 1763080403.457583,
  "correlationId": "5dcc275b-85e0-4e08-8ce3-6eb793c99ebf",
  "businessContext": null,
  "status": "PENDING",
  "lastReprocessingAttempt": null,
  "reprocessingCount": 0,
  "reprocessedBy": null
}
```

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Companion to**: DEMO-SCRIPT.md
