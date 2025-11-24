# Story: Dead Letter Queue Processing Framework

**Story Points**: 5
**Priority**: Highest (Patient Safety Critical)
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: DLQ Framework

---

## User Story

**As a** BioPro operations team member
**I want** systematic dead letter queue processing for failed events
**So that** no critical safety events are silently dropped and all failures are auditable for FDA compliance

---

## Description

Implement comprehensive dead letter queue (DLQ) processing framework to ensure zero tolerance for lost safety-critical events (quarantine, test results, product unsuitability). All event processing failures must be automatically captured, logged, and routed to dead letter queues for systematic investigation and remediation.

### Patient Safety Impact
When critical safety events like quarantine notifications or test result exceptions fail processing and are silently dropped, unsuitable blood products could be released for transfusion, potentially causing:
- Hemolytic transfusion reactions (life-threatening)
- Disease transmission (HIV, Hepatitis, etc.)
- Regulatory violations and patient harm

This framework ensures **no safety-critical event can be silently dropped**.

---

## Acceptance Criteria

**AC1: Common DLQ Library (AbstractListener)**
- GIVEN a BioPro service consuming Kafka events
- WHEN service implements AbstractListener base class
- THEN event processing failures are automatically captured
- AND failed events are routed to dead letter queue topic (`.DLT` suffix)
- AND event payload is preserved with failure context
- AND retry attempts are tracked and auditable

**AC2: Automatic DLQ Topic Provisioning**
- GIVEN a Kafka topic for BioPro events (e.g., `orders.events`)
- WHEN DLQ framework is enabled
- THEN corresponding DLQ topic is created (`orders.events.DLT`)
- AND DLQ topic has appropriate retention policy
- AND DLQ topic preserves message ordering where needed

**AC3: Retry Policy Configuration**
- GIVEN an event that fails processing
- WHEN failure occurs
- THEN configurable retry policy is applied (e.g., 3 attempts with exponential backoff)
- AND retry attempts are logged with timestamps
- AND after max retries, event is sent to DLQ
- AND retry policy is configurable per service/event type

**AC4: Failure Context Preservation**
- GIVEN an event that fails processing and goes to DLQ
- WHEN support team investigates failure
- THEN complete failure context is available:
  - Original event payload (full)
  - Exception message and stack trace
  - Timestamp of failure
  - Retry attempt history
  - Consumer group and partition info
- AND context enables root cause analysis

**AC5: Monitoring & Alerting Integration**
- GIVEN events in dead letter queues
- WHEN DLQ messages accumulate
- THEN monitoring system tracks:
  - DLQ message count per topic
  - DLQ message age
  - Failure rate trends
- AND alerts are triggered for safety-critical events
- AND dashboards show DLQ health metrics

**AC6: Manual Reprocessing Capability**
- GIVEN an event in DLQ that has been investigated
- WHEN issue is resolved (code fix, data correction, etc.)
- THEN event can be manually reprocessed
- AND reprocessing is tracked in audit trail
- AND reprocessing can be done individually or in batches

---

## Technical Details

### AbstractListener Base Class Structure
```java
public abstract class AbstractListener<T> {

    // Template method for event processing
    @KafkaListener(...)
    public void listen(@Payload T event,
                      @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
                      @Header(KafkaHeaders.OFFSET) long offset) {
        try {
            validateEvent(event);
            processMessage(event)
                .doOnError(this::handleProcessingError)
                .subscribe();
        } catch (InvalidEventException e) {
            sendToDLQ(event, e);
        }
    }

    // Abstract method for business logic
    protected abstract Mono<T> processMessage(T event);

    // DLQ handling
    private void sendToDLQ(T event, Exception error) {
        DLQMessage dlqMessage = DLQMessage.builder()
            .originalEvent(event)
            .exception(error.getMessage())
            .stackTrace(error.getStackTrace())
            .timestamp(Instant.now())
            .retryCount(getRetryCount(event))
            .build();

        kafkaTemplate.send(topic + ".DLT", dlqMessage);
        logDLQEvent(dlqMessage);
    }
}
```

### Retry Policy Configuration
```yaml
# application.yml
event-governance:
  dlq:
    retry:
      max-attempts: 3
      backoff:
        initial-interval: 1000ms
        multiplier: 2.0
        max-interval: 10000ms
    safety-critical-events:
      - QuarantineEvent
      - TestResultException
      - ProductUnsuitability
      alert-on-failure: true
```

