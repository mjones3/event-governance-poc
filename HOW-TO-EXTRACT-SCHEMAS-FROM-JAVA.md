# How to Automatically Extract Avro Schemas from BioPro Java Code

## Overview

The `extract_schemas_from_java.py` tool automatically inspects your BioPro Java domain event code and generates Avro schema files (.avsc).

## What It Does

1. **Scans** Java source code for domain event classes
2. **Parses** Java Record payload classes with `@Schema` annotations
3. **Converts** Java types to Avro types
4. **Generates** complete Avro schemas with event envelopes

## Installation

No installation needed! Just Python 3 (already on your system).

## Usage

### Basic Usage

```bash
python extract_schemas_from_java.py \
  --source-dir "C:\Users\MelvinJones\work\biopro\biopro-manufacturing\backend\apheresisplasma\src\main\java" \
  --output-dir extracted-biopro-schemas
```

### From POC Directory

```bash
cd C:\Users\MelvinJones\work\event-governance\poc

python extract_schemas_from_java.py \
  --source-dir "C:/Users/MelvinJones/work/biopro/biopro-manufacturing/backend/apheresisplasma/src/main/java" \
  --output-dir ./extracted-biopro-schemas
```

## What Gets Extracted

The tool looks for:

### 1. Event Payload Classes

Located in: `**/domain/event/payload/*.java`

Example:
```java
@Schema(
    name = "ApheresisPlasmaProductCreatedPayload",
    description = "Apheresis Plasma Product Created Payload"
)
public record ProductCreated(
    @Schema(name = "unitNumber", requiredMode = REQUIRED)
    String unitNumber,

    @Schema(name = "productCode")
    String productCode,

    @Schema(name = "volume")
    Volume volume
) implements Serializable {
}
```

### 2. Event Envelope Classes

Located in: `**/domain/event/*Event.java`

Example:
```java
public class ApheresisPlasmaProductCreatedEvent extends Event<ProductCreated> {
    public ApheresisPlasmaProductCreatedEvent(ProductCreated payload) {
        super(EventType.APHERESIS_PLASMA_PRODUCT_CREATED(),
              EventVersion.VERSION_1_0(),
              payload);
    }
}
```

## Generated Schema Example

For `ProductCreated.java`, the tool generates:

**File**: `ApheresisPlasmaProductCreatedEventSchema.avsc`

```json
{
  "type": "record",
  "name": "ApheresisPlasmaProductCreatedEvent",
  "namespace": "com.arcone.biopro.manufacturing.apheresisplasma.domain.event",
  "fields": [
    {
      "name": "eventId",
      "type": {"type": "string", "logicalType": "uuid"},
      "doc": "Unique identifier for this event"
    },
    {
      "name": "occurredOn",
      "type": {"type": "long", "logicalType": "timestamp-millis"},
      "doc": "Timestamp when event occurred"
    },
    {
      "name": "eventType",
      "type": "string",
      "default": "ApheresisPlasmaProductCreated"
    },
    {
      "name": "eventVersion",
      "type": "string",
      "default": "1.0"
    },
    {
      "name": "payload",
      "type": {
        "type": "record",
        "name": "ProductCreatedPayload",
        "fields": [
          {
            "name": "unitNumber",
            "type": "string",
            "doc": "Unit Number (example: W036202412345)"
          },
          {
            "name": "productCode",
            "type": "string"
          },
          {
            "name": "volume",
            "type": ["null", "Volume"],
            "default": null
          }
        ]
      }
    }
  ]
}
```

## Type Mappings

The tool automatically converts Java types to Avro types:

| Java Type | Avro Type |
|-----------|-----------|
| `String` | `"string"` |
| `Integer`, `int` | `"int"` |
| `Long`, `long` | `"long"` |
| `Boolean`, `boolean` | `"boolean"` |
| `UUID` | `{"type": "string", "logicalType": "uuid"}` |
| `ZonedDateTime` | `{"type": "long", "logicalType": "timestamp-millis"}` |
| `List<T>` | `{"type": "array", "items": T}` |
| `Map<String, V>` | `{"type": "map", "values": V}` |
| Custom types | References to nested records |

## Required vs Optional Fields

- **Required fields** (marked with `requiredMode = REQUIRED`):
  ```json
  {"name": "unitNumber", "type": "string"}
  ```

- **Optional fields** (no `requiredMode`):
  ```json
  {"name": "volume", "type": ["null", "Volume"], "default": null}
  ```

## Results from BioPro Manufacturing

