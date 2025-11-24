# SpringWolf Integration Guide for BioPro Manufacturing Service

## Table of Contents
1. [What is SpringWolf?](#what-is-springwolf)
2. [Why SpringWolf for BioPro?](#why-springwolf-for-biopro)
3. [How SpringWolf Works](#how-springwolf-works)
4. [BioPro Manufacturing Service Integration](#biopro-manufacturing-service-integration)
5. [Implementation Steps](#implementation-steps)
6. [Generated AsyncAPI Documentation](#generated-asyncapi-documentation)
7. [Integration with EventCatalog](#integration-with-eventcatalog)

## What is SpringWolf?

SpringWolf is an **automated AsyncAPI documentation generator** for Spring Boot applications. It's the event-driven equivalent of Springdoc/Swagger for REST APIs.

### Key Features
- **Automatic Discovery**: Scans your Spring Boot application for Kafka listeners and producers
- **AsyncAPI Specification**: Generates standard AsyncAPI 2.x/3.x documentation
- **Web UI**: Provides an interactive documentation interface (similar to Swagger UI)
- **Schema Integration**: Works with Avro, JSON Schema, and other formats
- **Zero Configuration**: Works out-of-the-box with minimal setup
- **Real-time Updates**: Documentation updates automatically with code changes

## Why SpringWolf for BioPro?

### Current State
Your BioPro manufacturing service currently:
- ✅ Uses Kafka for event-driven communication
- ✅ Implements Avro schemas via Confluent Schema Registry
- ✅ Publishes `ApheresisPlasmaProductCreatedEvent` events
- ✅ Has comprehensive schema validation

### Gaps SpringWolf Fills
- ❌ **No runtime documentation** of event flows
- ❌ **Manual AsyncAPI maintenance** required
- ❌ **Consumer/Producer relationships** not visible
- ❌ **Event payload examples** not easily accessible
- ❌ **No interactive testing interface** for events

### Benefits of Adding SpringWolf
1. **Automatic Documentation**: Zero-effort AsyncAPI generation from code
2. **Developer Experience**: Interactive UI to explore events and schemas
3. **Governance**: Runtime documentation ensures docs match reality
4. **Testing**: Built-in publisher UI for event testing
5. **Integration**: Seamless connection to EventCatalog and monitoring tools

## How SpringWolf Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   BioPro Manufacturing Service               │
│                                                              │
│  ┌──────────────────────┐    ┌─────────────────────────┐   │
│  │  @KafkaListener      │    │  KafkaTemplate          │   │
│  │  (Consumers)         │    │  (Publishers)           │   │
│  └──────────────────────┘    └─────────────────────────┘   │
│            │                            │                    │
│            │                            │                    │
│            ▼                            ▼                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           SpringWolf Auto-Scanner                     │  │
│  │  • Detects Kafka operations at startup               │  │
│  │  • Extracts topics, schemas, message types           │  │
│  │  • Generates AsyncAPI specification                  │  │
│  └──────────────────────────────────────────────────────┘  │
│            │                                                 │
│            ▼                                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           AsyncAPI Document Generator                 │  │
│  │  • Creates AsyncAPI 3.0 specification                │  │
│  │  • Integrates with Schema Registry                   │  │
│  │  • Adds Avro schema references                       │  │
│  └──────────────────────────────────────────────────────┘  │
│            │                                                 │
└────────────┼─────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    SpringWolf UI Endpoints                   │
│  • /springwolf/asyncapi.json  - AsyncAPI spec (JSON)       │
│  • /springwolf/asyncapi.yaml  - AsyncAPI spec (YAML)       │
│  • /springwolf/docs           - Interactive documentation  │
│  • /springwolf/ui             - Web UI                     │
└─────────────────────────────────────────────────────────────┘
```

### Detection Mechanism

SpringWolf uses **compile-time and runtime scanning**:

1. **Publisher Detection**
   ```java
   // SpringWolf automatically detects this
   kafkaTemplate.send(MANUFACTURING_TOPIC, eventId, avroRecord)
   ```
   - Scans for `KafkaTemplate.send()` calls
   - Extracts topic names
   - Infers message schemas from generic types

2. **Consumer Detection** (when present)
   ```java
   // Would be automatically detected
   @KafkaListener(topics = "biopro.collections.events")
   public void handleCollectionEvent(GenericRecord record) { }
   ```
   - Finds all `@KafkaListener` annotations
   - Extracts topic subscriptions
   - Documents consumer groups and message handlers

3. **Schema Integration**
   - Detects Avro serializers/deserializers
   - Connects to Schema Registry (your existing setup)
   - Embeds schema definitions in AsyncAPI spec

## BioPro Manufacturing Service Integration

### Current Event Flow

Your manufacturing service publishes events via `ManufacturingEventPublisher`:

```java
@Service
public class ManufacturingEventPublisher {

    private static final String MANUFACTURING_TOPIC = "biopro.manufacturing.events";
    private static final String MANUFACTURING_SUBJECT = "ApheresisPlasmaProductCreatedEvent";

    public void publishProductCreated(ProductCreatedRequest request) {
        // 1. Build event payload
        Map<String, Object> event = buildProductEvent(eventId, request);

        // 2. Validate against Schema Registry
        SchemaRegistryService.ValidationResult validation =
            schemaRegistryService.validateEvent("ApheresisPlasmaProductCreatedEvent", event);

        // 3. Convert to Avro GenericRecord
        GenericRecord avroRecord = convertToGenericRecord(event);

        // 4. Publish to Kafka
        kafkaTemplate.send(MANUFACTURING_TOPIC, eventId, avroRecord);
    }
}
```

### What SpringWolf Will Document

For the above code, SpringWolf will automatically generate:

1. **Channel (Topic) Information**
   - Topic name: `biopro.manufacturing.events`
   - Message type: `ApheresisPlasmaProductCreatedEvent`
   - Schema format: Avro
   - Schema Registry reference

2. **Message Schema**
   ```yaml
   ApheresisPlasmaProductCreatedEvent:
     type: object
     properties:
       eventId:
         type: string
         format: uuid
       occurredOn:
         type: integer
         format: int64
       eventType:
         type: string
         const: "ApheresisPlasmaProductCreated"
       payload:
         $ref: "#/components/schemas/ApheresisPlasmaProductPayload"
   ```

3. **Operation Details**
   - Operation type: `publish`
   - Triggered by: REST endpoint `/api/manufacturing/products`
   - Schema validation: Yes (via Schema Registry)
   - DLQ handling: Yes

4. **REST to Event Mapping**
   - HTTP POST → Kafka Event flow visualization
   - Request/Response/Event correlation

## Implementation Steps

### Step 1: Add SpringWolf Dependencies

Add to `biopro-demo-manufacturing/pom.xml`:

```xml
<dependencies>
    <!-- SpringWolf Core -->
    <dependency>
        <groupId>io.github.springwolf</groupId>
        <artifactId>springwolf-kafka</artifactId>
        <version>1.0.0</version>
    </dependency>

    <!-- SpringWolf UI -->
    <dependency>
        <groupId>io.github.springwolf</groupId>
        <artifactId>springwolf-ui</artifactId>
        <version>1.0.0</version>
    </dependency>

    <!-- Avro Plugin (for Schema Registry integration) -->
    <dependency>
        <groupId>io.github.springwolf</groupId>
        <artifactId>springwolf-add-ons-cloudstream-avro</artifactId>
        <version>1.0.0</version>
    </dependency>
</dependencies>
```

### Step 2: Configure SpringWolf

Add to `application.yml`:

```yaml
springwolf:
  enabled: true
  docket:
    info:
      title: "BioPro Manufacturing Service - Event API"
      version: "1.0.0"
      description: |
        Manufacturing service for BioPro platform.
        Publishes plasma product creation events.
      contact:
        name: "BioPro Platform Team"
        email: "platform@biopro.com"
    servers:
      manufacturing-kafka:
        protocol: kafka
        url: "redpanda:9092"
        description: "BioPro Kafka/Redpanda Cluster"

  kafka:
    publishing:
      enabled: true
      producer:
        bootstrap-servers: "redpanda:9092"

  scanner:
    kafka-listener:
      enabled: true
    async-producer:
      enabled: true

  # Schema Registry integration
  payload:
    extractors:
      avro:
        enabled: true
        schema-registry-url: "http://schema-registry:8081"
```

### Step 3: Annotate Publishers (Optional Enhancement)

While SpringWolf auto-detects Kafka operations, you can add annotations for richer documentation:

```java
@Service
@AsyncApi(
    id = "manufacturing-service",
    title = "Manufacturing Service Events"
)
public class ManufacturingEventPublisher {

    @AsyncPublisher(
        operation = @AsyncOperation(
            channelName = "biopro.manufacturing.events",
            description = "Published when a new apheresis plasma product is created"
        )
    )
    public void publishProductCreated(ProductCreatedRequest request) {
        // existing code...
    }
}
```

### Step 4: Add Schema Descriptions

Enhance your Avro schemas with documentation:

```json
{
  "type": "record",
  "name": "ApheresisPlasmaProductCreatedEvent",
  "namespace": "com.biopro.events.manufacturing",
  "doc": "Published when a new apheresis plasma product completes manufacturing",
  "fields": [
    {
      "name": "eventId",
      "type": "string",
      "doc": "Unique identifier for this event instance"
    },
    {
      "name": "payload",
      "type": {
        "type": "record",
        "name": "ApheresisPlasmaProductPayload",
        "doc": "Product details and manufacturing metadata",
        "fields": [
          {
            "name": "unitNumber",
            "type": "string",
            "doc": "Unique product/unit identifier"
          }
          // ... other fields
        ]
      }
    }
  ]
}
```

### Step 5: Access Documentation

After starting the service:

1. **AsyncAPI Specification**: `http://localhost:8082/springwolf/asyncapi.json`
2. **Interactive UI**: `http://localhost:8082/springwolf/docs`
3. **Swagger-like Interface**: `http://localhost:8082/springwolf/ui`

## Generated AsyncAPI Documentation

### Example Output

SpringWolf will generate an AsyncAPI specification like this:

```yaml
asyncapi: 3.0.0
info:
  title: BioPro Manufacturing Service - Event API
  version: 1.0.0
  description: Manufacturing service for BioPro platform

servers:
  manufacturing-kafka:
    host: redpanda:9092
    protocol: kafka
    description: BioPro Kafka/Redpanda Cluster

channels:
  biopro.manufacturing.events:
    address: biopro.manufacturing.events
    messages:
      ApheresisPlasmaProductCreatedEvent:
        $ref: '#/components/messages/ApheresisPlasmaProductCreatedEvent'
    description: Manufacturing events stream
    bindings:
      kafka:
        topic: biopro.manufacturing.events
        partitions: 3
        replicas: 1

operations:
  publishProductCreated:
    action: send
    channel:
      $ref: '#/channels/biopro.manufacturing.events'
    messages:
      - $ref: '#/components/messages/ApheresisPlasmaProductCreatedEvent'
    description: Publishes event when plasma product is manufactured
    bindings:
      kafka:
        groupId: manufacturing-service

components:
  messages:
    ApheresisPlasmaProductCreatedEvent:
      name: ApheresisPlasmaProductCreatedEvent
      title: Apheresis Plasma Product Created
      contentType: application/avro
      payload:
        schemaFormat: application/vnd.apache.avro+json;version=1.9.0
        schema:
          $ref: 'http://schema-registry:8081/subjects/ApheresisPlasmaProductCreatedEvent/versions/latest'
```

### Interactive UI Features

The SpringWolf UI provides:

1. **Channel Browser**: Visual representation of all topics
2. **Message Explorer**: View message schemas with examples
3. **Publisher Tool**: Send test messages directly from UI
4. **Schema Viewer**: Render Avro schemas in human-readable format
5. **Operation Flow**: Visualize publish/subscribe patterns

## Integration with EventCatalog

### Automated AsyncAPI Import

EventCatalog can automatically import SpringWolf's AsyncAPI specs:

#### 1. Update EventCatalog Configuration

Add to `eventcatalog/eventcatalog.config.js`:

```javascript
export default {
  generators: [
    [
      '@eventcatalog/generator-asyncapi',
      {
        services: [
          {
            path: 'http://localhost:8082/springwolf/asyncapi.json',
            id: 'manufacturing-service',
          },
        ],
        domain: 'manufacturing',
      },
    ],
  ],
};
```

#### 2. Run Sync

```bash
cd eventcatalog
npm run generate
```

This will:
- Fetch AsyncAPI spec from SpringWolf
- Generate EventCatalog documentation
- Create service/event mappings
- Link schemas to events

### Complete Documentation Pipeline

```
┌─────────────────────┐
│  Manufacturing      │
│  Service (Spring)   │
│                     │
│  ┌───────────────┐ │
│  │  SpringWolf   │ │  Auto-generates
│  │  Scanner      │ │  ↓
│  └───────┬───────┘ │
│          │         │
│          ▼         │
│  ┌───────────────┐ │
│  │  AsyncAPI     │ │
│  │  /springwolf/ │ │
│  │  asyncapi.json│ │
│  └───────┬───────┘ │
└──────────┼─────────┘
           │
           │ HTTP
           ▼
┌─────────────────────┐
│  EventCatalog       │
│                     │
│  ┌───────────────┐ │
│  │  AsyncAPI     │ │  Imports
│  │  Generator    │ │  ↓
│  └───────┬───────┘ │
│          │         │
│          ▼         │
│  ┌───────────────┐ │
│  │  Service      │ │
│  │  Events       │ │
│  │  Schemas      │ │
│  └───────────────┘ │
└─────────────────────┘
```

### Benefits of Integration

1. **Single Source of Truth**: Code → AsyncAPI → EventCatalog
2. **Always Up-to-Date**: Runtime documentation ensures accuracy
3. **Developer-Friendly**: Interactive tools for exploration
4. **Governance-Ready**: Automated compliance with event standards
5. **Monitoring Integration**: Link to Prometheus metrics

## Comparison: Current vs With SpringWolf

| Aspect | Current State | With SpringWolf |
|--------|--------------|-----------------|
| **Event Documentation** | Manual in EventCatalog | Auto-generated from code |
| **Schema Visibility** | Schema Registry UI only | Interactive AsyncAPI UI |
| **Testing** | Manual Kafka publishing | Built-in publisher UI |
| **API Discovery** | Code inspection | Runtime documentation |
| **Event Examples** | Manually created | Auto-extracted from code |
| **REST→Event Mapping** | Not documented | Automatically linked |
| **Maintenance** | Manual updates required | Zero-effort updates |

## Next Steps

1. **Pilot Integration**: Add SpringWolf to manufacturing service
2. **Validate Output**: Review generated AsyncAPI documentation
3. **Connect EventCatalog**: Set up automated import pipeline
4. **Extend to Other Services**: Add to Orders and Collections services
5. **Monitor Usage**: Track API documentation access

## Additional Resources

- [SpringWolf Documentation](https://www.springwolf.dev/)
- [AsyncAPI Specification](https://www.asyncapi.com/)
- [EventCatalog AsyncAPI Generator](https://www.eventcatalog.dev/docs/api/plugins/@eventcatalog/generator-asyncapi)

---

**Generated for BioPro Event Governance POC**
*Demonstrating runtime event documentation with SpringWolf*
