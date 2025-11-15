# BioPro Event Schemas

This directory contains Avro schemas for all BioPro events, organized by module and version.

## Directory Structure

```
schemas/
├── orders/
│   └── v1.0/
│       └── OrderCreatedEvent.avsc
├── collections/
│   └── v1.0/
│       └── CollectionReceivedEvent.avsc
└── manufacturing/
    └── v1.0/
        └── ApheresisPlasmaProductCreatedEvent.avsc
```

## Schema Organization

Schemas are organized using the following convention:

```
schemas/{module}/{version}/{EventName}.avsc
```

- **module**: The domain module (orders, collections, manufacturing)
- **version**: Semantic version (v1.0, v1.1, v2.0, etc.)
- **EventName**: The Avro schema name matching the event type

## Schema Versioning

- All schemas follow semantic versioning: vMAJOR.MINOR
- Breaking changes require a new MAJOR version
- Backward-compatible changes increment MINOR version
- Schemas are registered in Confluent Schema Registry

## Current Schemas

### Orders Module (v1.0)

**OrderCreatedEvent** - Published when a blood product order is created

- Subject: `OrderCreatedEvent`
- Namespace: `com.biopro.events.orders`
- Topic: `biopro.orders.events`
- Schema Registry ID: 2

### Collections Module (v1.0)

**CollectionReceivedEvent** - Published when a blood collection is received

- Subject: `CollectionReceivedEvent`
- Namespace: `com.biopro.events.collections`
- Topic: `biopro.collections.events`
- Schema Registry ID: 3

### Manufacturing Module (v1.0)

**ApheresisPlasmaProductCreatedEvent** - Published when an apheresis plasma product is manufactured

- Subject: `ApheresisPlasmaProductCreatedEvent`
- Namespace: `com.biopro.events.manufacturing`
- Topic: `biopro.manufacturing.events`
- Schema Registry ID: 4

## Schema Registry Integration

All schemas are registered with the Confluent Schema Registry at `http://localhost:8081`.

To view schemas in the registry:

```bash
# List all subjects
curl http://localhost:8081/subjects

# Get latest version of a schema
curl http://localhost:8081/subjects/OrderCreatedEvent/versions/latest

# Get schema by ID
curl http://localhost:8081/schemas/ids/2
```

## Updating Schemas

When updating schemas:

1. Create a new version directory (e.g., `v1.1/`)
2. Add the updated schema file
3. Test for backward compatibility
4. Register the new version in Schema Registry
5. Update the application code to use the new schema

## Schema Evolution Guidelines

- **Backward Compatible Changes** (same major version):
  - Adding optional fields (with defaults)
  - Adding new event types
  - Removing optional fields

- **Breaking Changes** (new major version required):
  - Removing required fields
  - Changing field types
  - Renaming fields
  - Changing field nullability from nullable to required

## Tools

### Download Current Schemas from Registry

```bash
# Download all schemas
python -c "
import json
import requests

schemas = ['OrderCreatedEvent', 'CollectionReceivedEvent', 'ApheresisPlasmaProductCreatedEvent']
modules = {'OrderCreatedEvent': 'orders', 'CollectionReceivedEvent': 'collections', 'ApheresisPlasmaProductCreatedEvent': 'manufacturing'}

for schema_name in schemas:
    resp = requests.get(f'http://localhost:8081/subjects/{schema_name}/versions/latest')
    data = resp.json()
    schema = json.loads(data['schema'])
    module = modules[schema_name]
    version = data['version']
    
    with open(f'schemas/{module}/v1.0/{schema_name}.avsc', 'w') as f:
        json.dump(schema, f, indent=2)
    print(f'Downloaded {schema_name} v{version}')
"
```

### Validate Schema

```bash
# Validate schema using avro-tools
java -jar avro-tools.jar compile schema schemas/orders/v1.0/OrderCreatedEvent.avsc /tmp

# Or validate with Python
python -c "
import json
from avro.schema import parse

with open('schemas/orders/v1.0/OrderCreatedEvent.avsc') as f:
    schema = parse(f.read())
print('Schema is valid')
"
```

### Check Schema Compatibility

```bash
# Test compatibility with Schema Registry
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data @schemas/orders/v1.1/OrderCreatedEvent.avsc \
  http://localhost:8081/compatibility/subjects/OrderCreatedEvent/versions/latest
```

## References

- [Apache Avro Documentation](https://avro.apache.org/docs/current/)
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html)
- [Schema Evolution Best Practices](https://docs.confluent.io/platform/current/schema-registry/avro.html)
