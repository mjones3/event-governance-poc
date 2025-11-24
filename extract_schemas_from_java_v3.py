#!/usr/bin/env python3
"""
BioPro Java to Avro Schema Extractor v3 - WITH TYPE DEDUPLICATION

Fixes the "Can't redefine" error by defining each custom type only once
and referencing it by name in subsequent uses.

Usage:
    python extract_schemas_from_java_v3.py --source-dir C:/path/to/java/code
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


@dataclass
class JavaField:
    name: str
    java_type: str
    required: bool
    doc: str
    example: Optional[str]


@dataclass
class JavaRecord:
    name: str
    namespace: str
    doc: str
    fields: List[JavaField]


# Global cache for resolved types
type_definitions_cache: Dict[str, dict] = {}

# Track types defined in current schema (to avoid redefinition)
types_defined_in_schema: Set[str] = set()


def is_value_object_enum(file_path: Path) -> Tuple[bool, List[str], Optional[str]]:
    """Check if a Java record is an enum-like value object and extract symbols and namespace

    Returns:
        Tuple of (is_enum, symbols, namespace)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract namespace
    namespace_match = re.search(r'package\s+([\w.]+);', content)
    namespace = namespace_match.group(1) if namespace_match else None

    # Pattern: record(String value) with static final String constants
    if 'record' in content and '(String value)' in content:
        # Extract static constants
        constants = re.findall(r'private\s+static\s+final\s+String\s+(\w+)\s*=\s*"([^"]+)"', content)
        if constants:
            return True, [const[1] for const in constants], namespace

    return False, [], None


