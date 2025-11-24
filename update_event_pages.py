#!/usr/bin/env python3
"""
Update EventCatalog event pages with:
1. Complete schema fields from Avro schemas
2. Realistic sample events
3. Avro schema as downloadable attachment (not displayed on page)
"""

import json
import os
import re
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import random
import uuid

SCHEMA_REGISTRY_URL = "http://localhost:8081"
EVENTCATALOG_DIR = Path("eventcatalog")
EVENTS_DIR = EVENTCATALOG_DIR / "events"

def get_all_subjects():
    """Get all subjects from Schema Registry"""
    response = requests.get(f"{SCHEMA_REGISTRY_URL}/subjects")
    if response.status_code == 200:
        return response.json()
    return []

def get_latest_schema(subject: str):
    """Get latest schema for a subject"""
    try:
        response = requests.get(f"{SCHEMA_REGISTRY_URL}/subjects/{subject}/versions/latest")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching schema for {subject}: {e}")
    return None

def parse_avro_type(avro_type: Any) -> tuple[str, bool]:
    """Parse Avro type to human-readable type and required flag"""
    if isinstance(avro_type, str):
        return avro_type, True
    elif isinstance(avro_type, dict):
        if avro_type.get("type") == "enum":
            symbols = avro_type.get("symbols", [])
            return f"enum ({', '.join(symbols[:3])}{'...' if len(symbols) > 3 else ''})", True
        elif avro_type.get("type") == "array":
            items_type, _ = parse_avro_type(avro_type.get("items", "unknown"))
            return f"array<{items_type}>", True
        elif avro_type.get("type") == "map":
            values_type, _ = parse_avro_type(avro_type.get("values", "unknown"))
            return f"map<string, {values_type}>", True
        elif avro_type.get("type") == "record":
            return avro_type.get("name", "record"), True
        elif avro_type.get("logicalType"):
            return avro_type.get("logicalType"), True
        else:
            return str(avro_type.get("type", "unknown")), True
    elif isinstance(avro_type, list):
        # Union type
        if "null" in avro_type:
            non_null_types = [t for t in avro_type if t != "null"]
            if non_null_types:
                type_str, _ = parse_avro_type(non_null_types[0])
                return type_str, False
        return "union", True
    return "unknown", True

def extract_fields_from_schema(schema: Dict) -> List[Dict]:
    """Extract fields from Avro schema"""
    fields = []
    schema_obj = schema.get("schema")
    if isinstance(schema_obj, str):
        schema_obj = json.loads(schema_obj)

    avro_fields = schema_obj.get("fields", [])

    for field in avro_fields:
        field_name = field.get("name")
        field_type = field.get("type")
        field_doc = field.get("doc", "")
        has_default = "default" in field

        type_str, required = parse_avro_type(field_type)

        # If has default, it's not required
        if has_default:
            required = False

        fields.append({
            "name": field_name,
            "type": type_str,
            "required": required,
            "description": field_doc
        })

    return fields

def generate_sample_value(field_type: str, field_name: str) -> Any:
    """Generate realistic sample value based on field type and name"""
    field_name_lower = field_name.lower()

    # UUID fields
    if "uuid" in field_type or "id" in field_name_lower:
        return str(uuid.uuid4())

    # Timestamp fields
    if "timestamp" in field_type or "time" in field_name_lower or "date" in field_name_lower:
        return int(datetime.now().timestamp() * 1000)

    # Enum fields
    if field_type.startswith("enum"):
        # Extract first enum value from type string
        match = re.search(r'\(([^)]+)\)', field_type)
        if match:
            values = [v.strip() for v in match.group(1).split(',')]
            return values[0] if values else "VALUE"
        return "VALUE"

    # String fields with specific patterns
    if field_type == "string":
        if "number" in field_name_lower or "unit" in field_name_lower:
            return f"W{random.randint(100000000, 999999999)}"
        elif "type" in field_name_lower:
            return "STANDARD"
        elif "status" in field_name_lower:
            return "ACTIVE"
        elif "location" in field_name_lower:
            return "New York Blood Center"
        elif "zone" in field_name_lower:
            return "America/New_York"
        elif "version" in field_name_lower:
            return "1.0"
        elif "blood" in field_name_lower or "abo" in field_name_lower:
            return random.choice(["AP", "AN", "BP", "BN", "OP", "ON", "ABP", "ABN"])
        else:
            return f"{field_name}_value"

    # Numeric fields
    if field_type in ["int", "long"]:
        if "amount" in field_name_lower or "volume" in field_name_lower:
            return random.randint(300, 500)
        return random.randint(1, 100)

    if field_type in ["float", "double"]:
        return round(random.uniform(1.0, 100.0), 2)

    # Boolean fields
    if field_type == "boolean":
        return random.choice([True, False])

    # Array fields
    if field_type.startswith("array"):
        return []  # Return empty array, will be populated if needed

    # Map fields
    if field_type.startswith("map"):
        return {}

    # Record fields
    if field_type not in ["string", "int", "long", "float", "double", "boolean"]:
        return {}

    return f"{field_name}_value"

