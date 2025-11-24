# SpringWolf Quick Start - BioPro Manufacturing Service

## 5-Minute Implementation Guide

### What You'll Get
After this quick start, you'll have:
- ✅ Interactive AsyncAPI documentation at `http://localhost:8082/springwolf/docs`
- ✅ Auto-generated event schema documentation
- ✅ Built-in event publisher UI for testing
- ✅ Integration-ready AsyncAPI spec for EventCatalog

### Prerequisites
- BioPro manufacturing service running
- Maven configured (already done ✓)
- Access to Schema Registry (already configured ✓)

## Step 1: Add Dependencies (2 minutes)

Add to `biopro-demo-manufacturing/pom.xml` in the `<dependencies>` section:

```xml
<!-- SpringWolf for AsyncAPI documentation -->
<dependency>
    <groupId>io.github.springwolf</groupId>
    <artifactId>springwolf-kafka</artifactId>
    <version>1.0.0</version>
</dependency>

<dependency>
    <groupId>io.github.springwolf</groupId>
    <artifactId>springwolf-ui</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Step 2: Configure SpringWolf (2 minutes)

Create `src/main/resources/application-springwolf.yml`:

```yaml
springwolf:
  enabled: true
  docket:
    info:
      title: "BioPro Manufacturing Service Events"
      version: "1.0.0"
      description: "Real-time documentation of manufacturing events"
      contact:
        name: "Platform Team"
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
        schema-registry-url: "http://schema-registry:8081"
```

## Step 3: Activate Profile (1 minute)

Update `application.yml` to include the SpringWolf profile:

```yaml
spring:
  profiles:
    active: springwolf
```

Or start with environment variable:
```bash
SPRING_PROFILES_ACTIVE=springwolf
```

## Step 4: Build and Run

```bash
cd biopro-demo-manufacturing
mvn clean package
docker-compose restart manufacturing-service
```

## Step 5: Access Documentation

Open your browser:

1. **AsyncAPI UI**: http://localhost:8082/springwolf/docs
2. **AsyncAPI Spec (JSON)**: http://localhost:8082/springwolf/asyncapi.json
3. **AsyncAPI Spec (YAML)**: http://localhost:8082/springwolf/asyncapi.yaml

## What You'll See

### Channel Documentation
```
Topic: biopro.manufacturing.events
├── Publisher: ManufacturingEventPublisher
├── Message: ApheresisPlasmaProductCreatedEvent
├── Schema: Avro (from Schema Registry)
└── Operations: PUBLISH
```

### Interactive Features

1. **Schema Browser**
   - View all event schemas
   - See field descriptions
   - Understand data types

2. **Event Publisher**
   - Test event publishing from UI
   - Auto-fill with example data
   - Validate against schema

3. **Channel Explorer**
   - See all Kafka topics
   - Understand message flow
   - View bindings and configuration

## Integration with EventCatalog

### Auto-Import to EventCatalog

Update `eventcatalog/eventcatalog.config.js`:

```javascript
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
    },
  ],
],
```

Then sync:
```bash
cd eventcatalog
npm run generate
```

## Example: Generated AsyncAPI Output

For your `ManufacturingEventPublisher.publishProductCreated()` method, SpringWolf generates:

```yaml
channels:
  biopro.manufacturing.events:
    address: biopro.manufacturing.events
    messages:
      ApheresisPlasmaProductCreatedEvent:
        contentType: application/avro
        payload:
          schemaFormat: application/vnd.apache.avro
          schema:
            $ref: 'http://schema-registry:8081/subjects/ApheresisPlasmaProductCreatedEvent/versions/latest'

operations:
  publishProductCreated:
    action: send
    channel:
      $ref: '#/channels/biopro.manufacturing.events'
    summary: "Publish Apheresis Plasma Product Created Event"
    description: "Triggered when manufacturing completes for a plasma product"
```

## Advanced: Add Custom Annotations (Optional)

Enhance documentation with annotations in `ManufacturingEventPublisher.java`:

```java
@Service
public class ManufacturingEventPublisher {

    @AsyncPublisher(
        operation = @AsyncOperation(
            channelName = "biopro.manufacturing.events",
            description = "Published when apheresis plasma product manufacturing completes",
            headers = @AsyncOperation.Headers(
                schemaName = "KafkaHeaders",
                values = {
                    @AsyncOperation.Headers.Header(
                        name = "event-type",
                        description = "Type of manufacturing event",
                        value = "ApheresisPlasmaProductCreated"
                    )
                }
            )
        ),
        message = @AsyncMessage(
            name = "ApheresisPlasmaProductCreatedEvent",
            description = "Complete manufacturing details for plasma product",
            contentType = "application/avro"
        )
    )
    public void publishProductCreated(ProductCreatedRequest request) {
        // existing implementation
    }
}
```

## Troubleshooting

### Issue: AsyncAPI endpoint returns 404
**Solution**: Ensure springwolf profile is active
```bash
docker-compose logs manufacturing-service | grep springwolf
```

### Issue: Schemas not showing
**Solution**: Verify Schema Registry connection
```yaml
springwolf:
  payload:
    extractors:
      avro:
        schema-registry-url: "http://schema-registry:8081"  # Must be accessible
```

### Issue: UI not loading
**Solution**: Check if UI dependency is included
```bash
mvn dependency:tree | grep springwolf-ui
```

## Next Steps

1. ✅ **Verify**: Open http://localhost:8082/springwolf/docs
2. ✅ **Test**: Use publisher UI to send test event
3. ✅ **Document**: Add descriptions to event classes
4. ✅ **Integrate**: Connect EventCatalog generator
5. ✅ **Expand**: Add to Orders and Collections services

## Benefits Realized

| Before | After |
|--------|-------|
| Manual event documentation | Auto-generated from code |
| Schema Registry UI only | Interactive AsyncAPI docs |
| Postman/curl for testing | Built-in event publisher |
| Outdated docs risk | Always current with code |
| Siloed knowledge | Centralized event catalog |

## Resources

- Full Guide: `SpringWolf-Integration-Guide.md`
- SpringWolf Docs: https://www.springwolf.dev/
- Your AsyncAPI: http://localhost:8082/springwolf/asyncapi.json

---

**Implementation Time: ~5 minutes**
**Maintenance Time: Zero** (auto-updated with code changes)
