# Schema Evolution Testing Guide

This guide explains how to test backward-compatible schema evolution with visualization in Grafana.

## What's Been Set Up

### 1. Schema Versions

**v1.0** (Current Production)
- Location: `schemas/orders/v1.0/OrderCreatedEvent.avsc`
- Fields: Standard order fields (orderNumber, status, location, items, etc.)

**v2.0** (New Version - Backward Compatible)
- Location: `schemas/orders/v2.0/OrderCreatedEvent.avsc`
- New Optional Fields:
  - `orderSource`: Source system (WEB, MOBILE, API, INTERNAL)
  - `requestedDeliveryDate`: When customer requested delivery (timestamp)
  - `emergencyContact`: Emergency contact info (nested record with name, phone, relationship)

### 2. Test Script

**File**: `test-schema-evolution.py`

**What it does**:
- Sends 100 order events in 10 batches
- Gradually increases v2.0 usage from 0% → 100% (linear rollout)
- Simulates real-world schema migration
- Prints progress and statistics

**Run it**:
```bash
python test-schema-evolution.py
```

## Testing Steps

### Step 1: Register v2.0 Schema

First, register the new v2.0 schema with Schema Registry:

```bash
cd C:/Users/MelvinJones/work/event-governance/poc

# Register v2.0 schema
python << 'PYEOF'
import requests
import json

with open('schemas/orders/v2.0/OrderCreatedEvent.avsc', 'r') as f:
    schema = json.load(f)

response = requests.post(
    'http://localhost:8081/subjects/OrderCreatedEvent/versions',
    json={'schema': json.dumps(schema)},
    headers={'Content-Type': 'application/vnd.schemaregistry.v1+json'}
)

if response.status_code in [200, 409]:  # 409 = already exists
    print(f"✅ v2.0 schema registered successfully!")
    print(f"   Response: {response.json()}")
else:
    print(f"❌ Failed to register schema: {response.status_code}")
    print(f"   Error: {response.text}")
PYEOF
```

### Step 2: Verify Schema Compatibility

```bash
# Check that v2.0 is backward compatible with v1.0
curl -X POST http://localhost:8081/compatibility/subjects/OrderCreatedEvent/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @schemas/orders/v2.0/OrderCreatedEvent.avsc
```

Expected output: `{"is_compatible":true}`

### Step 3: View Registered Schemas

```bash
# List all versions
curl http://localhost:8081/subjects/OrderCreatedEvent/versions

# Get v1.0 (version 1)
curl http://localhost:8081/subjects/OrderCreatedEvent/versions/1

# Get v2.0 (version 2)
curl http://localhost:8081/subjects/OrderCreatedEvent/versions/2
```

### Step 4: Run Evolution Test

```bash
python test-schema-evolution.py
```

**Expected output**:
```
======================================================================
  BioPro Schema Evolution Test
  Simulating gradual migration from v1.0 to v2.0
======================================================================

Configuration:
  Total messages: 100
  Batch size: 10
  Batch delay: 2s
  Evolution pattern: Linear 0% -> 100% v2.0

Starting test...

[Batch 1/10] Sending 10 messages...
  ├─ v1.0: 9 | v2.0: 1 (10% v2.0)
  └─ Cumulative: v1.0=9, v2.0=1, failed=0

[Batch 2/10] Sending 10 messages...
  ├─ v1.0: 8 | v2.0: 2 (20% v2.0)
  └─ Cumulative: v1.0=17, v2.0=3, failed=0

...

======================================================================
  Test Complete!
======================================================================

Final Statistics:
  v1.0 messages: 48 (48.0%)
  v2.0 messages: 52 (52.0%)
  Failed: 0
  Total: 100

✅ Check Grafana dashboard to visualize schema version distribution!
```

### Step 5: Monitor in Grafana

1. **Open Grafana**: http://localhost:3000
2. **Navigate to**: BioPro DLQ Monitoring Dashboard
3. **Observe**:
   - Schema validation success rate (should be 100%)
   - Event processing rate
   - Cache hit/miss rates
   - Schema version distribution (once we add metrics)

## Current Limitations

### What Works Now:
✅ v2.0 schema created with backward-compatible fields
✅ Test script ready to send mixed v1/v2 events
✅ Schema Registry can store both versions
✅ Consumers can read both v1 and v2 events (backward compatible)

### What Needs Implementation:
❌ Schema version tracking in metrics
❌ Grafana panels to visualize version distribution
❌ Service code to accept v2 fields (orderSource, requestedDeliveryDate, emergencyContact)

## Next Steps

To complete the schema evolution testing, we need to:

1. **Add Version Tracking Metrics**
   - Track which schema version was used for each event
   - Export metrics to Prometheus

2. **Update Order Publisher**
   - Accept v2 fields in API
   - Populate v2 fields in event payload
   - Track version in metrics

3. **Create Grafana Dashboard Panel**
   - Show schema version distribution over time
   - Show v1 vs v2 percentage
   - Show migration progress

4. **Test Cache Behavior**
   - Send v1 events (uses v1 schema)
   - Wait > 1 minute (cache expires)
   - Register v2 schema
   - Send v2 events (uses v2 schema)
   - Verify both work correctly

## Schema Evolution Best Practices

### Backward Compatible Changes (Safe):
✅ Add optional fields with defaults
✅ Add new enum values
✅ Widen field types (int → long)
✅ Make required fields optional (with defaults)

### Breaking Changes (Requires Major Version):
❌ Remove fields
❌ Rename fields
❌ Change field types (incompatible)
❌ Make optional fields required
❌ Remove enum values

## Architecture

```
┌─────────────────┐
│  Test Script    │
│  (Python)       │
└────────┬────────┘
         │ POST /api/orders
         │ (v1 or v2 data)
         ▼
┌─────────────────┐
│ Orders Service  │
│                 │
│ 1. Validate     │──────► Schema Registry
│    against      │        (v1.0 or v2.0)
│    schema       │
│                 │
│ 2. Convert to   │
│    GenericRecord│
│                 │
│ 3. Publish to   │
│    Kafka        │
└────────┬────────┘
         │ Avro binary
         │ [0x00][schema_id][data]
         ▼
┌─────────────────┐
│     Kafka       │
│  biopro.orders  │
│     .events     │
└─────────────────┘
         │
         ▼
    Consumers
    (can read both
     v1 and v2)
```

## Troubleshooting

### Schema Registration Fails
```bash
# Check Schema Registry is running
curl http://localhost:8081/subjects

# Check schema validity
cat schemas/orders/v2.0/OrderCreatedEvent.avsc | python -m json.tool
```

### Events Going to DLQ
```bash
# Check DLQ messages
docker exec biopro-redpanda rpk topic consume biopro.orders.dlq --offset end --num 5

# Check validation errors in logs
docker logs biopro-orders-service | grep -i "validation failed"
```

### Cache Not Expiring
```bash
# Current TTL: 1 minute
# Wait 61 seconds and send new event
# Check logs for "Fetching schema from Schema Registry" (cache miss)
docker logs biopro-orders-service -f | grep "schema"
```

## References

- [Avro Schema Evolution](https://docs.confluent.io/platform/current/schema-registry/avro.html)
- [Schema Registry API](https://docs.confluent.io/platform/current/schema-registry/develop/api.html)
- [Backward Compatibility Rules](https://docs.confluent.io/platform/current/schema-registry/avro.html#backward-compatibility)