---

## Implementation Tasks

### 1. Create AbstractListener Base Class (4 hours)
- [ ] Define AbstractListener interface with template method pattern
- [ ] Implement DLQ routing logic
- [ ] Add retry policy with exponential backoff
- [ ] Implement failure context preservation
- [ ] Add circuit breaker pattern

### 2. DLQ Topic Management (2 hours)
- [ ] Create script to provision DLQ topics for all event topics
- [ ] Configure DLQ topic retention policies
- [ ] Set up DLQ topic naming convention (`.DLT` suffix)
- [ ] Test DLQ topic creation and configuration

### 3. Implement Retry Mechanism (3 hours)
- [ ] Add retry counter to event headers
- [ ] Implement exponential backoff logic
- [ ] Configure max retry attempts
- [ ] Add retry exhaustion handling
- [ ] Test retry scenarios

### 4. Failure Context Logging (2 hours)
- [ ] Capture exception details (message, stack trace)
- [ ] Log retry attempt history
- [ ] Preserve original event payload
- [ ] Add timestamp and metadata
- [ ] Structure logs for easy querying

### 5. Monitoring Integration (3 hours)
- [ ] Add metrics for DLQ message count
- [ ] Track DLQ processing latency
- [ ] Create dashboard for DLQ health
- [ ] Configure alerts for safety-critical events
- [ ] Test alert triggering

### 6. Manual Reprocessing Tool (2 hours)
- [ ] Create utility to read events from DLQ
- [ ] Implement reprocessing logic
- [ ] Add batch reprocessing capability
- [ ] Track reprocessed events
- [ ] Test reprocessing scenarios

---

## Testing Strategy

### Unit Tests
- AbstractListener template method flow
- Retry logic with various failure scenarios
- Circuit breaker state transitions
- DLQ message construction

### Integration Tests
- End-to-end event processing with failures
- Events correctly routed to DLQ after max retries
- Failure context preserved in DLQ messages
- Manual reprocessing from DLQ

### Safety-Critical Event Tests
- Quarantine event failure and DLQ routing
- Test result exception handling
- Product unsuitability event failures
- Alert triggering for critical events

---

## Dependencies

### Libraries (Maven)
```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-circuitbreaker</artifactId>
</dependency>
```

### Infrastructure
- Kafka cluster with DLQ topics provisioned
- Monitoring system (Dynatrace, Prometheus, etc.)
- Logging aggregation (ELK stack, Splunk, etc.)

---

## Definition of Done

- [ ] AbstractListener base class implemented and published to Maven repo
- [ ] At least one BioPro service integrated with DLQ framework
- [ ] DLQ topics provisioned for integrated service
- [ ] Retry policy working with configurable backoff
- [ ] Failed events successfully routed to DLQ with complete context
- [ ] Monitoring dashboard showing DLQ metrics
- [ ] Alerts configured for safety-critical event failures
- [ ] Manual reprocessing tool working and documented
- [ ] Unit tests >90% coverage
- [ ] Integration tests passing
- [ ] Documentation complete (usage guide, runbook)

---

## Documentation Deliverables

- AbstractListener usage guide for developers
- DLQ investigation runbook for support teams
- Configuration guide for retry policies
- Monitoring and alerting setup guide
- Manual reprocessing procedure

---

## Risk & Mitigation

**Risk**: DLQ itself could fail, losing events
- **Mitigation**: DLQ topics have high replication factor
- **Mitigation**: Monitor DLQ health and alert on issues

**Risk**: DLQ fills up with unprocessed events
- **Mitigation**: Alerting on DLQ message age and count
- **Mitigation**: Regular review of DLQ messages by support team

**Risk**: Retry storms could impact system performance
- **Mitigation**: Circuit breaker pattern to stop retry attempts
- **Mitigation**: Exponential backoff prevents rapid retries

---

## FDA Compliance Notes

This framework directly addresses FDA 510(k) requirements by:
- Ensuring no safety-critical events can be silently dropped
- Providing complete audit trail of all event processing failures
- Enabling systematic investigation and remediation of failures
- Documenting risk mitigation procedures for event processing

---

**Labels**: dlq, dead-letter-queue, patient-safety, fda-compliance, proof-of-concept
**Created By**: Melvin Jones
