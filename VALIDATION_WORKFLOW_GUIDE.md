# BioPro Event Governance - Complete Validation Workflow Guide

## Overview
This guide demonstrates the complete workflow for schema registration, event validation, DLQ routing, and monitoring with Prometheus/Grafana.

**Infrastructure:**
- **Redpanda**: Kafka-compatible streaming platform (replaces Kafka + Zookeeper)
- **biopro-schema-registry**: Dedicated Confluent Schema Registry container
- **Redpanda Console**: Web UI for Kafka/Redpanda monitoring (http://localhost:8090)
- **kcat**: Command-line Kafka consumer/producer for testing

---

## 1. Schema Registration

### Understanding Schema Management

The BioPro system uses a **dedicated Confluent Schema Registry** (`biopro-schema-registry`) that is separate from Redpanda. This provides:
- Schema versioning and compatibility checking
- Centralized schema management
- BACKWARD compatibility enforcement by default

**Important**: Schema files are located in:
```
biopro-common-integration/src/main/resources/avro/OrderCreatedEvent.avsc
```

### Register OrderCreatedEvent Schema (Complete)

The complete schema includes all required fields. **Always use the complete schema** to avoid serialization errors.

```bash
# Option 1: Register from schema file (Recommended)
python3 -c "
import json
import requests

# Read the schema file
with open('biopro-common-integration/src/main/resources/avro/OrderCreatedEvent.avsc', 'r') as f:
    schema_str = f.read()

# Register the schema
response = requests.post(
    'http://localhost:8081/subjects/OrderCreatedEvent/versions',
    json={'schema': schema_str},
    headers={'Content-Type': 'application/vnd.schemaregistry.v1+json'}
)

print(f'Status: {response.status_code}')
print(response.text)
"

# Option 2: Register from within schema-registry container
docker exec biopro-schema-registry curl -X POST http://localhost:8081/subjects/OrderCreatedEvent/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @- <<'EOF'
{
  "schema": "$(cat biopro-common-integration/src/main/resources/avro/OrderCreatedEvent.avsc | jq -c . | sed 's/"/\\"/g')"
}
EOF
```

**Expected Response:**
```json
{"id":1}
```

### Schema Fields (Complete List)

The OrderCreatedEvent schema contains:

**Top-level fields:**
- `eventId` (string, UUID)
- `occurredOn` (long, timestamp-millis)
- `eventType` (string, default: "OrderCreated")
- `eventVersion` (string, default: "1.0")
- `payload` (OrderCreatedPayload record)

**Payload fields (24 fields total):**
- `orderNumber`, `externalId`, `orderStatus`
- `locationCode`, `locationName`
- `createDate`, `createDateTimeZone`, `createEmployeeCode`
- `shipmentType`, `priority`
- `shippingMethod`, `productCategory`, `desiredShippingDate`
- `shippingCustomerCode`, `shippingCustomerName`, `billingCustomerCode`
- `comments`, `willPickUp`, `willPickUpPhoneNumber`
- `transactionId` (required, UUID)
- `quarantinedProducts`, `labelStatus`, `version`
- `orderItems` (array of OrderItemCreated)

### Verify Schema Registration

```bash
# List all registered schemas
curl http://localhost:8081/subjects

# Get schema details
curl http://localhost:8081/subjects/OrderCreatedEvent/versions/latest | python3 -m json.tool

# List all fields in the payload
curl -s http://localhost:8081/subjects/OrderCreatedEvent/versions/latest | \
  python3 -c "import sys, json; data = json.load(sys.stdin); \
  schema = json.loads(data['schema']); \
  payload_fields = schema['fields'][4]['type']['fields']; \
  print('\n'.join([f['name'] for f in payload_fields]))"
```

### Handling Schema Updates and Incompatibility

**Problem**: Schema Registry enforces BACKWARD compatibility by default. If you need to register an incompatible schema:

```bash
# Step 1: Check current compatibility mode
curl http://localhost:8081/config

# Step 2: Soft delete the schema
curl -X DELETE http://localhost:8081/subjects/OrderCreatedEvent

# Step 3: Permanently delete the schema
curl -X DELETE "http://localhost:8081/subjects/OrderCreatedEvent?permanent=true"

# Step 4: Register the new schema
python3 -c "
import json, requests
with open('biopro-common-integration/src/main/resources/avro/OrderCreatedEvent.avsc', 'r') as f:
    schema_str = f.read()
response = requests.post(
    'http://localhost:8081/subjects/OrderCreatedEvent/versions',
    json={'schema': schema_str},
    headers={'Content-Type': 'application/vnd.schemaregistry.v1+json'}
)
print(f'Status: {response.status_code}')
print(response.text)
"
```

**Common Compatibility Errors:**
- `READER_FIELD_MISSING_DEFAULT_VALUE`: New required field without default
- `NAME_MISMATCH`: Record name changed (e.g., OrderItem → OrderItemCreated)
- `TYPE_MISMATCH`: Field type changed incompatibly

---

## 2. Valid Event - Passes Validation

### Example: Complete Valid Event Structure

**Important**: The API expects the following request format:
- `facilityId` (not `locationCode`) - mapped to `payload.locationCode` in the schema
- `bloodType` - mapped to `orderItems[].bloodType`
- `quantity` - mapped to `orderItems[].quantity`
- `priority` - ROUTINE, URGENT, or LIFE_THREATENING
- `orderId` (optional) - external order ID
- `requestedBy` (optional) - employee code

```bash
# Test with a valid event from host machine
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "facilityId": "LAB001",
    "bloodType": "O_NEGATIVE",
    "quantity": 2,
    "priority": "ROUTINE"
  }'

# Or from within Docker network
docker exec biopro-schema-registry curl -X POST http://biopro-orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-12345",
    "facilityId": "FAC-001",
    "bloodType": "A_POSITIVE",
    "quantity": 3,
    "priority": "URGENT",
    "requestedBy": "Dr. Johnson"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Order event published successfully",
  "orderId": "ORD-12345"
}
```

### What Happens Internally

1. **Event Building** (`OrderEventPublisher.buildOrderEvent()`)
   ```java
   Map<String, Object> event = new HashMap<>();
   event.put("eventId", UUID.randomUUID().toString());
   event.put("occurredOn", System.currentTimeMillis());
   event.put("eventType", "OrderCreated");
   event.put("eventVersion", "1.0");
   // ... builds payload structure
   ```

2. **Schema Validation** (`SchemaRegistryService.validateEvent()`)
   ```
   ✓ Schema exists: OrderCreatedEvent
   ✓ Required field 'eventId': present
   ✓ Required field 'occurredOn': present
   ✓ Required field 'payload': present
   ✓ Validation result: VALID
   ```

3. **Avro Serialization** (`convertToGenericRecord()`)
   ```
   → Converts Map to GenericRecord
   → Schema Registry assigns schema ID
   → Binary Avro encoding
   ```

4. **Kafka Publishing**
   ```
   → Topic: biopro.orders.events
   → Key: <eventId>
   → Value: <Avro GenericRecord>
   → Status: SUCCESS
   ```

### Check Logs for Valid Event

```bash
docker-compose logs --tail=20 orders-service | grep -E "(Successfully published|validation)"
```

**Expected Output:**
```
2025-11-06 05:22:53 - Received order creation request: OrderController.OrderRequest(orderId=ORD-12345, ...)
2025-11-06 05:22:53 - Successfully published order event: <event-id>
```

### Verify Event in Kafka

```bash
# Consume from main topic using kcat (Avro binary - will show scrambled)
docker exec biopro-kcat kcat -b redpanda:9092 \
  -C -t biopro.orders.events \
  -c 1 -o -1 \
  -f 'Topic: %t | Key: %k | Offset: %o\nValue: %s\n'

# Or use Redpanda Console web UI
# Navigate to: http://localhost:8090
# Click on Topics → biopro.orders.events → Messages
```

---

## 3. Invalid Event - Failed Validation

### Example 1: Missing Required Field (occurredOn)

```bash
# Send event missing 'occurredOn' field
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "invalidField": "bad data"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Order event published successfully",
  "orderId": null
}
```

**Note:** The API returns success, but internally validation fails and event goes to DLQ.

### What Happens Internally

1. **Event Building**
   ```
   → Builds event Map from request
   → Sets eventId, occurredOn, eventType, eventVersion
   → Request has "invalidField" but missing required order data
   ```

2. **Schema Validation FAILS**
   ```
   ✗ Required field 'payload': MISSING or NULL
   → ValidationResult.valid = false
   → ValidationResult.errorMessage = "Missing required field: payload"
   ```

3. **DLQ Routing Triggered**
   ```java
   dlqProcessor.routeToDLQ(
       eventId,
       "orders",
       "OrderCreatedEvent",
       "biopro.orders.events",
       originalPayload,
       new RuntimeException("Schema validation failed: Missing required field: payload"),
       0
   );
   ```

4. **DLQ Event Created**
   ```json
   {
     "dlqEventId": "503dc2dd-dc7f-4036-8c8a-e9c724a2b198",
     "originalEventId": "67bd96ea-6d95-46cf-baae-6fe0cc2b159e",
     "module": "orders",
     "eventType": "OrderCreatedEvent",
     "originalTopic": "biopro.orders.events",
     "errorType": "PROCESSING_ERROR",
     "errorMessage": "Schema validation failed: Missing required field: payload",
     "priority": "HIGH",
     "status": "PENDING",
     "retryCount": 0
   }
   ```

5. **Published to DLQ Topic**
   ```
   → Topic: biopro.orders.dlq
   → Serialization: JSON (not Avro)
   → Status: SUCCESS
   ```

### Check Logs for Failed Validation

```bash
docker-compose logs --since=1m orders-service | grep -E "(validation failed|DLQ)"
```

**Expected Output:**
```
2025-11-06 05:18:05 - Schema validation failed for event 67bd96ea-6d95-46cf-baae-6fe0cc2b159e: Missing required field: payload
2025-11-06 05:18:05 - Routing event to DLQ. EventId: 67bd96ea-6d95-46cf-baae-6fe0cc2b159e, Module: orders, EventType: OrderCreatedEvent, RetryCount: 0, Error: Schema validation failed: Missing required field: payload
2025-11-06 05:18:06 - Successfully routed event to DLQ: 503dc2dd-dc7f-4036-8c8a-e9c724a2b198
```

### Verify DLQ Event in Kafka

```bash
# Consume from DLQ topic using kcat (JSON format - human readable)
docker exec biopro-kcat kcat -b redpanda:9092 \
  -C -t biopro.orders.dlq \
  -c 1 -o -1 \
  -f '%s\n' | python3 -m json.tool

# Or use Redpanda Console web UI
# Navigate to: http://localhost:8090
# Click on Topics → biopro.orders.dlq → Messages
```

**Expected Output:**
```json
{
  "dlqEventId": "503dc2dd-dc7f-4036-8c8a-e9c724a2b198",
  "originalEventId": "67bd96ea-6d95-46cf-baae-6fe0cc2b159e",
  "module": "orders",
  "eventType": "OrderCreatedEvent",
  "originalTopic": "biopro.orders.events",
  "originalPayload": "e2V2ZW50SWQ9...",
  "errorType": "PROCESSING_ERROR",
  "errorMessage": "Schema validation failed: Missing required field: payload",
  "stackTrace": "com.biopro.demo.orders.service.OrderEventPublisher.publishOrderCreated...",
  "retryCount": 0,
  "priority": "HIGH",
  "originalTimestamp": 1762406285.449878348,
  "dlqTimestamp": 1762406285.449887856,
  "correlationId": "0fa3d16f-3f41-41bc-9556-2d9627b0fa05",
  "status": "PENDING",
  "reprocessingCount": 0
}
```

---

## 4. Monitoring with Prometheus

### Access Prometheus UI

```
URL: http://localhost:9090
```

### Key Metrics to Query

#### 1. Schema Validation Metrics

```promql
# Total schema validations
biopro_schema_validation_total

# Schema validation rate (per second)
rate(biopro_schema_validation_total[5m])

# Failed validations
biopro_schema_validation_total{result="failure"}

# Success rate percentage
100 * sum(rate(biopro_schema_validation_total{result="success"}[5m])) / sum(rate(biopro_schema_validation_total[5m]))
```

#### 2. DLQ Metrics

```promql
# Total DLQ events
biopro_dlq_events_total

# DLQ events by error type
biopro_dlq_events_total{error_type="SCHEMA_VALIDATION"}

# DLQ events rate
rate(biopro_dlq_events_total[5m])

# DLQ events by module
sum by (module) (biopro_dlq_events_total)
```

#### 3. Kafka Metrics

```promql
# Kafka producer send rate
kafka_producer_records_sent_total

# Kafka producer errors
kafka_producer_record_error_total

# Average batch size
kafka_producer_batch_size_avg
```

#### 4. Application Metrics

```promql
# HTTP requests
http_server_requests_seconds_count{uri="/api/orders"}

# HTTP request duration (95th percentile)
histogram_quantile(0.95, rate(http_server_requests_seconds_bucket[5m]))

# JVM memory usage
jvm_memory_used_bytes{area="heap"}
```

### Test Metrics Collection

```bash
# Generate test events
for i in {1..10}; do
  docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
    -H "Content-Type: application/json" \
    -d '{"orderId": "ORD-'$i'", "facilityId": "FAC-001", "bloodType": "A+", "quantity": 1, "priority": "ROUTINE", "requestedBy": "Tester"}'
  sleep 1
done

# Generate invalid events for DLQ
for i in {1..5}; do
  docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
    -H "Content-Type: application/json" \
    -d '{"invalid": "data-'$i'"}'
  sleep 1
done
```

### Check Metrics Endpoint

```bash
# View raw metrics
curl http://localhost:8080/actuator/prometheus
```

---

## 5. Grafana Dashboard Setup

### Access Grafana

```
URL: http://localhost:3000
Username: admin
Password: admin
```

### Add Prometheus Data Source

1. Navigate to **Configuration → Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Configure:
   - **URL**: `http://prometheus:9090`
   - **Access**: Server (default)
5. Click **Save & Test**

### Create BioPro Monitoring Dashboard

#### Dashboard JSON Configuration

```json
{
  "dashboard": {
    "title": "BioPro Event Governance Monitoring",
    "panels": [
      {
        "title": "Schema Validation Rate",
        "targets": [
          {
            "expr": "rate(biopro_schema_validation_total[5m])",
            "legendFormat": "{{result}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "DLQ Events by Error Type",
        "targets": [
          {
            "expr": "sum by (error_type) (biopro_dlq_events_total)",
            "legendFormat": "{{error_type}}"
          }
        ],
        "type": "piechart"
      },
      {
        "title": "Validation Success Rate %",
        "targets": [
          {
            "expr": "100 * sum(rate(biopro_schema_validation_total{result=\"success\"}[5m])) / sum(rate(biopro_schema_validation_total[5m]))"
          }
        ],
        "type": "stat"
      },
      {
        "title": "HTTP Request Rate",
        "targets": [
          {
            "expr": "rate(http_server_requests_seconds_count{uri=\"/api/orders\"}[5m])",
            "legendFormat": "{{status}}"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

### Manual Dashboard Creation Steps

#### Panel 1: Schema Validation Success Rate

1. Click **Add panel**
2. Select **Stat** visualization
3. Query:
   ```promql
   100 * sum(rate(biopro_schema_validation_total{result="success"}[5m]))
   / sum(rate(biopro_schema_validation_total[5m]))
   ```
4. Unit: **Percent (0-100)**
5. Thresholds:
   - Red: < 95
   - Yellow: < 99
   - Green: >= 99

#### Panel 2: Validation Rate Over Time

1. Add panel → **Time series**
2. Query A:
   ```promql
   rate(biopro_schema_validation_total{result="success"}[5m])
   ```
   Legend: `Success`
3. Query B:
   ```promql
   rate(biopro_schema_validation_total{result="failure"}[5m])
   ```
   Legend: `Failure`

#### Panel 3: DLQ Events by Module

1. Add panel → **Bar chart**
2. Query:
   ```promql
   sum by (module) (biopro_dlq_events_total)
   ```

#### Panel 4: Active DLQ Events (Status = PENDING)

1. Add panel → **Stat**
2. Query:
   ```promql
   sum(biopro_dlq_pending_events)
   ```
3. Thresholds:
   - Green: 0
   - Yellow: 1-10
   - Red: > 10

#### Panel 5: HTTP Response Time (p95)

1. Add panel → **Time series**
2. Query:
   ```promql
   histogram_quantile(0.95,
     rate(http_server_requests_seconds_bucket{uri="/api/orders"}[5m])
   )
   ```
3. Unit: **seconds (s)**

#### Panel 6: Kafka Producer Success Rate

1. Add panel → **Time series**
2. Query:
   ```promql
   rate(kafka_producer_records_sent_total[5m])
   ```

### Import Pre-built Dashboard

1. Go to **Dashboards → Import**
2. Paste the dashboard JSON above
3. Select **Prometheus** data source
4. Click **Import**

---

## 6. End-to-End Testing Workflow

### Complete Test Scenario

```bash
#!/bin/bash

echo "=== BioPro Event Governance Test Workflow ==="
echo ""

# 1. Check Schema Registration
echo "1. Verifying schema registration..."
curl -s http://localhost:8081/subjects/OrderCreatedEvent/versions/latest | python3 -m json.tool
echo ""

# 2. Verify schema has all 24 payload fields
echo "2. Checking schema field count..."
curl -s http://localhost:8081/subjects/OrderCreatedEvent/versions/latest | \
  python3 -c "import sys, json; data = json.load(sys.stdin); \
  schema = json.loads(data['schema']); \
  payload_fields = schema['fields'][4]['type']['fields']; \
  print(f'✓ Schema has {len(payload_fields)} payload fields (expected: 24)')"
echo ""

# 3. Send Valid Event
echo "3. Sending valid event..."
curl -s -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId": "TEST-VALID", "facilityId": "LAB001", "bloodType": "AB_NEGATIVE", "quantity": 2, "priority": "ROUTINE", "requestedBy": "Test User"}' | python3 -m json.tool
echo ""

# 4. Send Invalid Event
echo "4. Sending invalid event (missing required fields)..."
curl -s -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"wrongField": "wrong value"}' | python3 -m json.tool
echo ""

