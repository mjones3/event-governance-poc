# Story: EventCatalog Platform Deployment

**Story Points**: 3
**Priority**: Medium
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: Event Documentation

---

## User Story

**As a** BioPro developer
**I want** self-service access to live event documentation
**So that** I can discover events, understand schemas, and integrate with other services without manual coordination

---

## Description

Deploy EventCatalog platform to provide real-time, self-updating documentation of all BioPro events, schemas, and service relationships. Platform should automatically synchronize with Schema Registry to maintain current event catalog with schema fields, sample payloads, and service dependency visualization.

### Background
BioPro currently lacks centralized event documentation, leading to:
- Developers unable to discover available events
- Outdated documentation creating integration issues
- Manual effort to document each event change
- No visibility into service dependencies
- Difficult onboarding for new team members

EventCatalog provides living documentation that stays synchronized with actual system state.

---

## Acceptance Criteria

**AC1: EventCatalog Deployment**
- GIVEN infrastructure requirements for EventCatalog
- WHEN platform is deployed
- THEN EventCatalog is accessible via web browser at http://eventcatalog:3000
- AND platform loads successfully with BioPro branding
- AND homepage shows all BioPro domains (Orders, Collections, Manufacturing, Distribution)

**AC2: Schema Registry Integration**
- GIVEN EventCatalog is deployed
- WHEN configured to connect to Schema Registry
- THEN EventCatalog can query Schema Registry via REST API
- AND schemas are retrieved and parsed correctly
- AND schema versions are tracked and displayed
- AND schema changes trigger catalog updates

**AC3: Event Documentation Pages**
- GIVEN an event registered in Schema Registry
- WHEN viewing event in EventCatalog
- THEN event page displays:
  - Event name and description
  - Schema version and ID
  - All schema fields with types and descriptions
  - Sample event payload (auto-generated from schema)
  - Producer services
  - Consumer services
  - Domain/bounded context
- AND documentation is generated automatically from schema

**AC4: Service Dependency Visualization**
- GIVEN events flowing between BioPro services
- WHEN viewing service page in EventCatalog
- THEN NodeGraph visualization shows:
  - Services as nodes
  - Events as edges
  - Producer/consumer relationships
  - Event flow direction
- AND graph is interactive (clickable nodes/edges)
- AND graph updates automatically with schema changes

**AC5: Event Discovery**
- GIVEN all BioPro events documented in EventCatalog
- WHEN developer searches for events
- THEN search works by:
  - Event name
  - Service name
  - Domain name
  - Schema field names
- AND search results link to event/service pages
- AND search is fast and responsive

---

## Technical Details

### EventCatalog Stack
- **Platform**: EventCatalog v1.0+
- **Runtime**: Node.js 18+
- **Configuration**: MDX files for events/services
- **Plugins**: Avro schema integration

### Deployment Architecture
```yaml
# docker-compose.yml
eventcatalog:
  build:
    context: ./eventcatalog
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
  environment:
    SCHEMA_REGISTRY_URL: http://schema-registry:8081
    PORT: 3000
  volumes:
    - ./eventcatalog:/app
  depends_on:
    - schema-registry
```

### EventCatalog Configuration
```javascript
// eventcatalog.config.js
module.exports = {
  title: 'BioPro Event Catalog',
  tagline: 'Event-Driven Architecture Documentation',
  organizationName: 'BioPro',
  homepageLink: 'https://biopro.example.com',
  editUrl: 'https://github.com/biopro/event-governance/edit/main/eventcatalog',

  users: [],

  generators: [
    {
      plugin: '@eventcatalog/plugin-generator-avro',
      options: {
        schemaRegistryUrl: 'http://schema-registry:8081',
        domain: 'biopro',
        syncInterval: 300000  // 5 minutes
      }
    }
  ]
}
```

---

## Implementation Tasks

### 1. EventCatalog Setup (2 hours)
- [ ] Initialize EventCatalog project
- [ ] Configure BioPro branding (logo, colors, title)
- [ ] Set up domain structure (Orders, Collections, Manufacturing, Distribution)
- [ ] Create initial event and service folders
- [ ] Configure homepage

### 2. Schema Registry Integration (3 hours)
- [ ] Install Avro plugin for EventCatalog
- [ ] Configure Schema Registry connection
- [ ] Test schema retrieval via plugin
- [ ] Configure auto-sync interval
- [ ] Verify schema updates trigger catalog refresh

### 3. Event Documentation Generation (3 hours)
- [ ] Create script to generate event MDX files from schemas
- [ ] Parse Avro schemas and extract field information
- [ ] Generate sample event payloads from schemas
- [ ] Create event pages with schema fields table
- [ ] Add download links for Avro schema files

### 4. Service Documentation (2 hours)
- [ ] Create service MDX files for BioPro modules
- [ ] Document producer/consumer relationships
- [ ] Add service descriptions and metadata
- [ ] Configure NodeGraph for each service
- [ ] Link events to services

### 5. Docker Deployment (2 hours)
- [ ] Create Dockerfile for EventCatalog
- [ ] Add EventCatalog to docker-compose.yml
- [ ] Configure environment variables
- [ ] Test deployment and accessibility
- [ ] Configure volume mounts for persistence

---

## Testing Strategy

### Manual Testing
- [ ] Browse to EventCatalog URL and verify it loads
- [ ] Navigate to event pages and verify content
- [ ] Click NodeGraph and verify visualization works
- [ ] Search for events and verify results
- [ ] Update schema in registry and verify catalog updates

### Integration Testing
- [ ] Deploy full stack (Kafka, Schema Registry, EventCatalog)
- [ ] Register new event schema
- [ ] Verify EventCatalog shows new event within sync interval
- [ ] Update schema version
- [ ] Verify EventCatalog shows new version

---

## Dependencies

### Infrastructure
- Node.js 18+ runtime
- Docker for containerization
- Network access to Schema Registry

### NPM Dependencies
```json
{
  "dependencies": {
    "@eventcatalog/core": "^1.0.0",
    "@eventcatalog/plugin-generator-avro": "^1.0.0"
  }
}
```

---

## Definition of Done

- [ ] EventCatalog deployed and accessible via browser
- [ ] Connected to Schema Registry successfully
- [ ] At least 5 BioPro events documented automatically
- [ ] Event pages show complete schema information
- [ ] Sample payloads generated for all events
- [ ] Service pages created for at least 3 BioPro services
- [ ] NodeGraph visualization working
- [ ] Event search functional
- [ ] Auto-sync working (catalog updates when schemas change)
- [ ] Documentation created (how to add events/services, how to search)

---

## Documentation Deliverables

- EventCatalog deployment guide
- How to add new events to catalog
- How to update service documentation
- How to use search and discovery features
- Troubleshooting guide

---

## Future Enhancements

- SSO integration for access control
- Schema approval workflow
- Event versioning timeline visualization
- API documentation integration
- Slack/Teams notifications for schema changes

---

## Risk & Mitigation

**Risk**: EventCatalog could become out of sync with Schema Registry
- **Mitigation**: Configure short sync interval (5 minutes)
- **Mitigation**: Monitor sync job health and alert on failures

**Risk**: Performance issues with large number of events
- **Mitigation**: EventCatalog is static-site generated (fast)
- **Mitigation**: Incremental builds only regenerate changed pages

**Risk**: Adoption - developers may not use the catalog
- **Mitigation**: Make catalog the official source of truth
- **Mitigation**: Include catalog links in developer onboarding
- **Mitigation**: Require catalog updates in PR process

---

**Labels**: eventcatalog, documentation, self-service, proof-of-concept
**Created By**: Melvin Jones
