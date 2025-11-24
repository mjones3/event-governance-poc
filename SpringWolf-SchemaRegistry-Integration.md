# SpringWolf & Schema Registry Integration Guide

## Important: Understanding the Flow

**SpringWolf does NOT import schemas INTO Schema Registry**. Instead:

```
┌─────────────────────────────────────────────────────────────┐
│                   Actual Flow                                │
└─────────────────────────────────────────────────────────────┘

   Avro Schema Files (.avsc)
            ↓
   Schema Registry (registration)
            ↓
   Spring Boot Service (uses schemas)
            ↓
   SpringWolf (documents what exists)
            ↓
   AsyncAPI Spec (references schemas)
```

**SpringWolf is a documentation tool** - it reads and documents schemas that are already in Schema Registry.

## Current BioPro Setup (Already Correct!)

Your BioPro services already register schemas correctly:

### 1. Schema Files
Located in `schemas/avro/`:
```
schemas/avro/
├── ApheresisPlasmaProductCreatedEvent.avsc
├── CollectionReceivedEvent.avsc
└── OrderCreatedEvent.avsc
```

### 2. Schema Registration
Your `SchemaRegistryService` handles registration:

```java
public void registerSchema(String subject, String schemaPath) {
    Schema schema = new Schema.Parser().parse(new File(schemaPath));
    schemaRegistryClient.register(subject, new AvroSchema(schema));
}
```

### 3. Spring Boot Startup
Schemas are registered when services start:

```java
@PostConstruct
public void registerSchemas() {
    registerSchema("ApheresisPlasmaProductCreatedEvent",
                   "schemas/avro/ApheresisPlasmaProductCreatedEvent.avsc");
}
```

### 4. SpringWolf Documentation
SpringWolf reads these registered schemas and generates AsyncAPI docs.

## What You Probably Want: Complete Schema Management

If you want SpringWolf to be aware of ALL your Avro schemas, here's the complete workflow:

## Option 1: Use Your Current Setup (Recommended)

### Current State ✅
You already have:
1. Avro schema files in `schemas/avro/`
2. Schema registration on service startup
3. Schema Registry at http://localhost:8081

### Add SpringWolf Documentation

**Step 1**: Configure SpringWolf to read from Schema Registry

```yaml
# application.yml
springwolf:
  enabled: true
  docket:
    info:
      title: "BioPro Event Platform"
      version: "1.0.0"

  # Point to your Schema Registry
  payload:
    extractors:
      avro:
        enabled: true
        schema-registry-url: "http://schema-registry:8081"
        # SpringWolf will fetch schemas from here
```

**Step 2**: SpringWolf Auto-Discovery

SpringWolf will automatically:
1. Detect your `@KafkaListener` and `KafkaTemplate.send()` calls
2. Extract topic names and message types
3. Query Schema Registry for the Avro schemas
4. Generate AsyncAPI documentation with schema references

### Example: What Gets Generated

For your manufacturing service:

```yaml
# Generated AsyncAPI
components:
  messages:
    ApheresisPlasmaProductCreatedEvent:
      contentType: application/avro
      payload:
        schemaFormat: application/vnd.apache.avro+json;version=1.9.0
        schema:
          # Direct reference to your Schema Registry
          $ref: 'http://schema-registry:8081/subjects/ApheresisPlasmaProductCreatedEvent-value/versions/latest'
```

## Option 2: Schema-First with Maven Plugin

If you want automated schema registration during build:

### Step 1: Add Schema Registry Maven Plugin

