#!/usr/bin/env python3
"""
Avro Schema Validator
Validates Avro schema files for syntax and structural correctness.

Usage:
    python validate-schemas.py <schema-directory>

Example:
    python validate-schemas.py schemas/
"""

import json
import sys
import os
from pathlib import Path


def validate_avro_schema(schema_dict):
    """
    Validate Avro schema structure.

    Args:
        schema_dict: Parsed Avro schema as dictionary

    Returns:
        (bool, str): (is_valid, error_message)
    """
    # Check required fields for record type
    if not isinstance(schema_dict, dict):
        return False, "Schema must be a JSON object"

    schema_type = schema_dict.get("type")
    if not schema_type:
        return False, "Schema must have a 'type' field"

    if schema_type == "record":
        # Validate required fields for record type
        required_fields = ["name", "fields"]
        for field in required_fields:
            if field not in schema_dict:
                return False, f"Record schema missing required field: '{field}'"

        # Validate namespace (recommended but not required)
        if "namespace" not in schema_dict:
            print(f"  ⚠️  Warning: No 'namespace' specified (recommended: com.biopro.events.*)")

        # Validate fields array
        fields = schema_dict.get("fields")
        if not isinstance(fields, list):
            return False, "'fields' must be an array"

        if len(fields) == 0:
            return False, "Record must have at least one field"

        # Validate each field
        for idx, field in enumerate(fields):
            if not isinstance(field, dict):
                return False, f"Field {idx} must be an object"

            if "name" not in field:
                return False, f"Field {idx} missing 'name'"

            if "type" not in field:
                return False, f"Field '{field.get('name', idx)}' missing 'type'"

    return True, None


def validate_schema_file(filepath):
    """
    Validate a single Avro schema file.

    Args:
        filepath: Path to .avsc file

    Returns:
        bool: True if valid, False otherwise
    """
    print(f"Validating: {filepath}")

    try:
        with open(filepath, 'r') as f:
            schema = json.load(f)

        # Validate JSON structure
        is_valid, error = validate_avro_schema(schema)

        if not is_valid:
            print(f"  ✗ Invalid: {error}")
            return False

        # Extract schema info
        schema_name = schema.get("name", "Unknown")
        namespace = schema.get("namespace", "No namespace")
        num_fields = len(schema.get("fields", []))

        print(f"  ✓ Valid")
        print(f"    - Name: {schema_name}")
        print(f"    - Namespace: {namespace}")
        print(f"    - Fields: {num_fields}")

        return True

    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python validate-schemas.py <schema-directory>")
        print("\nExample:")
        print("  python validate-schemas.py schemas/")
        sys.exit(1)

    schema_dir = Path(sys.argv[1])

    if not schema_dir.exists():
        print(f"Error: Directory '{schema_dir}' does not exist")
        sys.exit(1)

    if not schema_dir.is_dir():
        print(f"Error: '{schema_dir}' is not a directory")
        sys.exit(1)

    print("=" * 60)
    print("Avro Schema Validation")
    print("=" * 60)
    print(f"Directory: {schema_dir}\n")

    # Find all .avsc files
    schema_files = list(schema_dir.rglob("*.avsc"))

    if not schema_files:
        print(f"No .avsc files found in {schema_dir}")
        sys.exit(1)

    print(f"Found {len(schema_files)} schema file(s)\n")

    # Validate each schema
    valid_count = 0
    invalid_count = 0

    for schema_file in sorted(schema_files):
        if validate_schema_file(schema_file):
            valid_count += 1
        else:
            invalid_count += 1
        print()  # Blank line between schemas

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Valid:   {valid_count}")
    print(f"Invalid: {invalid_count}")

    if invalid_count > 0:
        print("\n✗ Validation failed. Fix errors above.")
        sys.exit(1)
    else:
        print("\n✓ All schemas are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