def generate_sample_event(fields: List[Dict]) -> Dict:
    """Generate a realistic sample event from schema fields"""
    sample = {}

    for field in fields:
        field_name = field["name"]
        field_type = field["type"]
        required = field["required"]

        # Always include required fields, sometimes include optional ones
        if required or random.random() > 0.3:
            sample[field_name] = generate_sample_value(field_type, field_name)

    # Special handling for volumes array if present
    if "volumes" in sample and isinstance(sample["volumes"], list):
        sample["volumes"] = [
            {
                "type": "PLASMA",
                "amount": 450,
                "excludeInCalculation": False
            }
        ]

    return sample

def create_fields_table(fields: List[Dict]) -> str:
    """Create markdown table for schema fields"""
    if not fields:
        return ""

    table = "| Field | Type | Required | Description |\n"
    table += "|-------|------|----------|-------------|\n"

    for field in fields:
        name = field["name"]
        type_str = field["type"]
        required = "Yes" if field["required"] else "No"
        description = field["description"] or ""

        # Escape pipe characters in description
        description = description.replace("|", "\\|")

        table += f"| `{name}` | `{type_str}` | {required} | {description} |\n"

    return table

def update_event_mdx_file(event_dir: Path, subject: str, schema_data: Dict):
    """Update an event MDX file with complete information"""
    mdx_file = event_dir / "index.mdx"
    if not mdx_file.exists():
        print(f"MDX file not found: {mdx_file}")
        return

    # Extract schema information
    schema_id = schema_data.get("id", "unknown")
    version = schema_data.get("version", "1")

    # Parse schema
    schema_obj = schema_data.get("schema")
    if isinstance(schema_obj, str):
        schema_obj = json.loads(schema_obj)

    event_name = schema_obj.get("name", subject.replace("-value", ""))
    namespace = schema_obj.get("namespace", "")
    doc = schema_obj.get("doc", "")

    # Extract domain from namespace
    domain = "Unknown"
    if "distribution" in namespace:
        domain = "Distribution"
    elif "collections" in namespace:
        domain = "Collections"
    elif "manufacturing" in namespace:
        domain = "Manufacturing"
    elif "operations" in namespace:
        domain = "Operations"

    # Extract fields
    fields = extract_fields_from_schema(schema_data)

    # Generate sample event
    sample_event = generate_sample_event(fields)

    # Create fields table
    fields_table = create_fields_table(fields)

    # Read existing MDX
    with open(mdx_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not frontmatter_match:
        print(f"No frontmatter found in {mdx_file}")
        return

    frontmatter = frontmatter_match.group(1)

    # Create new content
    new_content = f"""---
{frontmatter}
---

# {event_name}

**Schema ID**: {schema_id}
**Schema Version**: {version}
**Subject**: {subject.replace('-value', '')}
**Domain**: {domain}
**Namespace**: {namespace}

## Business Context

{doc or f"Event published in the {domain} domain."}

## Event Schema Fields

{fields_table}

## Sample Event

```json
{json.dumps(sample_event, indent=2)}
```

## Schema Evolution

This event uses Avro schema validation through Confluent Schema Registry.

- **Schema ID**: {schema_id}
- **Version**: {version}
- **Compatibility**: BACKWARD (default)

## Message Format

Messages are serialized using **Avro** with the schema ID embedded in the message header (magic byte + schema ID).

## Integration Notes

### Consuming This Event

When consuming this event, use the Confluent Avro deserializer which will:
1. Read the schema ID from the message
2. Fetch the schema from the registry (with caching)
3. Deserialize the message using the schema

### Publishing This Event

When publishing this event:
1. Use the Confluent Avro serializer
2. The serializer will register the schema if needed
3. The schema ID will be embedded in each message

## Download Schema

- [Download Avro Schema](./{event_name}.avsc) - Complete Avro schema definition

<NodeGraph />
"""

    # Save schema file
    schema_file = event_dir / f"{event_name}.avsc"
    with open(schema_file, 'w', encoding='utf-8') as f:
        json.dump(schema_obj, f, indent=2)

    # Write updated MDX
    with open(mdx_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[OK] Updated {mdx_file.relative_to(EVENTCATALOG_DIR)}")

def main():
    """Main function to update all event pages"""
    print("Fetching schemas from Schema Registry...")

    subjects = get_all_subjects()
    print(f"Found {len(subjects)} subjects")

    # Filter to event subjects (ending with -value or Event)
    event_subjects = [s for s in subjects if s.endswith("-value") or s.endswith("Event")]
    print(f"Processing {len(event_subjects)} event schemas...")

    updated_count = 0
    for subject in event_subjects:
        # Get schema
        schema_data = get_latest_schema(subject)
        if not schema_data:
            print(f"[ERROR] Could not fetch schema for {subject}")
            continue

        # Determine event directory name
        event_name = subject.replace("-value", "").replace("Event", "")

        # Find matching event directory - must be exact match
        event_dir = EVENTS_DIR / event_name
        event_dirs = []

        if event_dir.exists() and event_dir.is_dir():
            event_dirs = [event_dir]
        else:
            # Try case-insensitive exact match
            for dir in EVENTS_DIR.iterdir():
                if dir.is_dir() and dir.name.lower() == event_name.lower():
                    event_dirs = [dir]
                    break

        if not event_dirs:
            print(f"[WARN] No event directory found for {subject}")
            continue

        for event_dir in event_dirs:
            update_event_mdx_file(event_dir, subject, schema_data)
            updated_count += 1

    print(f"\n[DONE] Updated {updated_count} event pages")

if __name__ == "__main__":
    main()
