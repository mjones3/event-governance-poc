#!/usr/bin/env python3
"""
JSON Schema to Avro Schema Converter
Converts JSON Schema to Apache Avro schema format for Schema Registry registration.

Usage:
    python json-to-avro.py <input-json-schema.json> <output-avro-schema.avsc>

Example:
    python json-to-avro.py TestResultReceived.json TestResultReceived.avsc
"""

import json
import sys
from typing import Dict, List, Any, Optional

def json_type_to_avro_type(json_type: str, format_hint: Optional[str] = None) -> Any:
    """
    Convert JSON Schema type to Avro type.

    Args:
        json_type: JSON Schema type (string, number, integer, boolean, object, array)
        format_hint: JSON Schema format hint (date-time, uuid, etc.)

    Returns:
        Avro type specification
    """
    # Handle logical types based on format hints
    if format_hint == "uuid":
        return {"type": "string", "logicalType": "uuid"}
    elif format_hint == "date-time":
        return {"type": "long", "logicalType": "timestamp-millis"}
    elif format_hint == "date":
        return {"type": "int", "logicalType": "date"}
    elif format_hint == "time":
        return {"type": "int", "logicalType": "time-millis"}

    # Standard type mappings
    type_map = {
        "string": "string",
        "number": "double",
        "integer": "long",
        "boolean": "boolean",
        "null": "null"
    }

    return type_map.get(json_type, "string")


def convert_property_to_avro_field(prop_name: str, prop_schema: Dict, required_fields: List[str]) -> Dict:
    """
    Convert a JSON Schema property to an Avro field.

    Args:
        prop_name: Property name
        prop_schema: Property schema definition
        required_fields: List of required field names

    Returns:
        Avro field definition
    """
    is_required = prop_name in required_fields

    field = {
        "name": prop_name,
        "doc": prop_schema.get("description", f"{prop_name} field")
    }

    # Handle type conversion
    json_type = prop_schema.get("type", "string")
    format_hint = prop_schema.get("format")

    if json_type == "object":
        # Nested object - create nested record
        nested_record = {
            "type": "record",
            "name": f"{prop_name.capitalize()}",
            "fields": []
        }

        nested_props = prop_schema.get("properties", {})
        nested_required = prop_schema.get("required", [])

        for nested_name, nested_schema in nested_props.items():
            nested_record["fields"].append(
                convert_property_to_avro_field(nested_name, nested_schema, nested_required)
            )

        if is_required:
            field["type"] = nested_record
        else:
            field["type"] = ["null", nested_record]
            field["default"] = None

    elif json_type == "array":
        # Array type
        items_schema = prop_schema.get("items", {})
        items_type = items_schema.get("type", "string")

        if items_type == "object":
            # Array of records
            item_record = {
                "type": "record",
                "name": f"{prop_name.capitalize()}Item",
                "fields": []
            }

            item_props = items_schema.get("properties", {})
            item_required = items_schema.get("required", [])

            for item_name, item_schema in item_props.items():
                item_record["fields"].append(
                    convert_property_to_avro_field(item_name, item_schema, item_required)
                )

            field["type"] = {
                "type": "array",
                "items": item_record
            }
        else:
            # Array of primitives
            field["type"] = {
                "type": "array",
                "items": json_type_to_avro_type(items_type, items_schema.get("format"))
            }
    else:
        # Primitive type
        avro_type = json_type_to_avro_type(json_type, format_hint)

        if is_required:
            field["type"] = avro_type
        else:
            field["type"] = ["null", avro_type]
            field["default"] = prop_schema.get("default", None)

    return field


def convert_json_schema_to_avro(json_schema: Dict) -> Dict:
    """
    Convert JSON Schema to Avro schema.

    Args:
        json_schema: JSON Schema definition

    Returns:
        Avro schema definition
    """
    # Extract event information
    title = json_schema.get("title", "Event")
    description = json_schema.get("description", "Event schema")

    # Determine namespace from $id or default
    schema_id = json_schema.get("$id", "")
    if schema_id:
        # Extract namespace from $id like: https://biopro.com/schemas/testresults/TestResultReceived
        parts = schema_id.rstrip("/").split("/")
        if len(parts) >= 2:
            namespace = f"com.biopro.events.{parts[-2]}"
        else:
            namespace = "com.biopro.events"
    else:
        namespace = "com.biopro.events"

    # Build Avro schema
    avro_schema = {
        "type": "record",
        "name": title.replace(" ", ""),  # Remove spaces from name
        "namespace": namespace,
        "doc": description
    }

    # Convert properties to fields
    fields = []
    properties = json_schema.get("properties", {})
    required_fields = json_schema.get("required", [])

    for prop_name, prop_schema in properties.items():
        fields.append(convert_property_to_avro_field(prop_name, prop_schema, required_fields))

    avro_schema["fields"] = fields

    return avro_schema


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) != 3:
        print("Usage: python json-to-avro.py <input.json> <output.avsc>")
        print("\nExample:")
        print("  python json-to-avro.py TestResultReceived.json TestResultReceived.avsc")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        # Read JSON Schema
        with open(input_file, 'r') as f:
            json_schema = json.load(f)

        print(f"✓ Loaded JSON Schema from {input_file}")

        # Convert to Avro
        avro_schema = convert_json_schema_to_avro(json_schema)

        print(f"✓ Converted to Avro schema")
        print(f"  - Name: {avro_schema['name']}")
        print(f"  - Namespace: {avro_schema['namespace']}")
        print(f"  - Fields: {len(avro_schema['fields'])}")

        # Write Avro Schema
        with open(output_file, 'w') as f:
            json.dump(avro_schema, f, indent=2)

        print(f"✓ Saved Avro schema to {output_file}")
        print("\nNext steps:")
        print(f"  1. Review the generated schema: {output_file}")
        print(f"  2. Add to Git: git add schemas/{output_file}")
        print(f"  3. Commit: git commit -m 'Add {avro_schema['name']} schema'")
        print(f"  4. Push to trigger CI/CD: git push")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{input_file}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
