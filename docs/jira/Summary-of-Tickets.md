# Event Governance Framework - Jira Stories

This directory contains detailed Jira story tickets for implementing the Event Governance Framework for FDA Compliance enabler.

## Parent Epic

**[EPIC: Event Governance Framework for FDA Compliance](./JIRA-EPIC-EVENT-GOVERNANCE.md)**
- High-level strategic enabler emphasizing patient safety and FDA compliance
- Business value: Prevent dropped safety-critical events (quarantine, test results)
- Includes 13 acceptance criteria and benefit hypothesis

---

## Child Stories

### Infrastructure & Core Components

#### [ST-1063: Schema Registry Integration](./ST-1063-Schema-Registry-Integration.md)
- **Story Points**: 5
- **Priority**: High
- **Component**: Schema Registry
- **Summary**: Deploy Confluent Schema Registry and integrate with BioPro services for centralized schema management with automatic validation
- **Key Features**:
  - Schema Registry deployment
  - Avro serialization with schema IDs
  - Backward compatibility validation
  - Producer/consumer integration
- **Deliverables**: Schema Registry running, 5+ schemas registered, producer/consumer integration working

#### [ST-1062: Dead Letter Queue Processing Framework](./ST-1062-Dead-Letter-Queue-Processing-Framework.md)
- **Story Points**: 5
- **Priority**: Highest (Patient Safety Critical)
- **Component**: DLQ Framework
- **Summary**: Implement comprehensive DLQ processing with AbstractListener base class to ensure zero tolerance for lost safety-critical events
- **Key Features**:
  - AbstractListener base class for systematic DLQ handling
  - Retry policies with exponential backoff
  - Failure context preservation
  - Critical alerting for safety events
- **Deliverables**: AbstractListener published, DLQ topics provisioned, retry policies working, monitoring integrated

---

### Automation & Tooling

#### [ST-1064: Avro Schema Extraction from Java Code](./ST-1064-Avro-Schema-Extraction-from-Java-Code.md)
- **Story Points**: 3
- **Priority**: High
- **Component**: CI/CD Automation
- **Summary**: Develop Python tool to automatically extract Avro schemas from Java event classes, eliminating manual schema maintenance
- **Key Features**:
  - Java code scanning and parsing
  - Java-to-Avro type mapping
  - Event envelope generation
  - Command-line interface
- **Deliverables**: Extraction tool working with 3+ event types, all Java types mapped, CLI functional

#### [ST-1068: CI/CD Event Schema Validation Pipeline](./ST-1068-CI-CD-Event-Schema-Validation-Pipeline.md)
- **Story Points**: 5
- **Priority**: High
- **Component**: CI/CD Automation
- **Summary**: Implement GitHub Actions pipeline to automatically validate schema compatibility on pull requests and block breaking changes
- **Key Features**:
  - Automatic schema extraction on PR
  - Schema comparison with Registry
  - Backward compatibility validation
  - PR comments with change summary
  - Auto-registration on merge
- **Deliverables**: Pipeline running on PRs, breaking changes blocked, compatible changes auto-registered

---

### Documentation & Discovery

#### [ST-1067: EventCatalog Platform Deployment](./ST-1067-EventCatalog-Platform-Deployment.md)
- **Story Points**: 3
- **Priority**: Medium
- **Component**: Event Documentation
- **Summary**: Deploy EventCatalog platform with Schema Registry integration for self-service event discovery and documentation
- **Key Features**:
  - EventCatalog deployment
  - Schema Registry integration
  - Event documentation pages
  - Service dependency visualization
  - Event search and discovery
- **Deliverables**: EventCatalog accessible, 5+ events documented, NodeGraph working, search functional

#### [ST-1065: EventCatalog Schema Registry Plugin](./ST-1065-EventCatalog-Schema-Registry-Plugin.md)
- **Story Points**: 5
- **Priority**: Medium
- **Component**: EventCatalog Integration
- **Summary**: Develop custom plugin to automatically synchronize EventCatalog with Schema Registry, keeping documentation current
- **Key Features**:
  - Automatic schema fetching and parsing
  - Event documentation generation
  - Sample payload generation
  - Service relationship mapping
  - Incremental synchronization
