# Story: Skeleton Service Integration for POC

**Story Points**: 3
**Priority**: Medium
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: POC Services

---

## User Story

**As a** BioPro developer
**I want** skeleton implementations of Orders, Collections, and Manufacturing services integrated with event governance
**So that** I can demonstrate end-to-end event flow with schema validation and DLQ processing across multiple domains

---

## Description

Integrate skeleton implementations of three core BioPro services (Orders, Collections, Manufacturing) into the proof-of-concept environment. Each service should publish and consume domain events using Avro serialization with Schema Registry validation, implement DLQ processing via AbstractListener, and demonstrate realistic event-driven interactions between bounded contexts.

### Background
The POC requires working services that demonstrate:
- Cross-service event communication
- Schema Registry integration in action
- DLQ processing for failed events
- Service dependency visualization in EventCatalog
- Realistic BioPro domain event flows

These skeleton services provide tangible examples for stakeholders while validating the governance framework.

---

## Acceptance Criteria

**AC1: Orders Service Integration**
- GIVEN skeleton Orders service implementation
- WHEN service is deployed in POC environment
- THEN service publishes `OrderCreatedEvent` to Kafka
- AND event uses Avro serialization with Schema Registry
- AND event appears in EventCatalog as produced by orders-service
- AND service implements AbstractListener for consuming events

**AC2: Collections Service Integration**
- GIVEN skeleton Collections service implementation
- WHEN service is deployed in POC environment
- THEN service publishes `CollectionReceivedEvent` to Kafka
- AND service consumes `OrderCreatedEvent` (listens for new orders)
- AND both publish and consume use Schema Registry validation
- AND service implements DLQ handling for failed events

**AC3: Manufacturing Service Integration**
- GIVEN skeleton Manufacturing service implementation
- WHEN service is deployed in POC environment
- THEN service publishes `ApheresisPlasmaProductCreatedEvent` to Kafka
- AND service consumes `CollectionReceivedEvent` (listens for collections)
- AND manufacturing flow demonstrates event-driven processing
- AND DLQ processing captures any failures

**AC4: Docker Compose Integration**
- GIVEN all three skeleton services
- WHEN POC environment starts via docker-compose
- THEN all services start successfully
- AND services connect to Kafka and Schema Registry
- AND health checks pass for all services
- AND logs show successful event publishing/consuming

**AC5: End-to-End Event Flow**
- GIVEN all services running in POC
- WHEN OrderCreatedEvent is published
- THEN Collections service receives and processes event
- AND CollectionReceivedEvent is published
- AND Manufacturing service receives and processes event
- AND complete event chain is visible in EventCatalog
- AND all schema validations pass

**AC6: DLQ Integration Testing**
- GIVEN services with DLQ processing enabled
- WHEN invalid event is published (schema mismatch)
- THEN event processing fails validation
- AND event is routed to dead letter queue
- AND failure context is preserved
- AND DLQ topic contains failed event with error details

---

## Technical Details

### Service Stack
- **Framework**: Spring Boot 3.x with WebFlux (reactive)
- **Kafka**: Spring Kafka with Avro serialization
- **Schema Registry**: Confluent client libraries
- **DLQ**: AbstractListener base class

### Orders Service
```java
@Service
public class OrderEventPublisher {

    @Autowired
    private KafkaTemplate<String, OrderCreatedEvent> kafkaTemplate;

    public Mono<Void> publishOrderCreated(OrderCreatedEvent event) {
        return Mono.fromFuture(
            kafkaTemplate.send("biopro.orders.events", event)
        ).then();
    }
}
```

### Collections Service (Producer + Consumer)
```java
@Service
public class CollectionEventListener extends AbstractListener<OrderCreatedEvent> {

    @Autowired
    private CollectionEventPublisher publisher;

    @Override
    protected Mono<OrderCreatedEvent> processMessage(OrderCreatedEvent event) {
        // Simulate collection received processing
        return Mono.fromCallable(() -> {
            CollectionReceivedEvent collection =
                CollectionReceivedEvent.builder()
                    .unitNumber(event.getOrderNumber())
                    .donationType(DonationType.ALLOGENEIC)
                    .build();

            publisher.publishCollectionReceived(collection).subscribe();
            return event;
        });
    }
}
```

### Docker Compose Configuration
```yaml
services:
  orders-service:
    build: ./orders-service
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      SCHEMA_REGISTRY_URL: http://schema-registry:8081
    depends_on:
      - kafka
      - schema-registry

  collections-service:
    build: ./collections-service
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      SCHEMA_REGISTRY_URL: http://schema-registry:8081
    depends_on:
      - kafka
      - schema-registry

  manufacturing-service:
    build: ./manufacturing-service
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      SCHEMA_REGISTRY_URL: http://schema-registry:8081
    depends_on:
      - kafka
      - schema-registry
```

---

## Implementation Tasks

