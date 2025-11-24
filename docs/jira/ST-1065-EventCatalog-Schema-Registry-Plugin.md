# Story: EventCatalog Schema Registry Plugin

**Story Points**: 5
**Priority**: Medium
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: EventCatalog Integration

---

## User Story

**As a** BioPro developer
**I want** EventCatalog to automatically synchronize with Schema Registry
**So that** event documentation stays current without manual updates and I can discover events with confidence

---

## Description

Develop custom EventCatalog plugin to automatically fetch schemas from Confluent Schema Registry, generate event documentation pages with complete field information, create sample payloads, and maintain service dependency mappings. Plugin should run on configurable schedule to keep EventCatalog synchronized with Schema Registry as single source of truth.

### Background
Manual event documentation becomes stale quickly, leading to:
- Developers using outdated schema information
- Integration failures due to incorrect field expectations
- Time wasted maintaining duplicate documentation
- Lost trust in documentation platform

This plugin automates synchronization between Schema Registry (authoritative schema source) and EventCatalog (developer-facing documentation), ensuring documentation accuracy.

---

## Acceptance Criteria

**AC1: Schema Registry Connection**
- GIVEN EventCatalog plugin configured with Schema Registry URL
- WHEN plugin initialization occurs
- THEN plugin successfully connects to Schema Registry API
- AND plugin authenticates if credentials configured
- AND connection health is validated
- AND connection errors are logged with helpful messages

**AC2: Schema Fetching and Parsing**
- GIVEN schemas registered in Schema Registry
- WHEN plugin sync runs
- THEN plugin fetches all subjects matching configured pattern
- AND plugin retrieves latest version for each subject
- AND plugin parses Avro schema JSON structure
- AND plugin extracts complete field information (name, type, required, default, doc)
- AND plugin handles nested records, enums, arrays, maps

**AC3: Event Documentation Generation**
- GIVEN parsed Avro schema
- WHEN plugin generates event documentation
- THEN event MDX file is created/updated with:
  - Event name and description from schema
  - Schema version and ID
  - Complete field table with types and descriptions
  - Generated sample event payload
  - Download link for Avro schema file
  - Producer/consumer service references
  - Domain classification
- AND generated documentation follows EventCatalog conventions
- AND existing manual edits are preserved (if possible)

**AC4: Sample Event Generation**
- GIVEN event schema with fields
- WHEN plugin generates sample payload
- THEN sample includes realistic data:
  - UUIDs for ID fields
  - ISO timestamps for date/time fields
  - Appropriate enum values
  - Nested structures populated
  - Arrays with sample items
- AND sample is valid according to schema
- AND sample is formatted as readable JSON

**AC5: Service Relationship Mapping**
- GIVEN event schemas with naming conventions
- WHEN plugin processes schemas
- THEN plugin infers producer services from subject naming
- AND plugin maps events to service pages
- AND service pages are updated with event relationships
- AND NodeGraph visualization data is generated

**AC6: Incremental Synchronization**
- GIVEN EventCatalog with existing event pages
- WHEN plugin sync runs
- THEN only changed schemas trigger updates
- AND unchanged events are not regenerated
- AND sync completes quickly (< 30 seconds for 100 events)
- AND sync reports what was added/updated/deleted

---

## Technical Details

### Plugin Architecture
```javascript
// eventcatalog-plugin-schema-registry/index.js
module.exports = function schemaRegistryPlugin(config) {
  return {
    name: '@biopro/eventcatalog-plugin-schema-registry',

    async init() {
      // Initialize Schema Registry client
      this.client = createRegistryClient(config.registryUrl);
    },

    async sync() {
      // Fetch all subjects from Schema Registry
      const subjects = await this.fetchSubjects();

      // Process each subject
      for (const subject of subjects) {
        const schema = await this.fetchLatestSchema(subject);
        const event = this.parseSchema(schema);
        const sample = this.generateSample(event);

        await this.writeEventPage(event, sample);
        await this.updateServiceMappings(event);
      }

      return {
        added: this.added.length,
        updated: this.updated.length,
        deleted: this.deleted.length
      };
    }
  };
};
```