- **Deliverables**: Plugin published, auto-sync working, complete field extraction, sample generation functional

#### [ST-1066: EventCatalog Platform Upgrade and Enhancement](./ST-1066-EventCatalog-Platform-Upgrade-and-Enhancement.md)
- **Story Points**: 3
- **Priority**: Low
- **Component**: Event Documentation
- **Summary**: Upgrade EventCatalog to latest version and customize event detail pages with complete schema fields, sample payloads, and schema downloads
- **Key Features**:
  - Version upgrade to latest stable
  - **Event detail page customization with complete schema fields**
  - **Automated sample event payload generation**
  - **Schema download links (no inline schema JSON)**
  - **Python script to update 80+ event pages from Schema Registry**
  - Enhanced search and discovery
  - Improved NodeGraph visualization
  - Schema version management UI
  - BioPro branding customization
  - Performance optimization
- **Deliverables**: Upgraded EventCatalog, customized event pages with complete schema info, sample payloads generated, script documented, enhanced features working, branding applied

---

### POC Integration

#### [ST-1069: Skeleton Service Integration for POC](./ST-1069-Skeleton-Service-Integration-for-POC.md)
- **Story Points**: 3
- **Priority**: Medium
- **Component**: POC Services
- **Summary**: Integrate skeleton Orders, Collections, and Manufacturing services to demonstrate end-to-end event flow with governance
- **Key Features**:
  - Three skeleton services (Orders, Collections, Manufacturing)
  - Kafka + Schema Registry integration
  - AbstractListener for DLQ handling
  - Docker Compose integration
  - End-to-end event flow
- **Deliverables**: Three services running, event flow working, DLQ integration tested, EventCatalog showing relationships

#### [ST-1070: POC Documentation Package](./ST-1070-POC-Documentation-Package.md)
- **Story Points**: 3
- **Priority**: Medium
- **Component**: Documentation
- **Summary**: Create comprehensive documentation covering architecture, setup, operations, and production readiness
- **Key Features**:
  - Architecture overview with diagrams
  - Quick start guide
  - Demo script for stakeholders
  - Schema management guide
  - DLQ operations runbook
  - Production readiness assessment
- **Deliverables**: All documentation complete, quick start tested, demo script validated, runbooks verified

#### [ST-1072: POC Demo Preparation and Presentation Assets](./ST-1072-POC-Demo-Preparation.md)
- **Story Points**: 3
- **Priority**: Medium
- **Component**: Demo/Presentation
- **Summary**: Prepare polished demo environment with automated scenarios, presentation materials, and recovery procedures
- **Key Features**:
  - Automated demo data generation
  - Environment reset capability
  - Presentation slide deck
  - Demo script with talking points
  - Five interactive scenarios
  - Health check automation
- **Deliverables**: Demo data script working, presentation deck complete, all scenarios tested, backup plans ready

---

### Operations

#### [ST-1071: Event Governance Monitoring and Observability](./ST-1071-Event-Governance-Monitoring-and-Observability.md)
- **Story Points**: 5
- **Priority**: High (Patient Safety Critical)
- **Component**: Monitoring
- **Summary**: Implement comprehensive monitoring with critical alerting for safety-critical event failures
- **Key Features**:
  - Kafka health monitoring
  - Schema Registry monitoring
  - DLQ monitoring with critical alerts
  - Event processing metrics
  - Grafana dashboards
  - Multi-channel alerting (email, Slack, PagerDuty)
- **Deliverables**: Prometheus deployed, 4+ dashboards created, alerts firing correctly, critical safety alerts configured

---

## Story Summary

| Story | Points | Priority | Status | Component |
|-------|--------|----------|--------|-----------|
| ST-1062: Dead Letter Queue Processing Framework | 5 | Highest | To Do | DLQ Framework |
| ST-1063: Schema Registry Integration | 5 | High | To Do | Schema Registry |
| ST-1064: Avro Schema Extraction from Java Code | 3 | High | To Do | CI/CD Automation |
| ST-1065: EventCatalog Schema Registry Plugin | 5 | Medium | To Do | EventCatalog Integration |
| ST-1066: EventCatalog Platform Upgrade and Enhancement | 3 | Low | To Do | Event Documentation |
| ST-1067: EventCatalog Platform Deployment | 3 | Medium | To Do | Event Documentation |
| ST-1068: CI/CD Event Schema Validation Pipeline | 5 | High | To Do | CI/CD Automation |
| ST-1069: Skeleton Service Integration for POC | 3 | Medium | To Do | POC Services |
| ST-1070: POC Documentation Package | 3 | Medium | To Do | Documentation |
| ST-1071: Event Governance Monitoring and Observability | 5 | High | To Do | Monitoring |
| ST-1072: POC Demo Preparation | 3 | Medium | To Do | Demo/Presentation |

