# BioPro Schema Management Tools

Utility scripts for managing Avro schemas in the Event Governance Framework.

## Tools Included

### 1. `json-to-avro.py`
Converts JSON Schema to Apache Avro schema format.

**Usage:**
```bash
python json-to-avro.py <input.json> <output.avsc>
```

**Example:**
```bash
python json-to-avro.py TestResultReceived.json schemas/TestResultReceived.avsc
```

**Features:**
- Converts JSON Schema types to Avro types
- Handles logical types (uuid, timestamp, date)
- Generates namespace from $id field
- Converts nested objects to Avro records
- Handles arrays and optional fields

---

### 2. `validate-schemas.py`
Validates Avro schema files for syntax and structure.

**Usage:**
```bash
python validate-schemas.py <schema-directory>
```

**Example:**
```bash
python validate-schemas.py schemas/
```

**Validates:**
- JSON syntax
- Required Avro fields (name, type, fields)
- Field structure
- Namespace presence (warning if missing)

---

### 3. `register-schemas.sh`
Registers Avro schemas to Confluent Schema Registry.

**Usage:**
```bash
./register-schemas.sh <schema-directory> <schema-registry-url>
```

**Example:**
```bash
./register-schemas.sh schemas/ http://localhost:8081
```

**Features:**
- Auto-discovers all .avsc files
- Determines subject names from directory structure
- Registers to Schema Registry
- Logs schema IDs to artifacts
- Returns exit code 0 on success, 1 on failure

---

### 4. `.gitlab-ci.yml.example`
GitLab CI/CD pipeline template for automated schema management.

**Setup:**
```bash
cp .gitlab-ci.yml.example ../.gitlab-ci.yml
```

**Pipeline Stages:**
1. **validate** - Validates schema syntax
2. **register** - Registers schemas to Schema Registry (main branch only)
3. **deploy** - Deploys service after schema registration

---

## Quick Start

### 1. Copy Tools to Your Repository

```bash
# Create scripts directory
mkdir -p scripts

# Copy utilities
cp schema-tools/* scripts/

# Make executable
chmod +x scripts/*.sh scripts/*.py
```

### 2. Create Schema Directory

```bash
mkdir -p schemas/testresults
mkdir -p schemas/units
```

### 3. Convert Existing JSON Schema

```bash
python scripts/json-to-avro.py \
    my-event.json \
    schemas/testresults/MyEvent.avsc
```

### 4. Validate Schema

```bash
python scripts/validate-schemas.py schemas/
```

### 5. Register to Schema Registry

```bash
./scripts/register-schemas.sh schemas/ http://localhost:8081
```

### 6. Set Up CI/CD

```bash
cp scripts/.gitlab-ci.yml.example .gitlab-ci.yml

# Edit .gitlab-ci.yml and update:
# - SCHEMA_REGISTRY_URL
# - Any project-specific configuration
```

### 7. Commit and Push

```bash
git add schemas/ scripts/ .gitlab-ci.yml
git commit -m "Add schema management tooling"
git push
```

---

## Directory Structure Example

```
your-service/
├── schemas/
│   ├── testresults/
│   │   ├── TestResultReceived.avsc
│   │   └── TestResultProcessed.avsc
│   └── units/
│       └── UnitUnsuitable.avsc
├── scripts/
│   ├── json-to-avro.py
│   ├── validate-schemas.py
│   ├── register-schemas.sh
│   └── README.md (this file)
├── .gitlab-ci.yml
└── pom.xml
```

---

## Troubleshooting

### Schema Registration Fails

**Problem**: `HTTP 409 - Schema incompatible`

**Solution**: Check compatibility:
```bash
curl -X POST \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data @schemas/MyEvent.avsc \
  http://localhost:8081/compatibility/subjects/MyEvent-value/versions/latest
```

### json-to-avro Doesn't Handle Complex Nesting

**Solution**: Manually edit the generated .avsc file to add nested record types.

### CI Pipeline Doesn't Trigger

**Problem**: Pipeline doesn't run on schema changes

**Solution**: Verify `.gitlab-ci.yml` has:
```yaml
only:
  changes:
    - schemas/**/*.avsc
```

---

## Additional Resources

- **Schema Management Guide**: `Schema-Management-Guide.md`
- **Integration Guide**: `Event-Governance-Integration-Guide.md`
- **Schema Evolution Guide**: `Schema-Evolution-Guide.md`

---

**Questions?**
**Slack**: #event-governance
**Wiki**: http://wiki.biopro.com/schema-management

**Version**: 1.0
**Last Updated**: 2024-11-15
