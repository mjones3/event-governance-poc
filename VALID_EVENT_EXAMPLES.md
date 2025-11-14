# Valid Event Examples

Quick copy-paste commands for testing valid events.

---

## ⚠️ IMPORTANT: API Request Format

The `/api/orders` endpoint accepts a **simplified request format**:

```json
{
  "orderId": "string",
  "facilityId": "string",      // REQUIRED!
  "bloodType": "string",
  "quantity": number,
  "priority": "string",
  "requestedBy": "string"
}
```

**Do NOT send the full event structure with `eventId`, `occurredOn`, `payload`, etc.**
That structure is created internally by the service!

---

## Quick Test Commands

### Example 1: Urgent O+ Blood Order

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-URGENT-001",
    "facilityId": "FAC-ER-01",
    "bloodType": "O+",
    "quantity": 4,
    "priority": "URGENT",
    "requestedBy": "Dr. Sarah Johnson"
  }'
```

### Example 2: Routine AB- Blood Order

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-ROUTINE-002",
    "facilityId": "FAC-MAIN-01",
    "bloodType": "AB-",
    "quantity": 2,
    "priority": "ROUTINE",
    "requestedBy": "Dr. Michael Chen"
  }'
```

### Example 3: Life-Threatening A+ Order

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-CRITICAL-003",
    "facilityId": "FAC-ICU-01",
    "bloodType": "A+",
    "quantity": 6,
    "priority": "LIFE_THREATENING",
    "requestedBy": "Dr. Lisa Martinez"
  }'
```

### Example 4: B- Blood Order (Rare Type)

```bash
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-RARE-004",
    "facilityId": "FAC-SURGERY-01",
    "bloodType": "B-",
    "quantity": 1,
    "priority": "URGENT",
    "requestedBy": "Dr. James Wilson"
  }'
```

---

## Automated Test Script

Run multiple valid events at once:

```bash
chmod +x test_valid_events.sh
./test_valid_events.sh
```

This will send 4 different valid events and show the results.

---

## Complete Valid Event Structure

**IMPORTANT:** The structure below is the INTERNAL event structure created by the service.
**DO NOT send this to the API endpoint!**

The API endpoint `/api/orders` only accepts the simplified request format shown above.

This complete structure is what gets published to Kafka internally:

```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "occurredOn": 1699564800000,
  "eventType": "OrderCreated",
  "eventVersion": "1.0",
  "payload": {
    "orderNumber": 1001,
    "externalId": "EXT-ORD-12345",
    "orderStatus": "PENDING",
    "locationCode": "FAC-MAIN-01",
    "locationName": "Main Facility - Blood Bank",
    "createDate": 1699564800000,
    "createDateTimeZone": "UTC",
    "createEmployeeCode": "EMP-001",
    "shipmentType": "STANDARD",
    "priority": "URGENT",
    "transactionId": "550e8400-e29b-41d4-a716-446655440000",
    "orderItems": [
      {
        "productFamily": "BLOOD_PRODUCTS",
        "bloodType": "O+",
        "quantity": 2,
        "comments": null,
        "attributes": null
      }
    ]
  }
}
```

**Note:** The service automatically converts the simple API request into this nested structure.

---

## Field Descriptions

### API Request Fields (What You Send)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `orderId` | string | No | Your external order ID |
| `facilityId` | string | **YES** | Facility location code (REQUIRED!) |
| `bloodType` | string | No | Blood type (O+, O-, A+, A-, B+, B-, AB+, AB-) |
| `quantity` | int | No | Quantity requested |
| `priority` | string | No | ROUTINE, URGENT, LIFE_THREATENING |
| `requestedBy` | string | No | Person requesting the order |

### Internal Event Fields (What Gets Created)

The service automatically builds the complete event structure:

**Top-Level Fields:**
- `eventId` - Auto-generated UUID
- `occurredOn` - Auto-generated timestamp
- `eventType` - Set to "OrderCreated"
- `eventVersion` - Set to "1.0"

**Payload Fields:**
- `orderNumber` - Auto-generated from orderId hash
- `externalId` - From your `orderId`
- `orderStatus` - Set to "PENDING"
- `locationCode` - From your `facilityId`
- `createDate` - Auto-generated timestamp
- `createEmployeeCode` - From your `requestedBy`
- `priority` - From your `priority`
- `transactionId` - Auto-generated UUID
- `orderItems` - Built from your `bloodType` and `quantity`

---

## Valid Priority Values

- `ROUTINE` - Standard delivery
- `URGENT` - Expedited delivery
- `LIFE_THREATENING` - Critical/emergency delivery

---

## Valid Blood Types

- `O+`, `O-` (Universal donor)
- `A+`, `A-`
- `B+`, `B-`
- `AB+`, `AB-` (Universal recipient)

---

## Testing Scenarios

### Scenario 1: Single Valid Event

```bash
# Send one valid event
docker exec biopro-schema-registry curl -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId": "TEST-001", "facilityId": "FAC-001", "bloodType": "O+", "quantity": 2, "priority": "ROUTINE", "requestedBy": "Tester"}'

