# BioPro Event Schemas - Complete Inventory

## Schema Locations

### Primary Avro Schema Files (.avsc)

Your project has Avro schemas in multiple locations:

#### 1. Source Schemas (Primary)
Location: `biopro-common-integration/src/main/resources/avro/`

```
biopro-common-integration/src/main/resources/avro/
├── ApheresisPlasmaProductCreatedEvent.avsc  (298 lines)
├── CollectionReceivedEvent.avsc
└── OrderCreatedEvent.avsc
```

**This is your source of truth** - these are compiled into the JAR and used at runtime.

#### 2. Versioned Schema Directory
Location: `schemas/`

```
schemas/
├── manufacturing/
│   └── v1.0/
│       └── ApheresisPlasmaProductCreatedEvent.avsc
├── orders/
│   ├── v1.0/
│   │   └── OrderCreatedEvent.avsc
│   └── v2.0/
│       └── OrderCreatedEvent.avsc
└── collections/
    └── v1.0/
        └── CollectionReceivedEvent.avsc
```

**Note**: v2.0 schemas include backward-compatible new fields.

#### 3. EventCatalog Copies
Location: `event-catalog/events/`

```
event-catalog/events/
├── ApheresisPlasmaProductCreated/
│   └── schema.avsc
├── CollectionReceived/
│   └── schema.avsc
└── OrderCreated/
    └── schema.avsc
```

#### 4. Build Artifacts (Generated)
Location: `biopro-common-integration/target/classes/avro/`

These are copies created during Maven build - **do not edit directly**.

---

## JSON Example Payloads

**IMPORTANT**: Your project uses **Avro schemas**, not JSON schemas. However, the REST endpoints accept JSON request bodies that are then converted to Avro.

Below are JSON examples extracted from your actual Spring Boot request classes.

### 1. Manufacturing Event - ApheresisPlasmaProductCreated

**REST Endpoint**: `POST http://localhost:8082/api/manufacturing/products`

**JSON Request Example**:
```json
{
  "productId": "UNIT-2024-001",
  "productType": "PLASMA_APHERESIS",
  "productDescription": "Apheresis Plasma Product",
  "productFamily": "PLASMA",
  "completionStage": "COMPLETE",
  "weight": {
    "value": 250.5,
    "unit": "GRAMS"
  },
  "volume": {
    "value": 600.0,
    "unit": "ML"
  },
  "anticoagulantVolume": {
    "value": 63.0,
    "unit": "ML"
  },
  "drawTime": 1704067200000,
  "drawTimeZone": "America/Chicago",
  "donationType": "APHERESIS",
  "procedureType": "AUTOMATED",
  "collectionLocation": "CENTER-001",
  "manufacturingLocation": "FACILITY-002",
  "aboRh": "O_POS",
  "performedBy": "TECH-123",
  "occurredOnTimeZone": "America/Chicago",
  "createDateTimeZone": "UTC",
  "expirationDate": 1735689600000,
  "expirationTime": 1735689600000,
  "collectionTimeZone": "America/Chicago",
  "bagType": "TRIPLE_BAG",
  "autoConverted": false,
  "inputProducts": [],
  "additionalSteps": []
}
```

**Java Request Class**: `ManufacturingEventPublisher.ProductCreatedRequest`

**Published to Kafka Topic**: `biopro.manufacturing.events`

**Schema Registry Subject**: `ApheresisPlasmaProductCreatedEvent-value`

**Event Envelope Structure** (what goes to Kafka):
```json
{
  "eventId": "uuid-generated-by-service",
  "occurredOn": 1704067200000,
  "occurredOnTimeZone": "America/Chicago",
  "eventType": "ApheresisPlasmaProductCreated",
  "eventVersion": "1.0",
  "payload": {
    "unitNumber": "UNIT-2024-001",
    "productCode": "PLASMA_APHERESIS",
    "productDescription": "Apheresis Plasma Product",
    "productFamily": "PLASMA",
    "completionStage": "COMPLETE",
    "weight": {
      "value": 250.5,
      "unit": "GRAMS"
    },
    "volume": {
      "value": 600.0,
      "unit": "ML"
    },
    "anticoagulantVolume": {
      "value": 63.0,
      "unit": "ML"
    },
    "drawTime": 1704067200000,
    "drawTimeZone": "America/Chicago",
    "donationType": "APHERESIS",
    "procedureType": "AUTOMATED",
    "collectionLocation": "CENTER-001",
    "manufacturingLocation": "FACILITY-002",
    "aboRh": "O_POS",
    "performedBy": "TECH-123",
    "createDate": 1704067200000,
    "createDateTimeZone": "UTC",
    "expirationDate": 1735689600000,
    "expirationTime": 1735689600000,
    "collectionTimeZone": "America/Chicago",
    "bagType": "TRIPLE_BAG",
    "autoConverted": false,
    "inputProducts": [],
    "additionalSteps": []
  }
}
```

---

### 2. Orders Event - OrderCreated

**REST Endpoint**: `POST http://localhost:8083/api/orders`