# 5. Wait for processing
echo "5. Waiting 3 seconds for event processing..."
sleep 3

# 6. Check validation logs
echo "6. Checking validation logs..."
docker logs --tail=10 biopro-orders-service 2>&1 | grep -E "(validation|Successfully published)"
echo ""

# 7. Check DLQ using kcat
echo "7. Checking DLQ for failed events..."
docker exec biopro-kcat kcat -b redpanda:9092 \
  -C -t biopro.orders.dlq \
  -c 1 -o -1 \
  -f '%s\n' 2>/dev/null | python3 -m json.tool
echo ""

# 8. Check main topic
echo "8. Checking main topic for valid events..."
docker exec biopro-kcat kcat -b redpanda:9092 \
  -C -t biopro.orders.events \
  -c 1 -o -1 \
  -f 'Key: %k | Offset: %o | Size: %S bytes\n' 2>/dev/null
echo ""

# 9. Check Prometheus metrics
echo "9. Checking Prometheus metrics..."
curl -s http://localhost:8080/actuator/prometheus | grep "biopro_schema_validation_total"
echo ""

echo "=== Test Complete ==="
echo ""
echo "Access UIs:"
echo "  Redpanda Console: http://localhost:8090"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000"
```

Save as `test_workflow.sh` and run:
```bash
chmod +x test_workflow.sh
./test_workflow.sh
```

---

## 7. Troubleshooting

### Schema Validation Not Working

```bash
# Check if schema exists
curl http://localhost:8081/subjects