### Configuration (eventcatalog.config.js)
```javascript
module.exports = {
  title: 'BioPro Event Catalog',

  plugins: [
    [
      '@biopro/eventcatalog-plugin-schema-registry',
      {
        registryUrl: process.env.SCHEMA_REGISTRY_URL || 'http://localhost:8081',
        subjectPattern: 'biopro.*-value',
        syncInterval: 300000, // 5 minutes
        domainMapping: {
          'biopro.orders': 'Orders',
          'biopro.collections': 'Collections',
          'biopro.manufacturing': 'Manufacturing',
          'biopro.distribution': 'Distribution'
        },
        sampleGeneration: {
          enableRealisticData: true,
          maxArrayItems: 3,
          maxNestingDepth: 5
        }
      }
    ]
  ]
};
```

### Schema Parsing Logic
```javascript
function parseAvroSchema(avroSchema) {
  const fields = [];

  function extractFields(schema, prefix = '') {
    if (schema.type === 'record') {
      for (const field of schema.fields) {
        const fieldName = prefix ? `${prefix}.${field.name}` : field.name;
        const fieldInfo = {
          name: fieldName,
          type: getFieldType(field.type),
          required: !isOptional(field),
          default: field.default,
          description: field.doc || ''
        };

        fields.push(fieldInfo);

        // Handle nested records
        if (field.type.type === 'record') {
          extractFields(field.type, fieldName);
        }
      }
    }
  }

  extractFields(avroSchema);
  return fields;
}

function getFieldType(type) {
  if (typeof type === 'string') return type;
  if (Array.isArray(type)) return type.filter(t => t !== 'null').join(' | ');
  if (type.type === 'array') return `array<${getFieldType(type.items)}>`;
  if (type.type === 'map') return `map<string, ${getFieldType(type.values)}>`;
  if (type.type === 'enum') return `enum (${type.symbols.join(', ')})`;
  if (type.logicalType) return type.logicalType;
  return type.type;
}
```

### Sample Generation Logic
```javascript
function generateSampleEvent(fields) {
  const sample = {};

  for (const field of fields) {
    const value = generateFieldValue(field);
    setNestedValue(sample, field.name, value);
  }

  return sample;
}

function generateFieldValue(field) {
  // UUID fields
  if (field.name.toLowerCase().includes('id') && field.type === 'string') {
    return crypto.randomUUID();
  }

  // Timestamp fields
  if (field.type === 'timestamp-millis' || field.name.includes('Date')) {
    return new Date().toISOString();
  }

  // Enum fields
  if (field.type.startsWith('enum')) {
    const symbols = extractEnumSymbols(field.type);
    return symbols[0];
  }

  // Type-based defaults
  switch (field.type) {
    case 'string': return 'sample-value';
    case 'int': return 42;
    case 'long': return 1234567890;
    case 'boolean': return true;
    case 'double': return 3.14;
    default: return null;
  }
}
```

---

## Implementation Tasks

### 1. Plugin Project Setup (2 hours)
- [ ] Initialize npm project for plugin
- [ ] Set up TypeScript configuration
- [ ] Add Schema Registry client dependency
- [ ] Create plugin interface structure
- [ ] Set up testing framework
- [ ] Configure ESLint and Prettier

### 2. Schema Registry Client Integration (3 hours)
- [ ] Implement Schema Registry API client
- [ ] Add authentication support
- [ ] Implement subject listing
- [ ] Implement schema fetching by version
- [ ] Add error handling and retries
- [ ] Test against real Schema Registry

### 3. Schema Parsing Implementation (4 hours)
- [ ] Implement Avro schema parser
- [ ] Handle primitive types
- [ ] Handle complex types (arrays, maps, records)
- [ ] Handle enums with symbols
- [ ] Handle logical types (UUID, timestamp)
- [ ] Extract field documentation
- [ ] Test with BioPro event schemas

### 4. Sample Event Generation (3 hours)
- [ ] Implement field value generation
- [ ] Add realistic data generation (UUIDs, timestamps)
- [ ] Handle nested structures
- [ ] Handle arrays with sample items
- [ ] Ensure generated samples are valid
- [ ] Test sample generation with complex schemas

### 5. Event Documentation Writer (4 hours)
- [ ] Implement MDX file generation
- [ ] Create field table formatting
- [ ] Add sample event section
- [ ] Add schema download link
- [ ] Preserve frontmatter metadata
- [ ] Handle file updates vs. creates
- [ ] Test documentation generation