def parse_simple_record(file_path: Path, source_dir: Path) -> Optional[dict]:
    """Parse a simple Java record and return Avro record definition"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract record name
    record_match = re.search(r'public\s+record\s+(\w+)\s*\(([^)]+)\)', content)
    if not record_match:
        return None

    record_name = record_match.group(1)
    params = record_match.group(2)

    # Extract namespace
    namespace_match = re.search(r'package\s+([\w.]+);', content)
    namespace = namespace_match.group(1) if namespace_match else ""

    # Parse record parameters (simple version)
    fields = []
    param_pattern = r'(\w+(?:<[^>]+>)?)\s+(\w+)'

    for match in re.finditer(param_pattern, params):
        field_type = match.group(1).strip()
        field_name = match.group(2).strip()

        # Resolve the type recursively
        avro_type = resolve_java_type_to_avro(field_type, source_dir, set())

        fields.append({
            "name": field_name,
            "type": avro_type,
            "doc": f"{field_name} field"
        })

    return {
        "type": "record",
        "name": record_name,
        "namespace": namespace,
        "fields": fields
    }


def find_type_file(type_name: str, source_dir: Path) -> Optional[Path]:
    """Find the Java file for a custom type"""
    # Search in valueobject and payload directories
    patterns = [
        f"**/valueobject/{type_name}.java",
        f"**/payload/{type_name}.java",
        f"**/{type_name}.java"
    ]

    for pattern in patterns:
        matches = list(source_dir.glob(pattern))
        if matches:
            return matches[0]

    return None


def get_type_full_name(type_def: dict) -> str:
    """Get the full name of a type (namespace.name)"""
    if isinstance(type_def, dict):
        if 'namespace' in type_def and 'name' in type_def:
            return f"{type_def['namespace']}.{type_def['name']}"
        elif 'name' in type_def:
            return type_def['name']
    return ""


def resolve_java_type_to_avro(java_type: str, source_dir: Path, processed: Set[str], use_references: bool = False) -> any:
    """Recursively resolve Java type to Avro type

    Args:
        java_type: The Java type to resolve
        source_dir: Source directory to search for type definitions
        processed: Set of types being processed (to avoid infinite recursion)
        use_references: If True, return type name reference instead of full definition for custom types
    """

    # Handle generic types
    if '<' in java_type:
        container_match = re.match(r'(\w+)<(.+)>', java_type)
        if container_match:
            container = container_match.group(1)
            element_type = container_match.group(2)

            if container == 'List':
                return {
                    "type": "array",
                    "items": resolve_java_type_to_avro(element_type.strip(), source_dir, processed, use_references)
                }

    # Base type mappings
    type_map = {
        'String': 'string',
        'Integer': 'int',
        'int': 'int',
        'Long': 'long',
        'long': 'long',
        'Boolean': 'boolean',
        'boolean': 'boolean',
        'Double': 'double',
        'double': 'double',
        'UUID': {'type': 'string', 'logicalType': 'uuid'},
        'ZonedDateTime': {'type': 'long', 'logicalType': 'timestamp-millis'},
        'LocalDate': {'type': 'int', 'logicalType': 'date'},
    }

    if java_type in type_map:
        return type_map[java_type]

    # Check cache first
    if java_type in type_definitions_cache:
        type_def = type_definitions_cache[java_type]

        # If this type was already defined in the current schema, return just the name
        if use_references:
            full_name = get_type_full_name(type_def)
            if full_name in types_defined_in_schema:
                return type_def['name']  # Return just the name, not the full definition

        return type_def

    # Avoid infinite recursion
    if java_type in processed:
        return "string"  # Fallback

    processed.add(java_type)

    # Try to find and parse the custom type
    type_file = find_type_file(java_type, source_dir)
    if type_file:
        # Check if it's an enum-like value object
        is_enum, symbols, enum_namespace = is_value_object_enum(type_file)
        if is_enum:
            enum_def = {
                "type": "enum",
                "name": java_type,
                "symbols": symbols
            }
            # Add namespace if available
            if enum_namespace:
                enum_def["namespace"] = enum_namespace
            type_definitions_cache[java_type] = enum_def
            return enum_def

        # Try to parse as a record
        record_def = parse_simple_record(type_file, source_dir)
        if record_def:
            type_definitions_cache[java_type] = record_def
            return record_def

    # Fallback: treat as string
    return "string"


def java_type_to_avro_with_resolution(java_type: str, required: bool, source_dir: Path, use_references: bool = False) -> any:
    """Convert Java type to Avro type with nested type resolution

    Args:
        java_type: The Java type to convert
        required: Whether the field is required
        source_dir: Source directory to search for type definitions
        use_references: If True, use type name references for already-defined types
    """

    avro_type = resolve_java_type_to_avro(java_type, source_dir, set(), use_references)

    # Make optional (union with null) if not required
    if not required:
        return ["null", avro_type]

    return avro_type


def mark_types_as_defined(avro_type: any):
    """Recursively mark all custom types in an Avro type as defined"""
    if isinstance(avro_type, dict):
        if 'type' in avro_type:
            # This is a complex type (record, enum, etc.)
            full_name = get_type_full_name(avro_type)
            if full_name:
                types_defined_in_schema.add(full_name)

            # Recursively process nested fields
            if 'fields' in avro_type:
                for field in avro_type['fields']:
                    mark_types_as_defined(field.get('type'))

            if 'items' in avro_type:
                mark_types_as_defined(avro_type['items'])

    elif isinstance(avro_type, list):
        # Union type
        for union_type in avro_type:
            mark_types_as_defined(union_type)


def parse_java_record(file_path: Path, source_dir: Path) -> Optional[JavaRecord]:
    """Parse a Java record class and extract field information"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract package/namespace
    namespace_match = re.search(r'package\s+([\w.]+);', content)
    namespace = namespace_match.group(1) if namespace_match else "com.biopro.events"

    # Extract record name
    record_match = re.search(r'public\s+record\s+(\w+)\s*\(', content)
    if not record_match:
        return None
    record_name = record_match.group(1)

    # Extract @Schema annotation for doc
    schema_doc_match = re.search(r'@Schema\([^)]*description\s*=\s*"([^"]+)"', content)
    doc = schema_doc_match.group(1) if schema_doc_match else f"Payload for {record_name} event"

    # Extract fields from record components
    fields = []

    # Find the record definition (between parentheses)
    record_def_match = re.search(r'public\s+record\s+\w+\s*\((.*?)\)\s*implements', content, re.DOTALL)
    if not record_def_match:
        return None

    record_components = record_def_match.group(1)

    # Split by field (look for @Schema annotations followed by type and name)
    field_pattern = r'@Schema\((.*?)\)\s*(\w+(?:<[^>]+>)?)\s+(\w+)(?:,|\s*$)'

    for match in re.finditer(field_pattern, record_components, re.DOTALL):
        schema_attrs = match.group(1)
        field_type = match.group(2)
        field_name = match.group(3)

        # Extract field attributes
        required = 'requiredMode = REQUIRED' in schema_attrs or 'requiredMode = Schema.RequiredMode.REQUIRED' in schema_attrs

        # Extract documentation
        doc_match = re.search(r'description\s*=\s*"([^"]+)"', schema_attrs)
        title_match = re.search(r'title\s*=\s*"([^"]+)"', schema_attrs)
        field_doc = doc_match.group(1) if doc_match else (title_match.group(1) if title_match else "")

        # Extract example
        example_match = re.search(r'example\s*=\s*"([^"]+)"', schema_attrs)
        example = example_match.group(1) if example_match else None

        fields.append(JavaField(
            name=field_name,
            java_type=field_type,
            required=required,
            doc=field_doc,
            example=example
        ))

    return JavaRecord(
        name=record_name,
        namespace=namespace,
        doc=doc,
        fields=fields
    )


