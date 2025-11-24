# Story: Schema Registry Integration

**Story Points**: 5
**Priority**: High
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: Schema Registry

---

## User Story

**As a** BioPro developer
**I want** event schemas centrally managed in a schema registry
**So that** all producers and consumers use validated, versioned schemas preventing schema-related failures

---

## Description

Implement integration with Confluent Schema Registry to provide centralized schema management for all BioPro event schemas. Enable automatic schema validation at both producer and consumer level using Avro serialization with embedded schema IDs.

### Background
BioPro currently lacks centralized schema management, leading to:
- Schema inconsistencies causing production failures
- No version control for event schema evolution
- Manual coordination required for schema changes
- Risk of incompatible schema changes breaking consumers

This story establishes Schema Registry as the single source of truth for all BioPro event schemas.

---

## Acceptance Criteria

**AC1: Schema Registry Deployment**
- GIVEN infrastructure requirements for Schema Registry
- WHEN registry is deployed to development environment
- THEN registry is accessible via REST API at http://schema-registry:8081
- AND health check endpoint returns healthy status
- AND registry is configured for BACKWARD compatibility mode by default

**AC2: Schema Registration**
- GIVEN an Avro schema for a BioPro event
- WHEN schema is registered via REST API
- THEN schema is assigned unique schema ID
- AND schema version is tracked (starting at version 1)
- AND schema is retrievable by subject name
- AND subject naming follows pattern: `{EventName}Event-value`

**AC3: Schema Compatibility Validation**
- GIVEN an existing schema registered in the registry
- WHEN new schema version is registered
- THEN compatibility check is performed against latest version
- AND backward-compatible changes are accepted
- AND breaking changes are rejected with error message
- AND compatibility mode can be configured per subject

**AC4: Producer Integration**
- GIVEN a BioPro service publishing events
- WHEN service uses Avro serializer with Schema Registry
- THEN schema ID is automatically embedded in message header
- AND message is validated against schema before publishing
- AND invalid messages cannot be published to Kafka
- AND schema is cached locally to minimize registry calls

**AC5: Consumer Integration**
- GIVEN a BioPro service consuming events
- WHEN service uses Avro deserializer with Schema Registry
- THEN schema is retrieved from registry using embedded schema ID
- AND message is validated against retrieved schema
- AND schema is cached locally for performance
- AND schema mismatches are detected and handled

---

## Technical Details

### Schema Registry Configuration
```yaml
# docker-compose.yml
schema-registry:
  image: confluentinc/cp-schema-registry:latest
  environment:
    SCHEMA_REGISTRY_HOST_NAME: schema-registry
    SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:9092
    SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
  ports:
    - "8081:8081"
```

### Compatibility Modes
- **BACKWARD** (default): New schema can read data written by previous schema
- **FORWARD**: Old schema can read data written by new schema
- **FULL**: Both BACKWARD and FORWARD
- **NONE**: No compatibility checking

### REST API Endpoints
- `GET /subjects` - List all subjects
- `POST /subjects/{subject}/versions` - Register new schema
- `GET /subjects/{subject}/versions/latest` - Get latest schema
- `POST /compatibility/subjects/{subject}/versions/latest` - Test compatibility

---

## Implementation Tasks

### 1. Deploy Schema Registry (2 hours)
- [ ] Add Schema Registry to docker-compose.yml
- [ ] Configure connection to Kafka
- [ ] Set default compatibility mode to BACKWARD
- [ ] Verify registry health endpoint

### 2. Register BioPro Event Schemas (3 hours)
- [ ] Create script to bulk-register existing schemas
- [ ] Register sample events (OrderCreated, CollectionReceived, etc.)
- [ ] Verify schema IDs are assigned
- [ ] Test schema retrieval via REST API

### 3. Implement Producer Integration (4 hours)
- [ ] Add Confluent Avro serializer dependency
- [ ] Configure Kafka producer with schema registry URL
- [ ] Update event publishing code to use Avro serialization
- [ ] Test schema validation on publish
- [ ] Verify schema ID in message headers

### 4. Implement Consumer Integration (4 hours)
- [ ] Add Confluent Avro deserializer dependency
- [ ] Configure Kafka consumer with schema registry URL
- [ ] Update event consumption code to use Avro deserialization
- [ ] Test schema-based deserialization
- [ ] Handle schema evolution scenarios

### 5. Testing & Validation (3 hours)
- [ ] Test backward-compatible schema changes
- [ ] Test breaking schema changes (should be rejected)
- [ ] Verify schema caching performance
- [ ] Test schema evolution with version incrementing
- [ ] Document common error scenarios and resolutions

---

## Testing Strategy

### Unit Tests
- Schema registration and retrieval
- Compatibility validation logic
- Avro serialization/deserialization

### Integration Tests
- End-to-end message flow with schema validation
- Producer publishes with schema, consumer deserializes
- Schema evolution scenarios (adding optional field, etc.)

### Error Scenarios
- Schema registry unavailable (should use cached schema)
- Invalid schema registration attempt
- Incompatible schema change detection
- Message with unknown schema ID

---

## Dependencies

### Infrastructure
- Kafka cluster running and accessible
- Network connectivity to Kafka from Schema Registry

### Libraries (Maven Dependencies)
```xml
<dependency>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-avro-serializer</artifactId>
    <version>7.5.0</version>
</dependency>
<dependency>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-schema-registry-client</artifactId>
    <version>7.5.0</version>
</dependency>
```

---

## Definition of Done

- [ ] Schema Registry deployed and accessible
- [ ] At least 5 BioPro event schemas registered successfully
- [ ] Producer can publish events with schema validation
- [ ] Consumer can consume events with schema validation
- [ ] Compatibility validation working (backward-compatible changes accepted, breaking changes rejected)
- [ ] Documentation created for schema registration process
- [ ] Integration tests passing
- [ ] Schema caching confirmed working (registry not called for every message)

---

## Documentation Deliverables

- Schema Registry deployment guide
- How to register new schemas
- How to configure producers/consumers for Avro with Schema Registry
- Troubleshooting guide for common issues
- Schema evolution best practices

---

## Risk & Mitigation

**Risk**: Schema Registry becomes single point of failure
- **Mitigation**: Implement schema caching in producers/consumers
- **Mitigation**: Configure Schema Registry with high availability

**Risk**: Breaking schema changes slip through
- **Mitigation**: Enforce compatibility checks in CI/CD pipeline
- **Mitigation**: Require schema approval workflow for changes

**Risk**: Performance impact from schema lookups
- **Mitigation**: Enable schema caching (default in Confluent libraries)
- **Mitigation**: Monitor schema registry performance metrics

---

**Labels**: schema-registry, avro, proof-of-concept, infrastructure
**Created By**: Melvin Jones