### 6. Service Relationship Mapping (3 hours)
- [ ] Implement service inference from naming
- [ ] Update service MDX files with events
- [ ] Generate NodeGraph data
- [ ] Handle producer/consumer relationships
- [ ] Test service page updates

### 7. Incremental Sync Logic (3 hours)
- [ ] Track schema versions
- [ ] Detect changes since last sync
- [ ] Skip unchanged schemas
- [ ] Report sync statistics
- [ ] Optimize for large catalogs
- [ ] Test incremental sync

### 8. Plugin Configuration (2 hours)
- [ ] Implement configuration validation
- [ ] Add domain mapping support
- [ ] Add subject pattern filtering
- [ ] Configure sync interval
- [ ] Add sample generation options
- [ ] Test various configurations

---

## Testing Strategy

### Unit Tests
- Schema parsing for all Avro types
- Sample generation for various field types
- MDX file generation and formatting
- Service relationship inference

### Integration Tests
- Connect to Schema Registry and fetch schemas
- Parse real BioPro event schemas
- Generate complete event documentation
- Update existing event pages
- Incremental sync with no changes

### End-to-End Tests
- Full sync from Schema Registry to EventCatalog
- Verify generated documentation accuracy
- Verify sample events are valid
- Verify service relationships correct
- Performance test with 100+ events

---

## Dependencies

### NPM Dependencies
```json
{
  "dependencies": {
    "@eventcatalog/sdk": "^2.0.0",
    "axios": "^1.6.0",
    "avsc": "^5.7.7",
    "js-yaml": "^4.1.0",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0"
  }
}
```

### Infrastructure
- Schema Registry running and accessible
- EventCatalog v2.0+
- Node.js 18+

---

## Definition of Done

- [ ] Plugin package created and published to npm (or internal registry)
- [ ] Plugin connects to Schema Registry successfully
- [ ] Plugin parses all BioPro event schemas correctly
- [ ] Plugin generates complete event documentation
- [ ] Plugin generates valid sample events
- [ ] Plugin updates service relationships
- [ ] Incremental sync working (only updates changed schemas)
- [ ] Plugin integrated into EventCatalog POC
- [ ] Full sync completes in < 1 minute for 100 events
- [ ] Unit tests >80% coverage
- [ ] Integration tests passing
- [ ] Plugin configuration documented
- [ ] README created with usage examples

---

## Documentation Deliverables

- Plugin installation and configuration guide
- Plugin architecture documentation
- Supported Avro types reference
- Sample generation customization guide
- Troubleshooting guide
- API reference for plugin hooks

---

## Plugin Publishing

### NPM Package Structure
```
eventcatalog-plugin-schema-registry/
├── package.json
├── README.md
├── LICENSE
├── src/
│   ├── index.ts
│   ├── client.ts
│   ├── parser.ts
│   ├── generator.ts
│   └── writer.ts
├── tests/
│   ├── parser.test.ts
│   ├── generator.test.ts
│   └── integration.test.ts
└── examples/
    └── eventcatalog.config.js
```

### Version Strategy
- v1.0.0: Initial release with core functionality
- v1.1.0: Add caching for performance
- v1.2.0: Add webhook support for real-time sync
- v2.0.0: Support EventCatalog v3

---

## Risk & Mitigation

**Risk**: Schema Registry changes break plugin
- **Mitigation**: Version plugin against Schema Registry API version
- **Mitigation**: Add API compatibility checks on startup

**Risk**: Large number of schemas causes slow sync
- **Mitigation**: Implement parallel schema fetching
- **Mitigation**: Use incremental sync to minimize updates

**Risk**: Plugin overwrites manual documentation edits
- **Mitigation**: Preserve custom sections in frontmatter
- **Mitigation**: Add "managed by plugin" marker
- **Mitigation**: Document sections safe to edit manually

**Risk**: Generated samples don't reflect realistic data
- **Mitigation**: Allow custom sample generators via config
- **Mitigation**: Learn from existing sample data if available

---

## Future Enhancements

- Real-time sync via Schema Registry webhooks
- Support for other schema formats (JSON Schema, Protobuf)
- Schema diff visualization in EventCatalog
- Integration with CI/CD for schema validation
- Custom template support for event pages
- Multi-registry support (dev, staging, prod)

---

**Labels**: eventcatalog, plugin, schema-registry, automation, proof-of-concept
**Created By**: Melvin Jones