Running against `biopro-manufacturing/backend/apheresisplasma` generated:

```
Found 5 event classes
Found 4 payload classes

Generated Schemas:
✓ ApheresisPlasmaProductCreatedEventSchema.avsc (23 fields)
✓ ApheresisPlasmaProductCompletedEventSchema.avsc (8 fields)
✓ ApheresisPlasmaProductUnsuitableEventSchema.avsc (6 fields)
✓ ApheresisPlasmaProductUpdatedEventSchema.avsc (0 fields)
```

## Workflow: From Java to Avro to Schema Registry

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Write Java Domain Events                                 │
│    - Create payload record classes                          │
│    - Add @Schema annotations                                │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Run Schema Extractor                                     │
│    python extract_schemas_from_java.py \                    │
│      --source-dir /path/to/java/src \                       │
│      --output-dir ./schemas                                 │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Review Generated .avsc Files                             │
│    - Verify field types                                     │
│    - Check required/optional flags                          │
│    - Review nested record references                        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Register to Schema Registry                              │
│    python register_schemas.py \                             │
│      --schemas-dir ./schemas \                              │
│      --registry http://localhost:8081                       │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Use in Spring Boot Services                              │
│    - Schema ID embedded automatically                       │
│    - SpringWolf documents from Schema Registry              │
│    - EventCatalog syncs via AsyncAPI                        │
└─────────────────────────────────────────────────────────────┘
```

## Advantages

### 1. Single Source of Truth
- Java code IS the source of truth
- Schemas automatically reflect code structure
- No manual .avsc file maintenance

### 2. @Schema Annotations Used
- Documentation extracted from annotations
- Examples included in generated schemas
- Required fields properly detected

### 3. Event Envelope Included
- Complete event structure with:
  - `eventId` (UUID)
  - `occurredOn` (timestamp)
  - `eventType` (string)
  - `eventVersion` (string)
  - `payload` (nested record)

### 4. Type Safety
- Java types → Avro types automatically
- Logical types for dates/times/UUIDs
- Optional vs required properly handled

## Limitations & Future Improvements

### Current Limitations

1. **Nested Records**: Custom types like `Volume`, `Weight`, `Step` are referenced but not fully defined
   - Tool outputs: `"type": "Volume"`
   - Need: Full nested record definitions

2. **Enums**: Value object enums not extracted
   - Example: `ProductCompletionStage` → needs `{"INTERMEDIATE", "FINAL"}`

3. **Complex Generics**: Some edge cases may not parse correctly

### Planned Improvements

1. **Recursive Type Resolution**: Automatically find and include nested record definitions
2. **Enum Extraction**: Parse value object enums and generate Avro enum types
3. **Validation**: Verify generated schemas against Avro schema validator
4. **Maven Plugin**: Integrate into build process for automatic generation

## Troubleshooting

### Issue: "No payload classes found"
**Solution**: Check that payload classes are in `domain/event/payload/` directory

### Issue: "Failed to parse record"
**Solution**: Ensure payload uses Java `record` syntax (not `class`)

### Issue: Unicode errors on Windows
**Solution**: Already fixed in latest version (removed unicode characters)

### Issue: Missing field documentation
**Solution**: Add `@Schema(description="...")` annotations to Java fields

## Example: Complete Workflow

```bash
# Step 1: Extract schemas from BioPro code
python extract_schemas_from_java.py \
  --source-dir "C:/Users/MelvinJones/work/biopro/biopro-manufacturing/backend/apheresisplasma/src/main/java" \
  --output-dir biopro-manufacturing-schemas

# Step 2: Review generated schemas
ls biopro-manufacturing-schemas
# Output:
#   ApheresisPlasmaProductCreatedEventSchema.avsc
#   ApheresisPlasmaProductCompletedEventSchema.avsc
#   ...

# Step 3: Register to Schema Registry
python register_schemas.py \
  --schemas-dir biopro-manufacturing-schemas \
  --registry http://localhost:8081

# Step 4: Verify registration
curl http://localhost:8081/subjects

# Step 5: Use in Spring Boot (already configured)
# - KafkaAvroSerializer will use registered schemas
# - SpringWolf will document from Schema Registry
```

## Related Tools

- **`register_schemas.py`**: Registers .avsc files to Schema Registry
- **`BioPro-Schema-Inventory.md`**: Manual schema documentation
- **SpringWolf**: Documents events at runtime from Schema Registry

---

**Created**: January 2025
**For**: BioPro Event Governance POC
**Tool**: `extract_schemas_from_java.py`