# Check Schema Registry connectivity and health
docker logs --tail 20 biopro-schema-registry

# Check orders-service can reach Schema Registry
docker exec biopro-orders-service curl http://schema-registry:8081/subjects

# Verify schema-registry is healthy
docker ps --filter "name=biopro-schema-registry" --format "{{.Names}}\t{{.Status}}"
```

### Schema Mismatch Errors (Critical)

**Symptoms:**
- Events going to DLQ with error: `Not a valid schema field: <fieldName>`
- Error: `Failed to convert event to Avro GenericRecord`
- NullPointerException for required fields

**Diagnosis:**
```bash
# Step 1: Check what fields are in the registered schema
curl -s http://localhost:8081/subjects/OrderCreatedEvent/versions/latest | \
  python3 -c "import sys, json; data = json.load(sys.stdin); \
  schema = json.loads(data['schema']); \
  payload_fields = schema['fields'][4]['type']['fields']; \
  print('Registered schema has', len(payload_fields), 'payload fields:'); \
  print('\n'.join([f['name'] for f in payload_fields]))"

# Step 2: Check what fields the code expects (from logs)
docker logs --tail 100 biopro-orders-service 2>&1 | grep -i "not a valid schema field"

# Step 3: Compare with source schema file
echo "Source schema file has these fields:"
python3 -c "
import json
with open('biopro-common-integration/src/main/resources/avro/OrderCreatedEvent.avsc', 'r') as f:
    schema = json.load(f)
    payload_fields = schema['fields'][4]['type']['fields']
    print(f'{len(payload_fields)} fields:')
    print('\n'.join([f['name'] for f in payload_fields]))
