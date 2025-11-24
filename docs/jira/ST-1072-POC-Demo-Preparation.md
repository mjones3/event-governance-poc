# Story: POC Demo Preparation and Presentation Assets

**Story Points**: 3
**Priority**: Medium
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: Demo/Presentation

---

## User Story

**As a** technical lead presenting Event Governance POC
**I want** polished demo environment and presentation materials
**So that** stakeholders clearly understand capabilities, business value, and are confident in recommending production implementation

---

## Description

Prepare comprehensive demo environment and presentation assets for Event Governance POC stakeholder demonstrations. Create automated demo scenarios, sample data, presentation slides, and recovery procedures to ensure smooth, impactful demonstrations that highlight patient safety benefits, FDA compliance capabilities, and developer productivity improvements.

### Background
POC success depends on effective stakeholder communication. Technical capabilities alone are insufficient - stakeholders need to see:
- Real-world event scenarios (order processing, quarantine events)
- Visual demonstration of schema validation preventing errors
- Clear explanation of patient safety impact
- Business value of automated governance

This story ensures POC is demo-ready with materials supporting both technical and executive audiences.

---

## Acceptance Criteria

**AC1: Automated Demo Data Generation**
- GIVEN clean POC environment
- WHEN demo data generation script is run
- THEN realistic sample events are published:
  - 5 OrderCreatedEvents with varied data
  - 5 CollectionReceivedEvents linked to orders
  - 3 ApheresisPlasmaProductCreatedEvents
  - 2 QuarantineEvents (safety-critical)
  - 1 invalid event triggering DLQ
- AND events appear in Kafka topics
- AND events visible in EventCatalog
- AND demo data represents realistic BioPro scenarios

**AC2: Demo Environment Reset Capability**
- GIVEN POC environment with previous demo data
- WHEN reset script is executed
- THEN all Kafka topics are cleared
- AND Schema Registry retains schemas (no re-registration needed)
- AND EventCatalog refreshes to clean state
- AND services restart cleanly
- AND environment ready for new demo in under 2 minutes

**AC3: Presentation Slide Deck**
- GIVEN stakeholder presentation meeting
- WHEN presenting POC to technical and business audiences
- THEN slide deck includes:
  - Executive summary (patient safety, FDA compliance)
  - Problem statement (current event governance gaps)
  - Solution overview (architecture diagram)
  - Live demo walkthrough slides
  - Business value quantification
  - Production roadmap (high-level)
  - Q&A preparation slides
- AND slides use BioPro branding and terminology

**AC4: Demo Script with Talking Points**
- GIVEN presenter delivering demo
- WHEN following demo script
- THEN script provides:
  - Opening hook (patient safety scenario)
  - Demonstration steps with exact commands
  - Expected outputs and what to highlight
  - Business value callouts at each step
  - Transition phrases between demo sections
  - Recovery steps if demo fails
  - Timing estimates (total 20 minutes)
- AND script tested with practice run

**AC5: Interactive Demo Scenarios**
- GIVEN live demo session
- WHEN demonstrating capabilities
- THEN presenter can show:
  - **Scenario 1**: Happy path event flow (Order → Collection → Manufacturing)
  - **Scenario 2**: Schema validation preventing incompatible change
  - **Scenario 3**: DLQ capturing failed safety-critical event
  - **Scenario 4**: EventCatalog self-service discovery
  - **Scenario 5**: CI/CD catching breaking schema change
- AND each scenario completes in 3-4 minutes
- AND failures are deliberate and highlight value

**AC6: Demo Environment Health Check**
- GIVEN demo about to start
- WHEN presenter runs health check script
- THEN script verifies:
  - All Docker containers running
  - Kafka accepting connections
  - Schema Registry accessible
  - EventCatalog UI loading
  - All services healthy
  - Sample data present (if needed)
- AND health check completes in 30 seconds
- AND provides clear GO/NO-GO status

---

## Technical Details