def generate_avro_schema(record: JavaRecord, source_dir: Path) -> dict:
    """Generate Avro schema from Java record with type deduplication"""

    # Clear caches for new schema generation
    global type_definitions_cache, types_defined_in_schema
    type_definitions_cache = {}
    types_defined_in_schema = set()

    schema = {
        "type": "record",
        "name": f"{record.name}Payload",
        "namespace": record.namespace,
        "doc": record.doc,
        "fields": []
    }

    # First pass: collect all fields without references (to define types)
    for field in record.fields:
        avro_field = {
            "name": field.name,
            "type": java_type_to_avro_with_resolution(field.java_type, field.required, source_dir, use_references=False),
            "doc": field.doc
        }

        # Add default for optional fields
        if not field.required and isinstance(avro_field["type"], list):
            avro_field["default"] = None

        # Add example if available
        if field.example:
            avro_field["doc"] += f" (example: {field.example})"

        # Mark types as defined
        mark_types_as_defined(avro_field["type"])

        schema["fields"].append(avro_field)

    # Second pass: replace duplicate type definitions with references
    # IMPORTANT: Use a SHARED seen_types set across all fields
    seen_types = set()
    for field in schema["fields"]:
        field["type"] = deduplicate_types(field["type"], seen_types)

    return schema


def deduplicate_types(avro_type: any, seen_types: Set[str]) -> any:
    """Replace duplicate type definitions with name references"""

    if isinstance(avro_type, dict):
        if 'type' in avro_type and avro_type['type'] in ['record', 'enum']:
            # This is a complex type definition
            full_name = get_type_full_name(avro_type)

            if full_name in seen_types:
                # Already defined, return the fully qualified name (namespace.name)
                # This is required for types in different namespaces
                return full_name
            else:
                # First occurrence, mark as seen and process nested fields
                if full_name:
                    seen_types.add(full_name)

                # Recursively process nested fields
                if 'fields' in avro_type:
                    for field in avro_type['fields']:
                        field['type'] = deduplicate_types(field['type'], seen_types)

                if 'items' in avro_type:
                    avro_type['items'] = deduplicate_types(avro_type['items'], seen_types)

                return avro_type

        elif 'items' in avro_type:
            # Array type
            avro_type['items'] = deduplicate_types(avro_type['items'], seen_types)
            return avro_type

    elif isinstance(avro_type, list):
        # Union type
        return [deduplicate_types(t, seen_types) for t in avro_type]

    return avro_type