### 1. Create Orders Service Skeleton (2 hours)
- [ ] Initialize Spring Boot project with required dependencies
- [ ] Implement OrderCreatedEvent publisher
- [ ] Configure Kafka producer with Schema Registry
- [ ] Add REST endpoint to trigger order creation
- [ ] Configure application.yml for Kafka/Schema Registry
- [ ] Create Dockerfile

### 2. Create Collections Service Skeleton (3 hours)
- [ ] Initialize Spring Boot project
- [ ] Implement OrderCreatedEvent consumer (using AbstractListener)
- [ ] Implement CollectionReceivedEvent publisher
- [ ] Configure both producer and consumer in application.yml
- [ ] Test DLQ routing for failed events
- [ ] Create Dockerfile

### 3. Create Manufacturing Service Skeleton (3 hours)
- [ ] Initialize Spring Boot project
- [ ] Implement CollectionReceivedEvent consumer (using AbstractListener)
- [ ] Implement ApheresisPlasmaProductCreatedEvent publisher
- [ ] Configure Kafka producer/consumer
- [ ] Add business logic simulation (processing delay)
- [ ] Create Dockerfile

### 4. Docker Compose Integration (2 hours)
- [ ] Add all three services to docker-compose.yml
- [ ] Configure service dependencies
- [ ] Add health checks
- [ ] Configure environment variables
- [ ] Test full stack startup

### 5. EventCatalog Service Registration (2 hours)
- [ ] Create service MDX files for orders-service
- [ ] Create service MDX files for collections-service
- [ ] Create service MDX files for manufacturing-service
- [ ] Document producer/consumer relationships
- [ ] Verify NodeGraph visualization shows service connections

---

## Testing Strategy

### Integration Tests
- Full stack deployment (Kafka, Schema Registry, all services)
- Publish OrderCreatedEvent via REST API
- Verify CollectionReceivedEvent published
- Verify ApheresisPlasmaProductCreatedEvent published
- Check all events appear in Kafka topics

### DLQ Testing
- Publish invalid event (wrong schema version)
- Verify event routed to DLQ
- Check DLQ message contains failure context
- Verify service continues processing valid events

### Schema Validation Testing
- Modify event schema (add optional field)
- Verify backward compatibility validation passes
- Publish event with new schema
- Verify consumers can deserialize with old schema

---

## Dependencies

### Maven Dependencies (each service)
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-webflux</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.kafka</groupId>
        <artifactId>spring-kafka</artifactId>
    </dependency>
    <dependency>
        <groupId>io.confluent</groupId>
        <artifactId>kafka-avro-serializer</artifactId>
    </dependency>
    <dependency>
        <groupId>com.biopro</groupId>
        <artifactId>event-governance-common</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </dependency>
</dependencies>
```

### Infrastructure
- Kafka cluster running
- Schema Registry deployed
- Event schemas registered
- DLQ topics provisioned

---

## Definition of Done

- [ ] Three skeleton services (Orders, Collections, Manufacturing) implemented
- [ ] All services integrated with Kafka and Schema Registry
- [ ] AbstractListener base class used for event consumption
- [ ] DLQ processing working for all consumers
- [ ] Services added to docker-compose.yml
- [ ] Full stack starts successfully with `docker-compose up`
- [ ] End-to-end event flow working (Order → Collection → Manufacturing)
- [ ] All events visible in Kafka topics with schema IDs
- [ ] Service pages created in EventCatalog
- [ ] NodeGraph visualization shows service relationships
- [ ] DLQ test demonstrates failure handling
- [ ] README created with demo instructions

---

## Documentation Deliverables

- Service architecture diagram showing event flows
- How to run the POC demo
- How to trigger events via REST APIs
- Expected event sequence documentation
- Troubleshooting guide for common startup issues

---

## Demo Scenarios

### Scenario 1: Happy Path
1. POST to orders-service creates order
2. Collections-service receives OrderCreatedEvent
3. Manufacturing-service receives CollectionReceivedEvent
4. All events visible in EventCatalog
5. Schema validation passes at each step

### Scenario 2: Schema Evolution
1. Update CollectionReceivedEvent schema (add optional field)
2. Register new schema version
3. Publish event with new schema
4. Verify old consumers still work (backward compatibility)

### Scenario 3: DLQ Processing
1. Manually publish invalid event
2. Consumer rejects event after retries
3. Event appears in DLQ topic
4. Support team can investigate failure context

---

## Risk & Mitigation

**Risk**: Services may not start in correct order
- **Mitigation**: Use docker-compose depends_on with health checks
- **Mitigation**: Services implement connection retry logic

**Risk**: Network issues between services and Kafka
- **Mitigation**: Configure connection timeouts and retries
- **Mitigation**: Health check endpoints verify Kafka connectivity

**Risk**: Schema Registry unavailable during startup
- **Mitigation**: Services use cached schemas when available
- **Mitigation**: Fail fast with clear error if registry required

---

**Labels**: skeleton-services, poc, integration, proof-of-concept
**Created By**: Melvin Jones
