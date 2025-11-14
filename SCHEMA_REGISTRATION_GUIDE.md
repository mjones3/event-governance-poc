# Schema Registry - Registration and Management Guide

Complete guide for registering and managing Avro schemas in Confluent Schema Registry.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Schema Registration Methods](#schema-registration-methods)
- [Manual Registration](#manual-registration)
- [Automatic Registration](#automatic-registration)
- [Schema Evolution](#schema-evolution)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The BioPro Event Governance Framework uses Confluent Schema Registry to:
- **Validate events** against registered schemas before publishing
- **Ensure compatibility** across schema versions
- **Enable schema evolution** without breaking consumers
- **Provide centralized schema management**

### Real BioPro Schemas

The POC includes **production-ready schemas** extracted from actual BioPro services:

**Collections Service**:
- `CollectionReceivedEvent.avsc` - Blood collection received events
- `CollectionUpdatedEvent.avsc` - Blood collection updates

**Orders Service**:
- `OrderCreatedEvent.avsc` - New blood product orders

**Manufacturing Service**:
- `ApheresisPlasmaProductCreatedEvent.avsc` - Manufactured plasma products

All schemas are located in: `biopro-common-integration/src/main/resources/avro/`

---

## Prerequisites

1. **Schema Registry Running**
   ```bash
   # Via Docker Compose
   docker-compose up -d schema-registry

   # Via Kubernetes/Tilt
   tilt up
   ```

2. **Verify Schema Registry**
   ```bash
   curl http://localhost:8081/subjects
   ```
   Should return `[]` initially.

---

## Schema Registration Methods

### Method 1: Manual Registration via REST API

**Step 1: Prepare the Schema**

Read your Avro schema file:
```bash
cat biopro-common-integration/src/main/resources/avro/CollectionReceivedEvent.avsc
```

**Step 2: Register the Schema**

```bash
# Collections Received Event
curl -X POST http://localhost:8081/subjects/collections-received-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @- <<EOF
{
  "schemaType": "AVRO",
  "schema": $(cat biopro-common-integration/src/main/resources/avro/CollectionReceivedEvent.avsc | jq -Rs .)
}
EOF
```

**Step 3: Verify Registration**

```bash
# List all subjects
curl http://localhost:8081/subjects

# Get schema for subject
curl http://localhost:8081/subjects/collections-received-value/versions/latest
```

---

### Method 2: Register All Schemas via Script

Create a registration script:

```bash
#!/bin/bash
# register-schemas.sh

SCHEMA_REGISTRY_URL="http://localhost:8081"
SCHEMA_DIR="biopro-common-integration/src/main/resources/avro"

# Function to register a schema
register_schema() {
  local schema_file=$1
  local subject=$2

  echo "Registering $schema_file as $subject..."

  curl -X POST ${SCHEMA_REGISTRY_URL}/subjects/${subject}/versions \
    -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    -d "{\"schemaType\":\"AVRO\",\"schema\":$(cat ${schema_file} | jq -Rs .)}"

  echo ""
}

# Register Collections schemas
register_schema "${SCHEMA_DIR}/CollectionReceivedEvent.avsc" "collections-received-value"
register_schema "${SCHEMA_DIR}/CollectionUpdatedEvent.avsc" "collections-updated-value"

# Register Orders schemas
register_schema "${SCHEMA_DIR}/OrderCreatedEvent.avsc" "orders-created-value"

# Register Manufacturing schemas
register_schema "${SCHEMA_DIR}/ApheresisPlasmaProductCreatedEvent.avsc" "manufacturing-apheresis-plasma-product-created-value"

echo "✅ All schemas registered!"
```

Run the script:
```bash
chmod +x register-schemas.sh
./register-schemas.sh
```

---

### Method 3: Automatic Registration (Recommended for Production)

The BioPro DLQ Framework automatically registers schemas when:
1. Application starts
2. Schema doesn't exist in registry
3. `spring.kafka.properties.schema.registry.url` is configured

**Configuration**:

```yaml
spring:
  kafka:
    properties:
      schema.registry.url: http://localhost:8081
      auto.register.schemas: true      # Enable auto-registration
      use.latest.version: true          # Use latest schema version
      value.subject.name.strategy: io.confluent.kafka.serializers.subject.TopicNameStrategy
```

**How It Works**:

When you publish an event:
```java
@Service
public class CollectionEventPublisher {

    @Autowired
    private KafkaTemplate<String, CollectionReceivedEvent> kafkaTemplate;

    public void publishCollectionReceived(CollectionReceivedEvent event) {
        // Schema is automatically registered on first publish
        kafkaTemplate.send("biopro.collections.received", event);
    }
}
```

The framework:
1. Generates Avro schema from event class
2. Checks if schema exists in registry
3. Registers schema if missing
4. Validates event against schema
5. Publishes to Kafka

---

## Schema Evolution

### Compatibility Modes

Schema Registry supports different compatibility modes:

**BACKWARD** (Default) - Recommended
- New schema can read data written with old schema
- ✅ Add optional fields
- ✅ Remove fields with defaults
- ❌ Remove required fields
- ❌ Change field types

**FORWARD**
- Old schema can read data written with new schema

**FULL**
- Both backward and forward compatible

**Set Compatibility**:

```bash
# Set global compatibility
curl -X PUT http://localhost:8081/config \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"compatibility":"BACKWARD"}'

# Set compatibility for specific subject
curl -X PUT http://localhost:8081/config/collections-received-value \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"compatibility":"BACKWARD"}'
```

### Example: Evolving CollectionReceivedEvent

**Version 1** (Initial):
```json
{
  "type": "record",
  "name": "CollectionReceivedEvent",
  "fields": [
    {"name": "unitNumber", "type": "string"},
    {"name": "status", "type": "string"}
  ]
}
```

**Version 2** (Add optional field - ✅ Compatible):
```json
{
  "type": "record",
  "name": "CollectionReceivedEvent",
  "fields": [
    {"name": "unitNumber", "type": "string"},
    {"name": "status", "type": "string"},
    {"name": "collectionDate", "type": ["null", "long"], "default": null}
  ]
}
```

**Version 3** (Add field with default - ✅ Compatible):
```json
{
  "type": "record",
  "name": "CollectionReceivedEvent",
  "fields": [
    {"name": "unitNumber", "type": "string"},
    {"name": "status", "type": "string"},
    {"name": "collectionDate", "type": ["null", "long"], "default": null},
    {"name": "facilityCode", "type": "string", "default": "UNKNOWN"}
  ]
}
```

**❌ Breaking Change** (Remove required field):
```json
{
  "type": "record",
  "name": "CollectionReceivedEvent",
  "fields": [
    {"name": "unitNumber", "type": "string"}
    // ❌ Removed "status" - breaks backward compatibility!
  ]
}
```

---

## Best Practices

### 1. Subject Naming Convention

Use consistent naming:
```
{module}-{event-name}-{key|value}
```

Examples:
- `collections-received-value`
- `orders-created-value`
- `manufacturing-product-created-value`

### 2. Schema Documentation

Always include `doc` fields:
```json
{
  "type": "record",
  "name": "CollectionReceivedEvent",
  "doc": "Event published when a blood collection is received",
  "fields": [
    {
      "name": "unitNumber",
      "type": "string",
      "doc": "Unique identifier for the collection unit"
    }
  ]
}
```

### 3. Default Values for Optional Fields

Always provide defaults:
```json
{
  "name": "comments",
  "type": ["null", "string"],
  "default": null,
  "doc": "Optional comments"
}
```

### 4. Enum Evolution

Use strings instead of enums when values might change:
```json
// ❌ Avoid enums for frequently changing values
{"name": "status", "type": {"type": "enum", "symbols": ["NEW", "PENDING"]}}

// ✅ Use string with documentation
{"name": "status", "type": "string", "doc": "Valid values: NEW, PENDING, COMPLETED"}
```

### 5. Version Schema Files

Keep schema history:
```
avro/
  v1/
    CollectionReceivedEvent.avsc
  v2/
    CollectionReceivedEvent.avsc
  current/
    CollectionReceivedEvent.avsc -> ../v2/CollectionReceivedEvent.avsc
```

---

## Troubleshooting

### Schema Not Found

**Problem**: `Schema not found` error when publishing events

**Solution**:
```bash
# Check if schema exists
curl http://localhost:8081/subjects/collections-received-value/versions/latest

# If not, register manually
curl -X POST http://localhost:8081/subjects/collections-received-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @schema.json
```

### Incompatible Schema Evolution

**Problem**: `Schema being registered is incompatible with an earlier schema`

**Solution**:
1. Check compatibility mode:
   ```bash
   curl http://localhost:8081/config/collections-received-value
   ```

2. Test compatibility before registering:
   ```bash
   curl -X POST http://localhost:8081/compatibility/subjects/collections-received-value/versions/latest \
     -H "Content-Type: application/vnd.schemaregistry.v1+json" \
     -d @new-schema.json
   ```

3. If intentional breaking change, register as new subject or delete old versions (⚠️ dangerous):
   ```bash
   # Delete specific version
   curl -X DELETE http://localhost:8081/subjects/collections-received-value/versions/1

   # Soft delete subject (can be restored)
   curl -X DELETE http://localhost:8081/subjects/collections-received-value

   # Permanent delete
   curl -X DELETE http://localhost:8081/subjects/collections-received-value?permanent=true
   ```

### Schema Registry Connection Issues

**Problem**: Cannot connect to Schema Registry

**Solution**:
```bash
# Check if Schema Registry is running
docker ps | grep schema-registry

# Check logs
docker logs schema-registry

# Verify network connectivity
curl -v http://localhost:8081/subjects
```

### Avro Code Generation Issues

**Problem**: Generated Java classes don't match schema

**Solution**:
```bash
# Clean and regenerate
mvn clean compile

# Verify Avro plugin in pom.xml
# Check target/generated-sources/avro for generated classes
```

---

## Schema Registry UI (Optional)

For easier schema management, install Confluent Control Center or Landoop Schema Registry UI:

```yaml
# docker-compose.yml
schema-registry-ui:
  image: landoop/schema-registry-ui:latest
  ports:
    - "8000:8000"
  environment:
    SCHEMAREGISTRY_URL: http://schema-registry:8081
```

Access at: http://localhost:8000

---

## Quick Reference

### Common Commands

```bash
# List all subjects
curl http://localhost:8081/subjects

# Get latest schema
curl http://localhost:8081/subjects/{subject}/versions/latest

# Get specific version
curl http://localhost:8081/subjects/{subject}/versions/1

# Register new schema
curl -X POST http://localhost:8081/subjects/{subject}/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema":"{...}"}'

# Check compatibility
curl -X POST http://localhost:8081/compatibility/subjects/{subject}/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema":"{...}"}'

# Delete schema
curl -X DELETE http://localhost:8081/subjects/{subject}/versions/1
```

---

**For more details, see**:
- [Confluent Schema Registry Documentation](https://docs.confluent.io/platform/current/schema-registry/index.html)
- [Avro Schema Specification](https://avro.apache.org/docs/current/spec.html)
- Main [README.md](README.md) for overall framework documentation

---

**Document Version**: 2.0
**Last Updated**: November 4, 2025
**Author**: Event Governance Team