def generate_event_envelope_schema(event_type: str, payload_schema: dict, namespace: str) -> dict:
    """Generate complete event schema with envelope"""

    return {
        "type": "record",
        "name": event_type,
        "namespace": namespace,
        "doc": f"Event published when {event_type.replace('Event', '').lower()} occurs",
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
                "name": "occurredOnTimeZone",
                "type": "string",
                "default": "UTC",
                "doc": "Timezone for occurredOn"
            },
            {
                "name": "eventType",
                "type": "string",
                "default": event_type.replace("Event", ""),
                "doc": "Type of event"
            },
            {
                "name": "eventVersion",
                "type": "string",
                "default": "1.0",
                "doc": "Version of the event schema"
            },
            {
                "name": "payload",
                "type": payload_schema,
                "doc": f"{event_type} payload"
            }
        ]
    }


def extract_schemas(source_dir: Path, output_dir: Path):
    """Extract all event schemas from Java source code"""

    print(f"{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.BLUE}BioPro Java to Avro Schema Extractor v3{Colors.NC}")
    print(f"{Colors.BLUE}WITH TYPE DEDUPLICATION FIX{Colors.NC}")
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}\n")

    print(f"{Colors.YELLOW}Source Directory:{Colors.NC} {source_dir}")
    print(f"{Colors.YELLOW}Output Directory:{Colors.NC} {output_dir}\n")

    # Find all Event classes
    print(f"{Colors.BLUE}[1/3] Scanning for Event classes...{Colors.NC}")
    event_files = list(source_dir.glob("**/domain/event/*Event.java"))
    payload_files = list(source_dir.glob("**/domain/event/payload/*.java"))

    print(f"{Colors.GREEN}Found {len(event_files)} event classes{Colors.NC}")
    print(f"{Colors.GREEN}Found {len(payload_files)} payload classes{Colors.NC}\n")

    # Parse payload records
    print(f"{Colors.BLUE}[2/3] Parsing Java payload records with type deduplication...{Colors.NC}")

    schemas_generated = 0
    schemas_failed = 0

    for payload_file in payload_files:
        print(f"{Colors.YELLOW}Processing:{Colors.NC} {payload_file.name}")

        try:
            record = parse_java_record(payload_file, source_dir)
            if not record:
                print(f"  {Colors.YELLOW}Skipped (not a record class){Colors.NC}\n")
                continue

            print(f"  Record: {record.name}")
            print(f"  Fields: {len(record.fields)}")

            # Generate payload schema WITH type deduplication
            payload_schema = generate_avro_schema(record, source_dir)

            # Infer event type name from payload
            event_type = f"Apheresis Plasma{record.name.replace('Product', 'Product ')}Event"

            # Generate full event schema with envelope
            event_schema = generate_event_envelope_schema(
                event_type.replace(" ", ""),
                payload_schema,
                record.namespace.replace(".payload", "")
            )

            # Write schema file
            output_file = output_dir / f"{event_type.replace(' ', '')}.avsc"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(event_schema, f, indent=2)

            print(f"  {Colors.GREEN}Generated:{Colors.NC} {output_file.name}")
            print(f"  Types defined: {len(types_defined_in_schema)}\n")
            schemas_generated += 1

        except Exception as e:
            print(f"  {Colors.RED}Error:{Colors.NC} {e}\n")
            import traceback
            traceback.print_exc()
            schemas_failed += 1

    # Summary
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.GREEN}Schema extraction complete!{Colors.NC}")
    print(f"  {Colors.GREEN}Successfully generated: {schemas_generated}{Colors.NC}")
    if schemas_failed > 0:
        print(f"  {Colors.RED}Failed: {schemas_failed}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Extract Avro schemas from BioPro Java event classes (v3 with type deduplication)'
    )
    parser.add_argument(
        '--source-dir',
        required=True,
        help='Source directory containing Java event classes'
    )
    parser.add_argument(
        '--output-dir',
        default='./extracted-schemas-v3',
        help='Output directory for generated .avsc files'
    )

    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)

    if not source_dir.exists():
        print(f"{Colors.RED}ERROR: Source directory not found: {source_dir}{Colors.NC}")
        return 1

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    extract_schemas(source_dir, output_dir)

    return 0


if __name__ == '__main__':
    exit(main())