```xml
<!-- pom.xml -->
<plugin>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-schema-registry-maven-plugin</artifactId>
    <version>7.5.3</version>
    <configuration>
        <schemaRegistryUrls>
            <param>http://localhost:8081</param>
        </schemaRegistryUrls>
        <subjects>
            <ApheresisPlasmaProductCreatedEvent-value>
                src/main/avro/ApheresisPlasmaProductCreatedEvent.avsc
            </ApheresisPlasmaProductCreatedEvent-value>
            <CollectionReceivedEvent-value>
                src/main/avro/CollectionReceivedEvent.avsc
            </CollectionReceivedEvent-value>
        </subjects>
    </configuration>
    <executions>
        <execution>
            <phase>compile</phase>
            <goals>
                <goal>register</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

### Step 2: Build Process Registers Schemas

```bash
mvn clean compile
# Automatically registers all schemas to Schema Registry
```

### Step 3: SpringWolf Documents Them

SpringWolf will then discover and document all registered schemas.

## Option 3: Central Schema Repository

For multi-service schema sharing:

### Structure

```
event-governance/
├── schemas/
│   └── avro/
│       ├── ApheresisPlasmaProductCreatedEvent.avsc
│       ├── CollectionReceivedEvent.avsc
│       └── OrderCreatedEvent.avsc
├── schema-registration-tool/
│   ├── register-all-schemas.sh
│   └── SchemaRegistryBulkLoader.java
└── services/
    ├── manufacturing-service/
    ├── orders-service/
    └── collections-service/
```

### Bulk Registration Script

Create `schema-registration-tool/register-all-schemas.sh`:

```bash
#!/bin/bash

SCHEMA_REGISTRY_URL="http://localhost:8081"
SCHEMAS_DIR="../schemas/avro"