**JSON Request Example (v1.0 - Minimal)**:
```json
{
  "orderId": "ORD-2024-001",
  "bloodType": "O_POS",
  "quantity": 2,
  "priority": "ROUTINE",
  "facilityId": "HOSP-123",
  "requestedBy": "DR-456",
  "orderStatus": "NEW"
}
```

**JSON Request Example (v2.0 - With New Fields)**:
```json
{
  "orderId": "ORD-2024-001",
  "bloodType": "O_POS",
  "quantity": 2,
  "priority": "URGENT",
  "facilityId": "HOSP-123",
  "requestedBy": "DR-456",
  "orderStatus": "NEW",
  "orderSource": "WEB",
  "requestedDeliveryDate": 1704153600000,
  "emergencyContact": {
    "name": "Jane Doe",
    "phone": "+1-555-0123",
    "relationship": "SPOUSE"
  }
}
```

**Java Request Class**: `OrderEventPublisher.OrderCreatedRequest`

**Published to Kafka Topic**: `biopro.orders.events`

**Schema Registry Subject**: `OrderCreatedEvent-value`

**Event Envelope Structure** (what goes to Kafka):
```json
{
  "eventId": "uuid-generated-by-service",
  "occurredOn": 1704067200000,
  "eventType": "OrderCreated",
  "eventVersion": "2.0",
  "payload": {
    "orderNumber": 12345678,
    "externalId": "ORD-2024-001",
    "orderStatus": "NEW",
    "locationCode": "HOSP-123",
    "locationName": null,
    "createDate": 1704067200000,
    "createDateTimeZone": "UTC",
    "createEmployeeCode": "DR-456",
    "shipmentType": null,
    "priority": "URGENT",
    "shippingMethod": null,
    "productCategory": null,
    "desiredShippingDate": null,
    "shippingCustomerCode": null,
    "shippingCustomerName": null,
    "billingCustomerCode": null,
    "comments": null,
    "willPickUp": false,
    "willPickUpPhoneNumber": null,
    "transactionId": "correlation-uuid",
    "quarantinedProducts": null,
    "labelStatus": null,
    "version": null,
    "orderItems": [
      {
        "productFamily": "BLOOD_PRODUCTS",
        "bloodType": "O_POS",
        "quantity": 2,
        "comments": null,
        "attributes": null
      }
    ],
    "orderSource": "WEB",
    "requestedDeliveryDate": 1704153600000,
    "emergencyContact": {
      "name": "Jane Doe",
      "phone": "+1-555-0123",
      "relationship": "SPOUSE"
    }
  }
}
```

**Schema Evolution Note**:
- v1.0 events: `eventVersion: "1.0"` - no `orderSource`, `requestedDeliveryDate`, or `emergencyContact`
- v2.0 events: `eventVersion: "2.0"` - includes new fields (backward compatible)

---

### 3. Collections Event - CollectionReceived

**REST Endpoint**: `POST http://localhost:8084/api/collections`

**JSON Request Example**:
```json
{
  "unitNumber": "UNIT-COL-2024-001",
  "donationType": "WHOLE_BLOOD",
  "status": "COLLECTED",
  "bagType": "SINGLE_BAG",
  "procedureType": "MANUAL",
  "collectionLocation": "CENTER-001",
  "aboRh": "A_POS",
  "drawTimeZone": "America/Chicago",
  "withdrawalTimeZone": "America/Chicago",
  "machineSerialNumber": "MACH-789",
  "machineType": "APHERESIS_DEVICE",
  "donationProperties": {
    "donorId": "DONOR-456",
    "donorWeight": "70kg"
  },
  "drawProperties": {
    "needleGauge": "16G",
    "armUsed": "LEFT"
  },
  "volumes": [
    {
      "type": "WHOLE_BLOOD",
      "amount": 450.0,
      "excludeInCalculation": false
    },
    {
      "type": "ANTICOAGULANT",
      "amount": 63.0,
      "excludeInCalculation": true
    }
  ]
}
```

**Java Request Class**: `CollectionEventPublisher.CollectionReceivedRequest`

**Published to Kafka Topic**: `biopro.collections.events`

**Schema Registry Subject**: `CollectionReceivedEvent-value`

**Event Structure** (what goes to Kafka - no envelope, flat structure):
```json
{
  "unitNumber": "UNIT-COL-2024-001",
  "status": "COLLECTED",
  "bagType": "SINGLE_BAG",
  "drawTime": 1704067200000,
  "drawTimeZone": "America/Chicago",
  "withdrawalTime": 1704067200000,
  "withdrawalTimeZone": "America/Chicago",
  "donationType": "WHOLE_BLOOD",
  "procedureType": "MANUAL",
  "collectionLocation": "CENTER-001",
  "aboRh": "A_POS",
  "machineSerialNumber": "MACH-789",
  "machineType": "APHERESIS_DEVICE",
  "donationProperties": {
    "donorId": "DONOR-456",
    "donorWeight": "70kg"
  },
  "drawProperties": {
    "needleGauge": "16G",
    "armUsed": "LEFT"
  },
  "volumes": [
    {
      "type": "WHOLE_BLOOD",
      "amount": 450.0,
      "excludeInCalculation": false
    },
    {
      "type": "ANTICOAGULANT",
      "amount": 63.0,
      "excludeInCalculation": true
    }
  ]
}
```

