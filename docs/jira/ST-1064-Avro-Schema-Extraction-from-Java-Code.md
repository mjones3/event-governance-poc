# Story: Avro Schema Extraction from Java Code

**Story Points**: 3
**Priority**: High
**Epic Link**: Event Governance Framework for FDA Compliance
**Type**: Technical Story
**Component**: CI/CD Automation

---

## User Story

**As a** BioPro developer
**I want** Avro schemas automatically extracted from Java event classes
**So that** schemas stay synchronized with code and manual schema management is eliminated

---

## Description

Develop automated tool to extract Avro schemas directly from Java domain event classes. Tool should parse Java code, identify event classes and their payload structures, convert Java types to Avro types, and generate valid Avro schema files (.avsc) ready for registration in Schema Registry.

### Background
Currently, developers must manually create and maintain Avro schemas separately from Java code, leading to:
- Schema drift when code changes but schemas aren't updated
- Double maintenance burden (Java code + Avro schemas)
- Human error in schema definitions
- Delayed schema updates blocking deployments

This tool automates schema generation from the authoritative source (Java code).

---

## Acceptance Criteria

**AC1: Java Code Scanning**
- GIVEN a BioPro module source directory
- WHEN extraction tool is run
- THEN tool scans for Java event classes in `**/domain/event/**/*.java`
- AND tool identifies payload classes in `**/domain/event/payload/*.java`
- AND tool parses Java class structure including fields and types

**AC2: Type Mapping**
- GIVEN Java field types in event payload classes
- WHEN schemas are generated
- THEN Java types are correctly mapped to Avro types:
  - `String` → `string`
  - `Integer`, `int` → `int`
  - `Long`, `long` → `long`
  - `Boolean`, `boolean` → `boolean`
  - `UUID` → `string` with logical type `uuid`
  - `Instant` → `long` with logical type `timestamp-millis`
  - `List<T>` → `array` with items type
  - `Map<K,V>` → `map` with values type
  - Enum → Avro `enum` with symbols
  - Custom Records → Avro `record` (nested)

**AC3: Schema Annotation Support**
- GIVEN Java classes with `@Schema` annotations from Avro library
- WHEN schemas are extracted
- THEN annotation values are used for:
  - Schema name (`@Schema(name="...")`)
  - Field documentation (`@AvroDoc("...")`)
  - Default values (`@AvroDefault("...")`)
  - Field aliases (`@AvroAlias("...")`)
- AND annotations take precedence over inferred values

**AC4: Event Envelope Generation**
- GIVEN an event payload class
- WHEN schema is generated
- THEN complete event schema includes:
  - `eventId` field (UUID, required)
  - `occurredOn` field (timestamp-millis, required)
  - `eventType` field (string, with default value)
  - `eventVersion` field (string, with default value)
  - `payload` field (nested record with payload structure)
- AND envelope follows BioPro event standards

**AC5: Schema File Output**
- GIVEN extracted schemas
- WHEN generation completes
- THEN Avro schema files are written to output directory
- AND files are named `{EventName}.avsc`
- AND files contain valid JSON-formatted Avro schemas
- AND schemas can be directly registered to Schema Registry

---

## Technical Details

### Tool Implementation (Python)
```python
#!/usr/bin/env python3
"""
Extract Avro schemas from BioPro Java event classes
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Optional

def extract_schemas(source_dir: Path, output_dir: Path):
    """
    Scan source directory for Java event classes and generate Avro schemas
    """
    # Find event payload classes
    payload_files = source_dir.rglob("**/domain/event/payload/*.java")

    for java_file in payload_files:
        # Parse Java class
        schema = parse_java_class(java_file)

        # Generate Avro schema
        avro_schema = generate_avro_schema(schema)

        # Write schema file
        output_file = output_dir / f"{schema['name']}.avsc"
        with open(output_file, 'w') as f:
            json.dump(avro_schema, f, indent=2)

def parse_java_class(java_file: Path) -> Dict:
    """Parse Java class and extract schema information"""
    # Implementation details...
    pass

def map_java_type_to_avro(java_type: str) -> any:
    """Map Java type to Avro type"""
    type_mapping = {
        'String': 'string',
        'Integer': 'int',
        'int': 'int',
        'Long': 'long',
        'long': 'long',
        'Boolean': 'boolean',
        'boolean': 'boolean',
        'UUID': {'type': 'string', 'logicalType': 'uuid'},
        'Instant': {'type': 'long', 'logicalType': 'timestamp-millis'},
        # ... more mappings
    }
    return type_mapping.get(java_type, 'string')
```