### Demo Data Generation Script
```python
#!/usr/bin/env python3
"""
Generate realistic demo data for Event Governance POC
"""
import uuid
import json
from datetime import datetime
from kafka import KafkaProducer
from confluent_kafka.avro import AvroProducer

def generate_demo_events():
    """Generate and publish sample events for demo"""

    # Orders
    for i in range(5):
        order = {
            "orderId": str(uuid.uuid4()),
            "customerCode": f"HOSP-{1000 + i}",
            "orderDate": datetime.now().isoformat(),
            "productCode": "PLATELET_APHERESIS",
            "quantity": 2,
            "priority": "ROUTINE" if i < 4 else "URGENT"
        }
        publish_event("biopro.orders.events", "OrderCreatedEvent", order)

    # Collections
    for i in range(5):
        collection = {
            "unitNumber": f"W{326394748 + i}",
            "collectionDate": datetime.now().isoformat(),
            "donationType": "ALLOGENEIC",
            "status": "RECEIVED"
        }
        publish_event("biopro.collections.events", "CollectionReceivedEvent", collection)

    # Invalid event for DLQ demo
    invalid_event = {"invalid": "schema"}
    publish_invalid_event("biopro.orders.events", invalid_event)
```

### Environment Reset Script
```bash
#!/bin/bash
# reset-demo.sh

echo "Resetting POC demo environment..."

# Clear Kafka topics (retain last hour for safety)
docker-compose exec kafka kafka-topics --delete --topic "biopro.*"

# Restart services (clears in-memory state)
docker-compose restart orders-service collections-service manufacturing-service

# Verify health
./health-check.sh

echo "Demo environment ready!"
```

### Health Check Script
```bash
#!/bin/bash
# health-check.sh

echo "Checking POC environment health..."

# Check Docker containers
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Some containers not running"
    exit 1
fi

# Check Kafka
if ! curl -s http://localhost:9092 > /dev/null; then
    echo "❌ Kafka not accessible"
    exit 1
fi

# Check Schema Registry
if ! curl -s http://localhost:8081/subjects | grep -q "\["; then
    echo "❌ Schema Registry not accessible"
    exit 1
fi

# Check EventCatalog
if ! curl -s http://localhost:3000 | grep -q "EventCatalog"; then
    echo "❌ EventCatalog not accessible"
    exit 1
fi

echo "✅ All systems healthy - ready for demo!"
```

---

## Implementation Tasks

### 1. Create Demo Data Generation (3 hours)
- [ ] Implement script to generate realistic events
- [ ] Create varied scenarios (routine, urgent, invalid)
- [ ] Add sample data for all event types
- [ ] Include safety-critical events (quarantine)
- [ ] Test data generation with Schema Registry
- [ ] Verify events appear in EventCatalog

### 2. Build Demo Environment Management (2 hours)
- [ ] Create reset script to clear demo data
- [ ] Implement health check script
- [ ] Add automated service restart capability
- [ ] Test reset/restart cycle
- [ ] Document timing for each operation

### 3. Develop Presentation Slide Deck (4 hours)
- [ ] Create executive summary slides
- [ ] Design architecture diagram slide
- [ ] Build demo walkthrough slides
- [ ] Add business value quantification
- [ ] Include patient safety scenario
- [ ] Design Q&A preparation slides
- [ ] Apply BioPro branding
- [ ] Review with stakeholders for feedback

### 4. Write Demo Script with Timing (3 hours)
- [ ] Document opening hook (patient safety)
- [ ] Write step-by-step demo commands
- [ ] Add expected outputs for each step
- [ ] Include business value talking points
- [ ] Document recovery procedures
- [ ] Add transition phrases
- [ ] Practice full demo and time it
- [ ] Refine based on practice session

### 5. Create Interactive Demo Scenarios (3 hours)
- [ ] Design happy path scenario
- [ ] Design schema validation failure scenario
- [ ] Design DLQ scenario with safety-critical event
- [ ] Design EventCatalog discovery scenario
- [ ] Design CI/CD validation scenario
- [ ] Test each scenario end-to-end
- [ ] Document expected outcomes

### 6. Prepare Backup and Recovery Plans (2 hours)
- [ ] Document common demo failures
- [ ] Create recovery procedures for each
- [ ] Prepare backup video/screenshots
- [ ] Test recovery procedures
- [ ] Create "Plan B" presentation flow

---

## Demo Scenarios Detail

### Scenario 1: Happy Path Event Flow (4 minutes)
**Talking Points**: "Let me show you how events flow through our system with automatic schema validation..."

**Steps**:
1. Show EventCatalog - browse to OrderCreatedEvent
2. Trigger order creation via REST API
3. Show Kafka topic receiving event
4. Show Collections service consuming event
5. Show Manufacturing service receiving collection
6. Return to EventCatalog - show complete event chain

**Business Value**: "This automation eliminates manual coordination between teams"

### Scenario 2: Schema Validation (3 minutes)
**Talking Points**: "Schema Registry prevents incompatible changes from breaking consumers..."