"
```

**Solution:**
If the registered schema is missing fields:
```bash
# 1. Delete the old incompatible schema
curl -X DELETE http://localhost:8081/subjects/OrderCreatedEvent
curl -X DELETE "http://localhost:8081/subjects/OrderCreatedEvent?permanent=true"

# 2. Re-register the complete schema from source
python3 -c "
import json, requests
with open('biopro-common-integration/src/main/resources/avro/OrderCreatedEvent.avsc', 'r') as f:
    schema_str = f.read()
response = requests.post(
    'http://localhost:8081/subjects/OrderCreatedEvent/versions',
    json={'schema': schema_str},
    headers={'Content-Type': 'application/vnd.schemaregistry.v1+json'}
)
print(f'Status: {response.status_code}')
print(response.text)
"

# 3. Verify all 24 payload fields are now registered
curl -s http://localhost:8081/subjects/OrderCreatedEvent/versions/latest | \
  python3 -c "import sys, json; data = json.load(sys.stdin); \
  schema = json.loads(data['schema']); \
  payload_fields = schema['fields'][4]['type']['fields']; \
  print(f'✓ Schema now has {len(payload_fields)} payload fields')"
```

### Events Not Going to DLQ

```bash
# Check DLQ topic exists using kcat
docker exec biopro-kcat kcat -b redpanda:9092 -L | grep dlq