**Note**: Unlike the other events, `CollectionReceivedEvent` has a **flat structure** (no event envelope with `eventId`, `occurredOn`, etc.)

---

## Testing Your Events

### Using curl

**Manufacturing Event**:
```bash
curl -X POST http://localhost:8082/api/manufacturing/products \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "UNIT-2024-001",
    "productType": "PLASMA_APHERESIS",
    "productDescription": "Apheresis Plasma Product",
    "productFamily": "PLASMA",
    "completionStage": "COMPLETE",
    "weight": {"value": 250.5, "unit": "GRAMS"},
    "volume": {"value": 600.0, "unit": "ML"},
    "anticoagulantVolume": {"value": 63.0, "unit": "ML"},
    "drawTimeZone": "America/Chicago",
    "donationType": "APHERESIS",
    "procedureType": "AUTOMATED",
    "collectionLocation": "CENTER-001",
    "manufacturingLocation": "FACILITY-002",
    "aboRh": "O_POS",
    "performedBy": "TECH-123",
    "occurredOnTimeZone": "America/Chicago",
    "createDateTimeZone": "UTC",
    "collectionTimeZone": "America/Chicago",
    "bagType": "TRIPLE_BAG",
    "autoConverted": false,
    "inputProducts": [],
    "additionalSteps": []
  }'
```

**Orders Event (v2.0)**:
```bash
curl -X POST http://localhost:8083/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-2024-001",
    "bloodType": "O_POS",
    "quantity": 2,
    "priority": "URGENT",
    "facilityId": "HOSP-123",
    "requestedBy": "DR-456",
    "orderStatus": "NEW",
    "orderSource": "WEB",
    "requestedDeliveryDate": 1704153600000,
    "emergencyContact": {
      "name": "Jane Doe",
      "phone": "+1-555-0123",
      "relationship": "SPOUSE"
    }
  }'
```

**Collections Event**:
```bash
curl -X POST http://localhost:8084/api/collections \
  -H "Content-Type: application/json" \
  -d '{
    "unitNumber": "UNIT-COL-2024-001",
    "donationType": "WHOLE_BLOOD",
    "status": "COLLECTED",
    "bagType": "SINGLE_BAG",
    "procedureType": "MANUAL",
    "collectionLocation": "CENTER-001",
    "aboRh": "A_POS",
    "drawTimeZone": "America/Chicago",
    "withdrawalTimeZone": "America/Chicago",
    "machineSerialNumber": "MACH-789",
    "machineType": "APHERESIS_DEVICE",
    "volumes": [
      {
        "type": "WHOLE_BLOOD",
        "amount": 450.0,
        "excludeInCalculation": false
      }
    ]
  }'
```

---

## Using Your Avro-from-JSON Tool

### Option 1: Convert JSON Examples to Avro

If your tool converts JSON payloads to Avro schemas, use the JSON examples above.

### Option 2: Extract from Existing Avro

Your existing `.avsc` files are already valid Avro schemas. Your tool might:

1. **Read the .avsc file** (it's JSON format)
2. **Generate example JSON** from the Avro schema
3. **Validate JSON** against the schema

### Recommended Workflow

```bash
# 1. Use existing Avro schema as input
cat biopro-common-integration/src/main/resources/avro/OrderCreatedEvent.avsc

# 2. Or use JSON examples from this document to generate/validate Avro
```

---

## Summary Table

| Event Name | REST Endpoint | Kafka Topic | Schema File | Has Envelope? | Version |
|------------|---------------|-------------|-------------|---------------|---------|
| ApheresisPlasmaProductCreated | `:8082/api/manufacturing/products` | `biopro.manufacturing.events` | `ApheresisPlasmaProductCreatedEvent.avsc` | ✅ Yes | 1.0 |
| OrderCreated | `:8083/api/orders` | `biopro.orders.events` | `OrderCreatedEvent.avsc` | ✅ Yes | 1.0, 2.0 |
| CollectionReceived | `:8084/api/collections` | `biopro.collections.events` | `CollectionReceivedEvent.avsc` | ❌ No | 1.0 |

---

## Key Findings for Your Avro Tool

1. **No standalone JSON schemas exist** - only Avro schemas (.avsc files)
2. **Avro schemas ARE JSON format** - you can read them directly
3. **JSON examples above** match the REST API request formats
4. **Event envelopes** wrap the actual payload (except CollectionReceived)
5. **Schema Registry subjects** use `-value` suffix

### If You Want Pure JSON Schema

You would need to:

1. **Extract from Avro**: Use a tool like `avro-tools` to convert `.avsc` → JSON Schema
   ```bash
   # Example (if you install avro-tools)
   java -jar avro-tools.jar tojson OrderCreatedEvent.avsc
   ```

2. **Or use the JSON examples** in this document directly with your tool

---

**Generated for BioPro Event Governance POC**
*Schema inventory extracted from actual Spring Boot services*