### Command Line Interface
```bash
python extract_schemas_from_java.py \
  --source-dir /path/to/biopro/module/src/main/java \
  --output-dir ./extracted-schemas \
  --namespace com.biopro.events.orders
```

---

## Implementation Tasks

### 1. Java Parser Implementation (3 hours)
- [ ] Implement file scanning for event classes
- [ ] Parse Java class structure (fields, types, annotations)
- [ ] Extract field names and types
- [ ] Handle nested classes
- [ ] Parse @Schema annotations

### 2. Type Mapping Logic (2 hours)
- [ ] Implement Java-to-Avro type mapping
- [ ] Handle primitive types
- [ ] Handle complex types (List, Map, etc.)
- [ ] Handle UUID and Instant with logical types
- [ ] Handle enum types
- [ ] Handle nested record types

### 3. Event Envelope Generation (2 hours)
- [ ] Create standard event envelope structure
- [ ] Add eventId, occurredOn, eventType, eventVersion fields
- [ ] Nest payload as record type
- [ ] Apply BioPro naming conventions
- [ ] Add documentation strings

### 4. Schema File Output (1 hour)
- [ ] Generate valid Avro JSON format
- [ ] Write files to output directory
- [ ] Add pretty-printing (indentation)
- [ ] Validate generated schemas
- [ ] Handle file naming

### 5. CLI and Configuration (2 hours)
- [ ] Implement command-line argument parsing
- [ ] Add source directory configuration
- [ ] Add output directory configuration
- [ ] Add namespace override option
- [ ] Add dry-run mode for testing
- [ ] Add verbose logging option

---

## Testing Strategy

### Unit Tests
- Java type to Avro type mapping
- Annotation parsing
- Nested structure handling
- File naming conventions

### Integration Tests
- Extract schemas from sample BioPro event classes
- Validate generated schemas against Avro spec
- Register generated schemas to Schema Registry
- Verify schemas match manually-created versions

### Test Cases
- Simple event with primitive types
- Event with nested records
- Event with collections (List, Map)
- Event with enums
- Event with @Schema annotations
- Event with optional fields (defaults)

---

## Dependencies

### Python Libraries
```bash
pip install requests  # For Schema Registry API calls (optional)
```

### Sample Java Events for Testing
- OrderCreatedEvent
- CollectionReceivedEvent
- ApheresisPlasmaProductCreatedEvent

---

## Definition of Done

- [ ] Tool successfully extracts schemas from at least 3 different BioPro event classes
- [ ] All Java types correctly mapped to Avro types
- [ ] Generated schemas are valid Avro JSON
- [ ] Generated schemas can be registered to Schema Registry
- [ ] @Schema annotations are honored
- [ ] Event envelope structure matches BioPro standards
- [ ] CLI interface working with all options
- [ ] Unit tests >80% coverage
- [ ] Documentation complete (usage guide with examples)
- [ ] Sample schemas generated and validated

---

## Documentation Deliverables

- Tool usage guide with examples
- Java-to-Avro type mapping reference
- Supported annotation reference
- Troubleshooting guide for common issues
- Example schemas for each BioPro domain

---

## Future Enhancements

- Support for schema evolution hints in comments
- Integration with Maven build process
- Automatic schema registration after extraction
- Schema diff tool to show changes
- Support for cross-module event dependencies

---

## Risk & Mitigation

**Risk**: Tool may not handle all Java type variations
- **Mitigation**: Start with common types, expand based on real usage
- **Mitigation**: Provide manual override mechanism for edge cases

**Risk**: Generated schemas may differ from manually-created ones
- **Mitigation**: Compare generated vs. manual for initial events
- **Mitigation**: Validate schemas before registration

**Risk**: Java code changes may break schema extraction
- **Mitigation**: Unit tests cover various Java patterns
- **Mitigation**: Tool fails fast with clear error messages

---

**Labels**: schema-extraction, automation, avro, ci-cd, proof-of-concept
**Created By**: Melvin Jones