for schema_file in $SCHEMAS_DIR/*.avsc; do
    schema_name=$(basename "$schema_file" .avsc)
    subject="${schema_name}-value"

    echo "Registering $subject..."

    # Read schema file and register
    schema_content=$(cat "$schema_file" | jq -c '.')

    curl -X POST \
        -H "Content-Type: application/vnd.schemaregistry.v1+json" \
        --data "{\"schema\": \"$schema_content\"}" \
        "${SCHEMA_REGISTRY_URL}/subjects/${subject}/versions"

    echo "✓ Registered $subject"
done

echo "All schemas registered!"
```

### Run Registration

```bash
cd schema-registration-tool
chmod +x register-all-schemas.sh
./register-all-schemas.sh
```

## How SpringWolf Discovers Schemas

### Automatic Detection

SpringWolf scans your code for:

1. **Kafka Producers** (what you have now)
```java
kafkaTemplate.send(MANUFACTURING_TOPIC, eventId, avroRecord)
//                 ↑                              ↑
//                 Topic Name                Avro Type
```

SpringWolf extracts:
- Topic: `biopro.manufacturing.events`
- Infers: Schema subject should be `ApheresisPlasmaProductCreatedEvent-value`
- Queries Schema Registry: `http://schema-registry:8081/subjects/ApheresisPlasmaProductCreatedEvent-value/versions/latest`

2. **Kafka Consumers** (if you add listeners)
```java
@KafkaListener(topics = "biopro.collections.events")
public void handleCollection(GenericRecord record) {
    // SpringWolf detects this and documents the consumer
}
```

### Manual Schema Binding (Optional)

If SpringWolf can't auto-detect, add annotations:

```java
@AsyncPublisher(
    operation = @AsyncOperation(
        channelName = "biopro.manufacturing.events",
        message = @AsyncMessage(
            name = "ApheresisPlasmaProductCreatedEvent",
            contentType = "application/avro",
            schemaFormat = "application/vnd.apache.avro+json;version=1.9.0"
        )
    )
)
public void publishProductCreated(ProductCreatedRequest request) {
    // ...
}
```

## Verifying the Integration

### 1. Check Schema Registry

```bash
# List all subjects
curl http://localhost:8081/subjects

# Get specific schema
curl http://localhost:8081/subjects/ApheresisPlasmaProductCreatedEvent-value/versions/latest
```

### 2. Check SpringWolf AsyncAPI

```bash
# Get AsyncAPI spec
curl http://localhost:8082/springwolf/asyncapi.json | jq '.components.schemas'
```

Should show:

```json
{
  "components": {
    "schemas": {
      "ApheresisPlasmaProductCreatedEvent": {
        "$ref": "http://schema-registry:8081/subjects/ApheresisPlasmaProductCreatedEvent-value/versions/latest"
      }
    }
  }
}
```

### 3. Check SpringWolf UI

Open http://localhost:8082/springwolf/docs and verify:
- All topics are listed
- Schemas are linked
- Avro schemas are displayed

## Complete Configuration Example

### application.yml

```yaml
spring:
  kafka:
    bootstrap-servers: redpanda:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: io.confluent.kafka.serializers.KafkaAvroSerializer
    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: io.confluent.kafka.serializers.KafkaAvroDeserializer
    properties:
      schema.registry.url: http://schema-registry:8081

springwolf:
  enabled: true
  docket:
    info:
      title: "BioPro Manufacturing Service"
      version: "1.0.0"
    servers:
      biopro-kafka:
        protocol: kafka
        url: "redpanda:9092"

  kafka:
    publishing:
      enabled: true

  payload:
    extractors:
      avro:
        enabled: true
        # Must match your Spring Kafka schema.registry.url
        schema-registry-url: "http://schema-registry:8081"

  scanner:
    async-publisher:
      enabled: true
    async-listener:
      enabled: true
```

## Best Practices

### 1. Schema Naming Convention

Use consistent subject naming:
```
{EventName}-value    # For event values
{EventName}-key      # For event keys (if needed)
```

### 2. Schema Versioning

Register new versions properly:
```bash
# Version 1
curl -X POST http://localhost:8081/subjects/MyEvent-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "{...}"}'

# Version 2 (backward compatible)
curl -X POST http://localhost:8081/subjects/MyEvent-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "{...}"}'
```

### 3. Development Workflow

```
1. Create/Update Avro Schema (.avsc file)
      ↓
2. Register to Schema Registry (manual or automated)
      ↓
3. Run SpringWolf-enabled service
      ↓
4. Verify in SpringWolf UI
      ↓
5. Sync to EventCatalog (optional)
```

## Troubleshooting

### SpringWolf Not Finding Schemas

**Problem**: AsyncAPI shows schema as empty object

**Solution**: Verify Schema Registry connection
```bash
# From Spring Boot container
curl http://schema-registry:8081/subjects
```

### Schema Registry Subject Not Found

**Problem**: 404 when SpringWolf queries Schema Registry

**Solution**: Ensure subject naming matches
```java
// If your code uses this subject name:
String subject = "ApheresisPlasmaProductCreatedEvent";

// Schema Registry needs this exact name registered
// Check with:
curl http://localhost:8081/subjects | grep ApheresisPlasmaProductCreatedEvent
```

### Multiple Schema Versions

**Problem**: SpringWolf shows old schema version

**Solution**: Configure version selection
```yaml
springwolf:
  payload:
    extractors:
      avro:
        use-latest-version: true  # Always use latest
```

## Summary: Your Action Items

For your BioPro setup, you should:

### ✅ Already Done
1. Avro schemas defined in `schemas/avro/`
2. Schema Registry running on port 8081
3. Services register schemas on startup

### 🔧 To Add SpringWolf
1. Add SpringWolf dependencies to `pom.xml`
2. Configure SpringWolf in `application.yml` (point to Schema Registry)
3. Restart services
4. Access http://localhost:8082/springwolf/docs

### 📚 Optional Enhancements
1. Add Maven plugin for automated schema registration
2. Create bulk schema loading script
3. Add SpringWolf annotations for richer documentation
4. Integrate with EventCatalog generator

## Key Takeaway

**SpringWolf + Schema Registry Flow:**

```
You Write:        Avro Schema Files
You Register:     Schemas to Schema Registry (via code or plugin)
SpringWolf Reads: Registered schemas from Schema Registry
SpringWolf Docs:  AsyncAPI with schema references
EventCatalog:     Imports AsyncAPI from SpringWolf
```

SpringWolf is the **documentation layer**, not the schema registration layer!

---

**Need Help?**
- Schema Registration: See `Schema-Management-Guide.md`
- SpringWolf Setup: See `SpringWolf-Quick-Start.md`
- Complete Integration: See `SpringWolf-Integration-Guide.md`