# Check DLQ processor logs
docker logs --tail 50 biopro-orders-service | grep -i dlq

# Verify JSON serialization is configured
docker logs biopro-orders-service | grep "dlqKafkaTemplate"
```

### Request Format Errors

**Symptoms:**
- NullPointerException for locationCode or other fields
- DLQ error: `null value for (non-nullable) string`

**Solution:**
Ensure you're using the correct request format:
```json
{
  "facilityId": "LAB001",        // NOT "locationCode"
  "bloodType": "O_NEGATIVE",     // Use underscores, not plus signs
  "quantity": 2,
  "priority": "ROUTINE"          // ROUTINE, URGENT, or LIFE_THREATENING
}
```

### Prometheus Not Scraping Metrics

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq .

# Check actuator endpoint is accessible
curl http://localhost:8080/actuator/prometheus

# Check Prometheus configuration
docker exec biopro-prometheus cat /etc/prometheus/prometheus.yml
```

### Grafana Not Showing Data

```bash
# Test Prometheus data source from Grafana container
docker exec biopro-grafana curl http://prometheus:9090/api/v1/query?query=up

# Check Grafana logs
docker-compose logs grafana | tail -20

# Verify time range in dashboard (last 5 minutes)
```

---

## 8. Metrics Reference

### BioPro Custom Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `biopro_schema_validation_total` | Counter | `module`, `result` | Total schema validations |
| `biopro_dlq_events_total` | Counter | `module`, `event_type`, `error_type` | Total DLQ events |
| `biopro_dlq_pending_events` | Gauge | `module` | Currently pending DLQ events |
| `biopro_event_published_total` | Counter | `module`, `event_type` | Successfully published events |

