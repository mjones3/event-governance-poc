# BioPro Event Governance Framework - Architecture

## Enterprise Architecture Overview

This document provides detailed architecture diagrams and design decisions for the BioPro Event Governance Framework.

---

## Detailed Component Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        App1[Orders Service]
        App2[Collections Service]
        App3[Manufacturing Service]
    end

    subgraph "BioPro DLQ Framework"
        subgraph "Core Module"
            DLQProc[DLQ Processor]
            Reprocessor[Reprocessing Service]
            Model[Domain Models]
        end

        subgraph "Integration Module"
            KafkaInt[Kafka Integration]
            SchemaReg[Schema Registry Service]
            Cache[In-Memory Cache - Caffeine]
        end

        subgraph "Config Module"
            AutoConf[Auto Configuration]
            Props[Configuration Properties]
            CB[Circuit Breaker]
            Retry[Retry Logic]
        end

        subgraph "Security Module"
            Audit[Audit Service]
            Auth[Authorization]
        end

        subgraph "Monitoring Module"
            Metrics[Metrics Collector]
            DynaMetrics[Dynatrace Custom Metrics]
            Health[Health Indicators]
        end
    end

    subgraph "Infrastructure"
        Kafka[(Kafka Cluster)]
        SR[(Schema Registry)]
        Dynatrace[Dynatrace]
    end

    App1 --> DLQProc
    App2 --> DLQProc
    App3 --> DLQProc

    DLQProc --> KafkaInt
    DLQProc --> SchemaReg
    DLQProc --> CB
    DLQProc --> Retry
    DLQProc --> Audit
    DLQProc --> Metrics

    Reprocessor --> KafkaInt
    Reprocessor --> Audit

    SchemaReg --> Cache

    KafkaInt --> Kafka
    SchemaReg --> SR

    Metrics --> Dynatrace
    DynaMetrics --> Dynatrace

    AutoConf -.->|configures| DLQProc
    AutoConf -.->|configures| CB
    AutoConf -.->|configures| Retry

    style DLQProc fill:#FF6B6B
    style SchemaReg fill:#4ECDC4
    style CB fill:#95E1D3
    style Retry fill:#95E1D3
    style Audit fill:#F38181
    style Metrics fill:#AA96DA
```

---

## Event Processing Flow (Detailed)

```mermaid
sequenceDiagram
    autonumber
    participant App as BioPro Module
    participant Cache as Schema Cache (Caffeine)
    participant Schema as Schema Registry
    participant Validator as Schema Validator
    participant CB as Circuit Breaker
    participant Retry as Retry Logic
    participant DLQ as DLQ Processor
    participant Kafka as Kafka Broker
    participant Audit as Audit Service
    participant Metrics as Metrics Collector

    App->>Cache: Check Schema Cache

    alt Cache Hit
        Cache-->>App: Return Schema
    else Cache Miss
        App->>Schema: Fetch Schema
        Schema-->>Cache: Store in Cache
        Schema-->>App: Return Schema
    end

    App->>Validator: Validate Event

    alt Valid Event
        Validator-->>App: Valid
        App->>CB: Check Circuit State

        alt Circuit Closed
            CB-->>App: Allow
            App->>Retry: Execute with Retry

            loop Retry Attempts
                Retry->>Kafka: Publish Event

                alt Success
                    Kafka-->>Retry: Ack
                    Retry-->>App: Success
                    App->>Metrics: Record Success
                    App->>Audit: Log Success
                else Failure
                    Kafka-->>Retry: Error
                    Note over Retry: Wait (exponential backoff)
                end
            end

            alt All Retries Failed
                Retry-->>App: Final Failure
                App->>DLQ: Route to DLQ
                DLQ->>Kafka: Publish to DLQ Topic
                DLQ->>Metrics: Record DLQ Event
                DLQ->>Audit: Log DLQ Routing
                App->>CB: Record Failure
            end

        else Circuit Open
            CB-->>App: Reject (Fail Fast)
            App->>DLQ: Route to DLQ
            DLQ->>Kafka: Publish to DLQ Topic
        end

    else Invalid Event
        Validator-->>App: Invalid
        App->>DLQ: Route to DLQ
        DLQ->>Kafka: Publish to DLQ Topic
        DLQ->>Metrics: Record Schema Error
        DLQ->>Audit: Log Validation Failure
    end