**Steps**:
1. Show current OrderCreatedEvent schema in Registry
2. Attempt to register breaking change (remove required field)
3. Show compatibility check rejection
4. Explain how this prevents production incidents

**Business Value**: "This prevented what would have been a production outage"

### Scenario 3: DLQ Safety Net (4 minutes)
**Talking Points**: "For patient safety, we cannot allow critical events to be silently dropped..."

**Steps**:
1. Explain quarantine event scenario
2. Publish invalid quarantine event
3. Show event rejected by consumer
4. Show event routed to DLQ with failure context
5. Show alert triggered for safety-critical event

**Business Value**: "This ensures FDA compliance and patient safety"

### Scenario 4: EventCatalog Discovery (3 minutes)
**Talking Points**: "Developers can now self-service discover and integrate with events..."

**Steps**:
1. Search for "quarantine" events
2. View schema fields and descriptions
3. Download Avro schema
4. Show service dependency visualization
5. Navigate from event to producer/consumer services

**Business Value**: "Eliminates weeks of manual coordination for integrations"

### Scenario 5: CI/CD Validation (3 minutes)
**Talking Points**: "Schema changes are automatically validated in pull requests..."

**Steps**:
1. Show PR with schema change
2. Show CI/CD pipeline running validation
3. Show compatibility check results in PR comment
4. Show build failure for breaking change

**Business Value**: "Catches issues before they reach production"

---

## Presentation Outline

### Slide 1: Title
- Event Governance Framework for BioPro
- Patient Safety Through Automated Event Management

### Slide 2: The Problem
- Current event governance gaps
- Risk of silently dropped safety-critical events
- Schema drift causing production failures
- Manual coordination overhead

### Slide 3: Patient Safety Impact
- Quarantine event dropped → unsuitable product released
- Test result exception lost → disease transmission risk
- FDA compliance requirements for event audit trails

### Slide 4: Solution Architecture
- High-level diagram
- Schema Registry (single source of truth)
- DLQ processing (zero tolerance for lost events)
- EventCatalog (living documentation)
- CI/CD automation (validate before deploy)

### Slides 5-9: Live Demo
- One slide per scenario
- Annotated screenshots
- Expected outcomes highlighted

### Slide 10: Business Value
- FDA compliance enabled
- Patient safety ensured
- Developer productivity increased
- Production incidents reduced

### Slide 11: Production Roadmap
- High-level phases (no dates)
- Key milestones
- Success criteria

### Slide 12: Questions

---

## Definition of Done

- [ ] Demo data generation script working
- [ ] Environment reset script tested
- [ ] Health check script validated
- [ ] Presentation slide deck complete and reviewed
- [ ] Demo script written with timing verified
- [ ] All 5 demo scenarios tested successfully
- [ ] Practice demo completed with stakeholder feedback
- [ ] Backup plans documented for common failures
- [ ] Demo environment documented (setup, teardown)
- [ ] All scripts checked into repository
- [ ] README created with demo instructions

---

## Demo Checklist (Day-of)

**1 Hour Before**:
- [ ] Start POC environment
- [ ] Run health check script
- [ ] Generate demo data
- [ ] Test each scenario once
- [ ] Verify EventCatalog loading
- [ ] Prepare backup slides/videos

**15 Minutes Before**:
- [ ] Final health check
- [ ] Browser tabs open (EventCatalog, Schema Registry UI)
- [ ] Terminal windows positioned
- [ ] Demo script printed or on second screen
- [ ] Water and clicker ready

**After Demo**:
- [ ] Capture questions and feedback
- [ ] Save interesting scenarios/questions for FAQ
- [ ] Note any technical issues for improvement

---

## Risk & Mitigation

**Risk**: Network issues during live demo
- **Mitigation**: Record backup video of each scenario
- **Mitigation**: Have screenshots of expected outputs
- **Mitigation**: Practice "Plan B" presentation flow

**Risk**: Demo environment fails to start
- **Mitigation**: Start environment 1 hour early
- **Mitigation**: Health check script identifies issues early
- **Mitigation**: Document quick fixes for common issues

**Risk**: Stakeholders don't understand technical concepts
- **Mitigation**: Use business language in talking points
- **Mitigation**: Lead with patient safety, not technology
- **Mitigation**: Prepare analogies for technical concepts

**Risk**: Demo runs long or short
- **Mitigation**: Practice and time demo multiple times
- **Mitigation**: Have optional "deep dive" scenarios
- **Mitigation**: Build in buffer time for questions

---

**Labels**: demo, presentation, stakeholder-communication, proof-of-concept
**Created By**: Melvin Jones