### Spring Boot Actuator Metrics

| Metric Name | Description |
|-------------|-------------|
| `http_server_requests_seconds` | HTTP request duration histogram |
| `jvm_memory_used_bytes` | JVM memory usage |
| `kafka_producer_records_sent_total` | Kafka records sent |
| `kafka_producer_record_error_total` | Kafka producer errors |

---

## 9. Architecture Flow Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/orders
       ▼
┌─────────────────────────────────────────────────┐
│          OrderController                         │
└──────┬──────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│      OrderEventPublisher                         │
│  1. Build event Map                              │
│  2. Validate against schema ──┐                  │
│  3. Convert to GenericRecord  │                  │
│  4. Publish to Kafka         │                  │
└──────┬────────────────────────┼──────────────────┘
       │                        │
       │ Valid                  │ Invalid
       ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│  Kafka Topic     │    │   DLQProcessor   │
│ orders.events    │    │  - Build DLQ evt │
│  (Avro Binary)   │    │  - Add metadata  │
└──────────────────┘    └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  Kafka Topic     │
                        │ orders.dlq       │
                        │  (JSON)          │
                        └──────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  Prometheus      │
                        │  - Scrapes       │
                        │    /actuator     │
                        │  - Stores metrics│
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   Grafana        │
                        │  - Visualizes    │
                        │  - Dashboards    │
                        │  - Alerts        │
                        └──────────────────┘
```

---

## 10. Quick Commands Reference

```bash
# Schema Operations
curl http://localhost:8081/subjects
curl http://localhost:8081/subjects/OrderCreatedEvent/versions/latest | python3 -m json.tool
curl http://localhost:8081/config  # Check compatibility mode