```

---

## DLQ Data Model

```mermaid
erDiagram
    DLQEvent ||--o{ BusinessContext : has
    DLQEvent {
        string dlqEventId PK
        string originalEventId
        string module
        string eventType
        string originalTopic
        bytes originalPayload
        enum errorType
        string errorMessage
        string stackTrace
        int retryCount
        enum priority
        timestamp originalTimestamp
        timestamp dlqTimestamp
        string correlationId
        enum status
        int reprocessingCount
        string reprocessedBy
    }

    BusinessContext {
        string module
        string version
        string environment
        map metadata
    }

    DLQEvent ||--o{ ReprocessingAttempt : has
    ReprocessingAttempt {
        string attemptId PK
        string dlqEventId FK
        timestamp attemptTimestamp
        string initiatedBy
        enum result
        string errorMessage
    }
```

---

## Resilience Patterns

### Circuit Breaker States

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open : Failure threshold exceeded
    Open --> HalfOpen : Wait duration elapsed
    HalfOpen --> Closed : Success threshold met
    HalfOpen --> Open : Failure detected

    note right of Closed
        Normal operation
        Recording successes/failures
        Sliding window: 100 calls
    end note

    note right of Open
        Fail fast
        No calls permitted
        Wait: 1 minute (default)
    end note

    note right of HalfOpen
        Test recovery
        Limited calls: 3 (default)
        Deciding state
    end note
```

### Retry Strategy

```mermaid
graph LR
    A[Attempt 1] -->|Fail| B[Wait 1s]
    B --> C[Attempt 2]
    C -->|Fail| D[Wait 2s]
    D --> E[Attempt 3]
    E -->|Fail| F[Wait 4s]
    F --> G[Attempt 4]
    G -->|Fail| H[Route to DLQ]

    C -->|Success| S1[Success]
    E -->|Success| S2[Success]
    G -->|Success| S3[Success]

    style A fill:#4CAF50
    style C fill:#4CAF50
    style E fill:#4CAF50
    style G fill:#4CAF50
    style H fill:#FF5252
    style S1 fill:#00C853
    style S2 fill:#00C853
    style S3 fill:#00C853
```

---

## Schema Registry Integration

### Schema Caching Strategy

```mermaid
graph TB
    App[Application]
    Cache[In-Memory Cache<br/>Caffeine<br/>30 min TTL<br/>1000 entries]
    SR[Schema Registry<br/>Confluent<br/>Built-in caching]

    App -->|1. Check| Cache
    Cache -->|Hit| App
    Cache -->|Miss| SR
    SR -->|Schema| Cache
    SR -->|Schema| App

    style Cache fill:#4CAF50
    style SR fill:#FF9800
```

### Schema Evolution

```mermaid
graph LR
    V1[Schema v1] --> V2[Schema v2]
    V2 --> V3[Schema v3]

    V1 -.->|Backward Compatible| V2
    V2 -.->|Backward Compatible| V3

    subgraph "Compatibility Rules"
        BC[Backward Compatible<br/>✓ Add optional fields<br/>✓ Remove fields with defaults<br/>✗ Change field types<br/>✗ Remove required fields]
    end

    style V1 fill:#E3F2FD
    style V2 fill:#BBDEFB
    style V3 fill:#90CAF9
```

---

## Deployment Architecture

### Development Environment

```mermaid
graph TB
    subgraph "Developer Machine"
        IDE[IDE]
        App[Spring Boot App<br/>Port 8080]
    end

    subgraph "Docker Compose"
        ZK[Zookeeper<br/>Port 2181]
        Kafka[Kafka<br/>Port 9092]
        SR[Schema Registry<br/>Port 8081]
        UI[Kafka UI<br/>Port 8090]
    end

    IDE --> App
    App --> Kafka
    App --> SR
    Kafka --> ZK
    SR --> Kafka
    UI --> Kafka
    UI --> SR

    style App fill:#4CAF50
    style Kafka fill:#000000,color:#FFFFFF
    style SR fill:#0066CC,color:#FFFFFF
```

### Production Environment (Multi-AZ)

```mermaid
graph TB
    subgraph "AWS - us-east-1"
        subgraph "AZ-1a"
            App1[Orders Service<br/>Instance 1]
            Kafka1[Kafka Broker 1]
        end

        subgraph "AZ-1b"
            App2[Orders Service<br/>Instance 2]
            Kafka2[Kafka Broker 2]
        end

        subgraph "AZ-1c"
            App3[Orders Service<br/>Instance 3]
            Kafka3[Kafka Broker 3]
        end

        ALB[Application Load Balancer]
        SR[Schema Registry<br/>HA Cluster]
    end

    ALB --> App1
    ALB --> App2
    ALB --> App3

    App1 --> Kafka1
    App1 --> Kafka2
    App1 --> Kafka3

    App2 --> Kafka1
    App2 --> Kafka2
    App2 --> Kafka3

    App3 --> Kafka1
    App3 --> Kafka2
    App3 --> Kafka3

    App1 --> SR
    App2 --> SR
    App3 --> SR

    Kafka1 -.->|Replication| Kafka2
    Kafka2 -.->|Replication| Kafka3
    Kafka3 -.->|Replication| Kafka1

    style ALB fill:#FF9800
    style SR fill:#0066CC,color:#FFFFFF
```

---

## Monitoring & Observability

### Metrics Flow

```mermaid
graph LR
    App[BioPro Module]
    Micrometer[Micrometer]
    DynaRegistry[Dynatrace Registry]
    OneAgent[Dynatrace OneAgent]
    Dynatrace[Dynatrace SaaS]
    Alerts[Davis AI & Alerts]

    App -->|Metrics & Custom Events| Micrometer
    Micrometer -->|Export| DynaRegistry
    DynaRegistry -->|Push| OneAgent
    OneAgent -->|Ingest| Dynatrace
    Dynatrace --> Alerts
    Alerts -->|Notifications| Team[Team: Slack/Email/PagerDuty]
    Dynatrace -->|Dashboards & Analytics| Exec[Executives]

    style Micrometer fill:#4CAF50
    style DynaRegistry fill:#2196F3
    style OneAgent fill:#1976D2
    style Dynatrace fill:#1496FF,color:#FFFFFF
```

### Key Dashboard Panels

```mermaid
graph TB
    D[BioPro DLQ Dashboard]

    D --> P1[Event Throughput<br/>Events/sec by Module]
    D --> P2[DLQ Rate<br/>% of events to DLQ]
    D --> P3[Processing Duration<br/>p50, p95, p99]
    D --> P4[Circuit Breaker State<br/>Closed/Open/Half-Open]
    D --> P5[Error Distribution<br/>By error type]
    D --> P6[Reprocessing Success Rate<br/>Success vs Failure]

    style D fill:#FF6B6B,color:#FFFFFF
    style P1 fill:#4ECDC4
    style P2 fill:#4ECDC4
    style P3 fill:#4ECDC4
    style P4 fill:#4ECDC4
    style P5 fill:#4ECDC4
    style P6 fill:#4ECDC4
```

---

## Security Architecture

### Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant User
    participant API as BioPro API
    participant JWT as JWT Validator
    participant RBAC as RBAC Service
    participant DLQ as DLQ Service
    participant Audit as Audit Log

    User->>API: Request with JWT Token
    API->>JWT: Validate Token

    alt Token Valid
        JWT-->>API: Valid User
        API->>RBAC: Check Permissions

        alt Has Permission
            RBAC-->>API: Authorized
            API->>DLQ: Execute Operation
            DLQ-->>API: Result
            API->>Audit: Log Operation
            API-->>User: Success Response
        else No Permission
            RBAC-->>API: Unauthorized
            API->>Audit: Log Authorization Failure
            API-->>User: 403 Forbidden
        end
    else Token Invalid
        JWT-->>API: Invalid
        API->>Audit: Log Auth Failure
        API-->>User: 401 Unauthorized
    end
```

---

## Design Decisions

### 1. Multi-Module Maven Project

**Decision**: Use Maven multi-module structure instead of separate repositories

**Rationale**:
- Simplified dependency management
- Easier versioning across modules
- Single build command for entire library
- Consistent release process

### 2. Spring Boot Starter Pattern

**Decision**: Package as Spring Boot Starter with auto-configuration

**Rationale**:
- Zero-configuration for consuming applications
- Follows Spring Boot conventions
- Easy adoption by BioPro teams
- Automatic bean registration

### 3. Single-Layer In-Memory Schema Caching

**Decision**: Use only in-memory Caffeine cache (Schema Registry has built-in caching)

**Rationale**:
- Schema Registry client already has built-in caching
- Simpler architecture (no external cache dependency)
- Lower operational overhead
- Caffeine provides excellent performance for application-level caching
- Reduces infrastructure complexity

### 4. Circuit Breaker + Retry

**Decision**: Use both patterns together (circuit breaker wraps retry)

**Rationale**:
- Retry handles transient failures
- Circuit breaker prevents cascading failures
- Combined approach provides comprehensive resilience
- Aligns with enterprise patterns

### 5. DLQ per Module

**Decision**: Each BioPro module has its own DLQ topic

**Rationale**:
- Module isolation
- Independent reprocessing workflows
- Easier troubleshooting
- Module-specific retention policies

---

## Performance Characteristics

### Throughput

- **Event Validation**: 10,000+ events/sec
- **DLQ Routing**: 5,000+ events/sec
- **Schema Cache Hit Rate**: >95% in steady state

### Latency (p99)

- **Event Processing**: < 100ms
- **Schema Validation**: < 10ms (cache hit)
- **Schema Validation**: < 50ms (cache miss)
- **DLQ Routing**: < 50ms

### Resource Usage

- **Memory**: ~512MB baseline + schema cache
- **CPU**: Low (<10% idle, <30% under load)
- **Network**: Dependent on event size and throughput

---

## Future Enhancements

1. **AWS Integration**
   - Secrets Manager for credentials
   - KMS for encryption
   - CloudWatch Logs for audit trail
   - S3 for long-term DLQ storage

2. **Advanced Security**
   - Complete JWT validation with Cognito
   - Fine-grained RBAC with LDAP integration
   - Automated PII detection with AWS Comprehend
   - Field-level encryption

3. **Enhanced Monitoring**
   - Full Dynatrace OneAgent integration
   - Custom business events
   - Executive dashboards
   - Automated alerting

4. **Operational Features**
   - Web UI for DLQ management
   - Bulk reprocessing capabilities
   - Automated recovery workflows
   - Historical analytics

---

## References

- [Confluent Schema Registry Documentation](https://docs.confluent.io/platform/current/schema-registry/index.html)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Resilience4j Documentation](https://resilience4j.readme.io/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)

---

**Document Version**: 1.0
**Last Updated**: 2025
**Author**: Melvin Jones, Solutions Architect