**Total Story Points**: 43

---

## Implementation Sequence Recommendation

### Phase 1: Foundation (18 points)
1. **ST-1063**: Schema Registry Integration (5 points)
2. **ST-1062**: DLQ Processing Framework (5 points)
3. **ST-1064**: Avro Schema Extraction from Java Code (3 points)
4. **ST-1067**: EventCatalog Platform Deployment (3 points)
5. **ST-1071**: Event Governance Monitoring and Observability (5 points) - Can run in parallel with others

**Goal**: Establish core infrastructure and safety mechanisms

### Phase 2: Integration (9 points)
6. **ST-1069**: Skeleton Service Integration for POC (3 points)
7. **ST-1068**: CI/CD Event Schema Validation Pipeline (5 points)
8. **ST-1065**: EventCatalog Schema Registry Plugin (5 points) - Can start in parallel with ST-1068

**Goal**: Demonstrate end-to-end capabilities

### Phase 3: Polish (9 points)
9. **ST-1070**: POC Documentation Package (3 points)
10. **ST-1072**: POC Demo Preparation (3 points)
11. **ST-1066**: EventCatalog Platform Upgrade and Enhancement (3 points) - Optional, can be deferred

**Goal**: Prepare for stakeholder demonstration

---

## Dependencies

```
ST-1063 (Schema Registry)
    ├── ST-1062 (DLQ) - Needs Kafka/Schema Registry
    ├── ST-1064 (Schema Extraction) - Needs Schema Registry
    ├── ST-1067 (EventCatalog) - Needs Schema Registry
    └── ST-1069 (Services) - Needs Schema Registry

ST-1062 (DLQ)
    └── ST-1069 (Services) - Services use AbstractListener

ST-1064 (Schema Extraction)
    └── ST-1068 (CI/CD) - CI/CD uses extraction tool

ST-1067 (EventCatalog)
    ├── ST-1065 (Plugin) - Plugin extends EventCatalog
    └── ST-1066 (Upgrade) - Upgrade improves EventCatalog

ST-1069 (Services)
    ├── ST-1070 (Documentation) - Documents services
    └── ST-1072 (Demo) - Demo uses services

ST-1071 (Monitoring)
    └── Can run parallel with any phase
```

---

## Patient Safety Focus

The following stories directly impact patient safety and should be prioritized:

- **ST-1062**: Dead Letter Queue Processing Framework - **Highest Priority**
  - Prevents lost quarantine/test result events
  - Zero tolerance for dropped safety-critical events

- **ST-1071**: Event Governance Monitoring and Observability - **High Priority**
  - Critical alerting for safety-critical event failures
  - Operational visibility into event processing health

- **ST-1063**: Schema Registry Integration - **High Priority**
  - Prevents schema-related production failures
  - Ensures all services use validated schemas

---

## FDA Compliance Considerations

All stories contribute to FDA 510(k) compliance requirements:

- **Schema Registry**: Documented schema evolution with versioning
- **DLQ Framework**: Audit trail for all event processing failures
- **Monitoring**: Operational oversight with alerting for anomalies
- **EventCatalog**: Living documentation of system architecture
- **CI/CD Validation**: Systematic validation of changes before deployment

---

## Notes

- All stories written as if work needs to be done (not already completed)
- Stories focus on business value and patient safety
- Technical details provided for implementation guidance
- Each story includes acceptance criteria, tasks, testing strategy, and DoD
- Stories sized for 3-5 points for manageable sprints
- Documentation deliverables included in each story

---

**Created By**: Melvin Jones
**Last Updated**: 2025-11-17
**Epic Link**: Event Governance Framework for FDA Compliance
