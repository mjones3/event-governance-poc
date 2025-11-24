#!/usr/bin/env python3
"""
BioPro Schema Registry - EventCatalog Schema Registration

This script registers all Avro schemas from EventCatalog to Schema Registry
"""

import os
import json
import requests
from pathlib import Path
from typing import Tuple, List

# Configuration
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
EVENTCATALOG_DIR = Path("./eventcatalog/events")

# Colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_header():
    print("=" * 60)
    print("   BioPro EventCatalog Schema Registration Tool")
    print("=" * 60)
    print()
    print(f"Schema Registry URL: {SCHEMA_REGISTRY_URL}")
    print(f"EventCatalog Events: {EVENTCATALOG_DIR}")
    print()

def check_schema_registry() -> bool:
    """Check if Schema Registry is accessible"""
    print("[1/3] Checking Schema Registry connectivity...")
    try:
        response = requests.get(f"{SCHEMA_REGISTRY_URL}/subjects", timeout=5)
        if response.status_code == 200:
            print("OK - Connected to Schema Registry")
            return True
    except Exception as e:
        print(f"ERROR: Cannot connect to Schema Registry at {SCHEMA_REGISTRY_URL}")
        print(f"  Error: {e}")
        print(f"  Make sure Schema Registry is running:")
        print(f"    docker-compose up -d schema-registry")
        return False
    return False

def find_schema_files() -> List[Path]:
    """Find all .avsc schema files in EventCatalog"""
    print("[2/3] Checking EventCatalog directory...")

    if not EVENTCATALOG_DIR.exists():
        print(f"ERROR: EventCatalog directory not found: {EVENTCATALOG_DIR}")
        return []

    schema_files = list(EVENTCATALOG_DIR.glob("**/*.avsc"))

    if not schema_files:
        print(f"ERROR: No .avsc files found in {EVENTCATALOG_DIR}")
        return []

    print(f"OK - Found {len(schema_files)} schema file(s)")
    print()
    return schema_files

def register_schema(schema_file: Path) -> Tuple[bool, str]:
    """Register a single schema to Schema Registry"""
    event_name = schema_file.parent.name
    schema_name = schema_file.stem

    # Skip payload-only schemas
    if "Payload" in schema_name:
        return None, "skipped"

    subject = schema_name

    print(f"-> Registering: {schema_name}")
    print(f"  Event: {event_name}")
    print(f"  File: {schema_file}")
    print(f"  Subject: {subject}")

    try:
        # Read and validate schema
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_json = json.load(f)

        # Create payload for Schema Registry
        payload = {
            "schema": json.dumps(schema_json)
        }

        # Register schema
        response = requests.post(
            f"{SCHEMA_REGISTRY_URL}/subjects/{subject}/versions",
            json=payload,
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            timeout=10
        )

        if response.status_code in [200, 201]:
            result = response.json()
            schema_id = result.get('id', 'unknown')
            print(f"  OK - Registered successfully")
            print(f"    Schema ID: {schema_id}")
            print(f"    HTTP Status: {response.status_code}")
            print()
            return True, schema_name
        else:
            print(f"  ERROR - Registration failed")
            print(f"    HTTP Status: {response.status_code}")
            print(f"    Response: {response.text}")
            print()
            return False, schema_name

    except json.JSONDecodeError as e:
        print(f"  ERROR - Invalid JSON in schema file")
        print(f"    Error: {e}")
        print()
        return False, schema_name
    except Exception as e:
        print(f"  ERROR - Registration failed with error")
        print(f"    Error: {e}")
        print()
        return False, schema_name

def print_summary(registered: int, skipped: int, failed: int):
    """Print registration summary"""
    print("=" * 60)
    print("Registration Summary:")
    print(f"  Successfully registered: {registered}")
    print(f"  Skipped (embedded): {skipped}")
    if failed > 0:
        print(f"  Failed: {failed}")
    print("=" * 60)
    print()

def show_registered_subjects():
    """Show registered subjects in Schema Registry"""
    try:
        response = requests.get(f"{SCHEMA_REGISTRY_URL}/subjects", timeout=5)
        if response.status_code == 200:
            subjects = response.json()
            print("Registered Subjects in Schema Registry:")
            for subject in subjects[:20]:
                print(f"  - {subject}")
            print()
            if len(subjects) > 20:
                print(f"(Showing first 20 of {len(subjects)} subjects)")
                print()
    except Exception as e:
        print(f"Could not retrieve subjects: {e}")
        print()

def print_next_steps():
    """Print next steps for the user"""
    print(f"{Colors.YELLOW}Next Steps:{Colors.NC}")
    print(f"  1. View all schemas: {Colors.BLUE}http://localhost:8000{Colors.NC} (Schema Registry UI)")
    print(f"  2. View subjects API: {Colors.BLUE}curl {SCHEMA_REGISTRY_URL}/subjects{Colors.NC}")
    print(f"  3. EventCatalog: {Colors.BLUE}http://localhost:3002{Colors.NC}")
    print()

def main():
    """Main registration flow"""
    print_header()

    # Check connectivity
    if not check_schema_registry():
        return 1
    print()

    # Find schema files
    schema_files = find_schema_files()
    if not schema_files:
        return 1

    # Register schemas
    print(f"{Colors.BLUE}[3/3] Registering schemas...{Colors.NC}")
    print()

    registered = 0
    failed = 0
    skipped = 0

    for schema_file in schema_files:
        result, status = register_schema(schema_file)

        if result is None:  # Skipped
            skipped += 1
        elif result:  # Success
            registered += 1
        else:  # Failed
            failed += 1

    # Print summary
    print_summary(registered, skipped, failed)

    # Show registered subjects
    show_registered_subjects()

    # Print next steps
    print_next_steps()

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