# Check logs
docker-compose logs --tail=5 orders-service | grep "Successfully published"
```

### Scenario 2: Bulk Valid Events

```bash
# Send 10 valid events
for i in {1..10}; do
  docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
    -H "Content-Type: application/json" \
    -d "{\"orderId\": \"BULK-$i\", \"facilityId\": \"FAC-001\", \"bloodType\": \"A+\", \"quantity\": $i, \"priority\": \"ROUTINE\", \"requestedBy\": \"Bulk Tester\"}"
  echo "Sent event $i"
  sleep 0.5
done

# Check total events
docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.events | awk -F ":" '{sum += $3} END {print "Total events:", sum}'
```

### Scenario 3: Different Priorities

```bash
# Routine
docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId": "PRIO-ROUTINE", "facilityId": "FAC-001", "bloodType": "O+", "quantity": 2, "priority": "ROUTINE", "requestedBy": "Dr. Smith"}'

# Urgent
docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId": "PRIO-URGENT", "facilityId": "FAC-001", "bloodType": "O+", "quantity": 2, "priority": "URGENT", "requestedBy": "Dr. Jones"}'

# Life-threatening
docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId": "PRIO-CRITICAL", "facilityId": "FAC-001", "bloodType": "O+", "quantity": 2, "priority": "LIFE_THREATENING", "requestedBy": "Dr. Williams"}'
```

---

## Verifying Results

### Check if event was published successfully

```bash
# View recent logs
docker-compose logs --tail=20 orders-service | grep -E "(Successfully published|validation)"

# Count events in main topic
docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.events | awk -F ":" '{sum += $3} END {print sum}'

# Count events in DLQ (should be 0 for valid events)
docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.dlq | awk -F ":" '{sum += $3} END {print sum}'
```

### Check metrics

```bash
# View validation metrics
curl -s http://localhost:8080/actuator/prometheus | grep biopro_schema_validation_total

# Prometheus UI
# Open: http://localhost:9090
# Query: rate(biopro_schema_validation_total{result="success"}[5m])
```

---

## Expected Successful Response

```json
{
  "success": true,
  "message": "Order event published successfully",
  "orderId": "ORD-URGENT-001"
}
```

---

## Common Issues

### Issue: Validation fails even with valid event

**Symptom:**
```
Schema validation failed for event: Missing required field: payload
```

**Cause:** The `OrderEventPublisher.buildOrderEvent()` method needs to properly construct the nested payload structure.

**Check:** Verify the event builder creates the correct structure with `payload` containing order details.

### Issue: 403 or authentication errors

**Cause:** Spring Security may be blocking requests.

**Solution:**
```bash
# Check if security is disabled in application.properties
docker exec biopro-orders-service cat /app/BOOT-INF/classes/application.properties | grep security
```

---

## Next Steps

After sending valid events:

1. **Check Kafka topic** for the event
2. **View Prometheus metrics** to see validation success count
3. **Create Grafana dashboard** to visualize event flow
4. **Test invalid events** to verify DLQ routing

See `VALIDATION_WORKFLOW_GUIDE.md` for complete workflow.
