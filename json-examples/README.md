# BioPro Event JSON Examples

This directory contains JSON example payloads for all BioPro events, extracted from the actual Spring Boot services.

## Files

- `manufacturing-event-example.json` - ApheresisPlasmaProductCreated event
- `order-event-v1-example.json` - OrderCreated event (v1.0)
- `order-event-v2-example.json` - OrderCreated event (v2.0 with new fields)
- `collection-event-example.json` - CollectionReceived event

## Usage with Your Avro Tool

These JSON files can be used with tools that convert JSON to Avro schemas.

### Example Workflow

```bash
# If your tool converts JSON → Avro
your-tool convert manufacturing-event-example.json > manufacturing.avsc

# Or validate JSON against existing Avro schema
your-tool validate manufacturing-event-example.json \
  --schema ../schemas/manufacturing/v1.0/ApheresisPlasmaProductCreatedEvent.avsc
```

## Corresponding Avro Schemas

Each JSON example corresponds to an existing Avro schema:

| JSON Example | Avro Schema Location |
|--------------|---------------------|
| `manufacturing-event-example.json` | `biopro-common-integration/src/main/resources/avro/ApheresisPlasmaProductCreatedEvent.avsc` |
| `order-event-v1-example.json` | `schemas/orders/v1.0/OrderCreatedEvent.avsc` |
| `order-event-v2-example.json` | `schemas/orders/v2.0/OrderCreatedEvent.avsc` |
| `collection-event-example.json` | `biopro-common-integration/src/main/resources/avro/CollectionReceivedEvent.avsc` |

## Testing Against Live Services

You can send these examples to the REST endpoints (with slight modifications):

**Manufacturing** (remove envelope, send only request payload):
```bash
curl -X POST http://localhost:8082/api/manufacturing/products \
  -H "Content-Type: application/json" \
  -d @manufacturing-rest-request.json
```

See `BioPro-Schema-Inventory.md` for REST API request formats.

## Notes

- **Event envelopes** (eventId, occurredOn, eventType, eventVersion) are added by the services
- **REST requests** only need the `payload` content (or simplified request format)
- **Kafka messages** contain the full event envelope structure shown in these examples
- **Collection events** have a flat structure (no envelope)

---

**Generated from BioPro Spring Boot Services**
*Extracted: January 2025*