# Register/Update Schema
python3 -c "
import json, requests
with open('biopro-common-integration/src/main/resources/avro/OrderCreatedEvent.avsc', 'r') as f:
    schema_str = f.read()
response = requests.post(
    'http://localhost:8081/subjects/OrderCreatedEvent/versions',
    json={'schema': schema_str},
    headers={'Content-Type': 'application/vnd.schemaregistry.v1+json'}
)
print(f'Status: {response.status_code}, Response: {response.text}')
"

# Delete Schema (for incompatible updates)
curl -X DELETE http://localhost:8081/subjects/OrderCreatedEvent
curl -X DELETE "http://localhost:8081/subjects/OrderCreatedEvent?permanent=true"

# Send Valid Event (from host)
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"facilityId": "LAB001", "bloodType": "O_NEGATIVE", "quantity": 2, "priority": "ROUTINE"}'

# Send Valid Event (from Docker network)
docker exec biopro-schema-registry curl -X POST http://biopro-orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId": "TEST", "facilityId": "FAC-001", "bloodType": "A_POSITIVE", "quantity": 1, "priority": "ROUTINE", "requestedBy": "Tester"}'

# Send Invalid Event (will go to DLQ)
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'

# Check Logs
docker logs --tail=20 biopro-orders-service | grep validation
docker logs --tail=20 biopro-orders-service | grep DLQ
docker logs --tail=30 biopro-orders-service 2>&1 | grep -i error

# Consume from Topics using kcat
docker exec biopro-kcat kcat -b redpanda:9092 -C -t biopro.orders.events -c 1 -o -1
docker exec biopro-kcat kcat -b redpanda:9092 -C -t biopro.orders.dlq -c 1 -o -1 -f '%s\n' | python3 -m json.tool

# List all topics
docker exec biopro-kcat kcat -b redpanda:9092 -L

# Check Metrics
curl http://localhost:8080/actuator/prometheus | grep biopro

# Prometheus Query (from terminal)
curl 'http://localhost:9090/api/v1/query?query=biopro_schema_validation_total'

# Access UIs
# Redpanda Console: http://localhost:8090
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Schema Registry API: http://localhost:8081
# Orders Service: http://localhost:8080
```

---

## Summary

This guide covers the complete validation workflow for the BioPro Event Governance POC:

### Infrastructure Components

1. ✅ **Redpanda** - Kafka-compatible streaming platform (port 19092)
   - Replaces Kafka + Zookeeper with a simpler architecture
   - Topic: `biopro.orders.events` (Avro), `biopro.orders.dlq` (JSON)

2. ✅ **biopro-schema-registry** - Dedicated Confluent Schema Registry (port 8081)
   - Centralized schema management with versioning
   - BACKWARD compatibility enforcement
   - **Critical**: Always use complete schema with all 24 payload fields

3. ✅ **Redpanda Console** - Web UI (port 8090)
   - Browse topics, messages, schemas
   - Monitor consumer groups and cluster health

4. ✅ **kcat** - Command-line Kafka tool
   - Fast message consumption and production
   - Works seamlessly through corporate proxy (Netskope)

### Workflow Steps

1. ✅ **Schema Registration** - Register complete Avro schema from source file
2. ✅ **Valid Events** - Events with correct `facilityId` and fields pass validation
3. ✅ **Invalid Events** - Schema mismatches/validation failures route to DLQ
4. ✅ **Prometheus** - Metrics collection from /actuator/prometheus endpoint
5. ✅ **Grafana** - Dashboard visualization of validation, DLQ, and system metrics

### Key Learnings

**Schema Management:**
- Always register the **complete schema** with all fields
- Schema mismatch causes events to go to DLQ
- Use `curl http://localhost:8081/subjects/OrderCreatedEvent/versions/latest` to verify

**Request Format:**
- Use `facilityId` (not `locationCode`)
- Blood types: `O_NEGATIVE`, `A_POSITIVE`, etc. (underscores, not plus signs)
- Priority: `ROUTINE`, `URGENT`, or `LIFE_THREATENING`

**Troubleshooting:**
- Check logs: `docker logs biopro-orders-service | grep -i error`
- Verify schema fields match code expectations
- Use Redpanda Console for visual debugging

For questions or issues, refer to the troubleshooting section or check the logs.
