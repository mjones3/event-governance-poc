#!/usr/bin/env python3
"""
BioPro Schema Registry - Bulk Schema Registration Tool

Registers all Avro schemas from schemas/avro/ to Confluent Schema Registry.
After registration, SpringWolf can automatically document them.

Usage:
    python register_schemas.py
    python register_schemas.py --registry http://localhost:8081
    python register_schemas.py --schemas-dir ./schemas/avro
"""

import os
import sys
import json
import argparse
from pathlib import Path
import requests
from typing import List, Tuple

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_header():
    """Print script header"""
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}BioPro Schema Registry - Bulk Registration Tool{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")


def check_schema_registry(url: str) -> bool:
    """Check if Schema Registry is accessible"""
    print(f"{Colors.BLUE}[1/3] Checking Schema Registry connectivity...{Colors.NC}")
    try:
        response = requests.get(f"{url}/subjects", timeout=5)
        response.raise_for_status()
        print(f"{Colors.GREEN}Connected to Schema Registry at {url}{Colors.NC}\n")
        return True
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}ERROR: Cannot connect to Schema Registry at {url}{Colors.NC}")
        print(f"{Colors.YELLOW}  Error: {e}{Colors.NC}")
        print(f"{Colors.YELLOW}  Make sure Schema Registry is running:{Colors.NC}")
        print(f"{Colors.YELLOW}    docker-compose ps schema-registry{Colors.NC}")
        return False


def find_schema_files(schemas_dir: str) -> List[Path]:
    """Find all .avsc files in the schemas directory"""
    print(f"{Colors.BLUE}[2/3] Scanning for schema files...{Colors.NC}")
    print(f"  Directory: {schemas_dir}")

    schemas_path = Path(schemas_dir)
    if not schemas_path.exists():
        print(f"{Colors.RED}ERROR: Schemas directory not found: {schemas_dir}{Colors.NC}")
        return []

    schema_files = list(schemas_path.glob("*.avsc"))

    if not schema_files:
        print(f"{Colors.RED}ERROR: No .avsc files found in {schemas_dir}{Colors.NC}")
        return []

    print(f"{Colors.GREEN}Found {len(schema_files)} schema file(s){Colors.NC}")
    for schema_file in schema_files:
        print(f"  - {schema_file.name}")
    print()

    return schema_files


def register_schema(registry_url: str, schema_file: Path) -> Tuple[bool, str]:
    """Register a single schema to Schema Registry"""
    schema_name = schema_file.stem
    subject = f"{schema_name}-value"

    print(f"{Colors.YELLOW}Registering:{Colors.NC} {schema_name}")
    print(f"  File: {schema_file}")
    print(f"  Subject: {subject}")

    try:
        # Read the Avro schema file
        with open(schema_file, 'r') as f:
            schema_content = json.load(f)

        # Prepare the payload for Schema Registry
        payload = {
            "schema": json.dumps(schema_content)
        }

        # Register the schema
        response = requests.post(
            f"{registry_url}/subjects/{subject}/versions",
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            json=payload,
            timeout=10
        )

        if response.status_code in [200, 201]:
            result = response.json()
            schema_id = result.get('id', 'unknown')
            print(f"{Colors.GREEN}  Registered successfully{Colors.NC}")
            print(f"    Schema ID: {schema_id}")
            print(f"    HTTP Status: {response.status_code}")
            return True, str(schema_id)
        else:
            print(f"{Colors.RED}  Registration failed{Colors.NC}")
            print(f"    HTTP Status: {response.status_code}")
            print(f"    Response: {response.text}")
            return False, ""

    except json.JSONDecodeError as e:
        print(f"{Colors.RED}  Invalid JSON in schema file{Colors.NC}")
        print(f"    Error: {e}")
        return False, ""
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}  Request failed{Colors.NC}")
        print(f"    Error: {e}")
        return False, ""
    except Exception as e:
        print(f"{Colors.RED}  Unexpected error{Colors.NC}")
        print(f"    Error: {e}")
        return False, ""
    finally:
        print()


def verify_registration(registry_url: str):
    """Verify registered subjects in Schema Registry"""
    print(f"{Colors.BLUE}Verifying registered subjects:{Colors.NC}")
    try:
        response = requests.get(f"{registry_url}/subjects", timeout=5)
        response.raise_for_status()
        subjects = response.json()

        biopro_subjects = [s for s in subjects if any(
            event in s for event in [
                "ApheresisPlasmaProductCreated",
                "CollectionReceived",
                "OrderCreated"
            ]
        )]

        if biopro_subjects:
            for subject in biopro_subjects:
                print(f"  {subject}")
        else:
            print(f"  {Colors.YELLOW}No BioPro subjects found{Colors.NC}")

    except requests.exceptions.RequestException:
        print(f"  {Colors.YELLOW}Could not verify subjects{Colors.NC}")

    print()


def print_next_steps(registry_url: str):
    """Print next steps for the user"""
    print(f"{Colors.YELLOW}Next Steps:{Colors.NC}")
    print(f"  1. Verify schemas: {Colors.BLUE}curl {registry_url}/subjects{Colors.NC}")
    print(f"  2. Add SpringWolf dependencies to your services")
    print(f"  3. Configure SpringWolf in application.yml")
    print(f"  4. Access AsyncAPI docs: {Colors.BLUE}http://localhost:8082/springwolf/docs{Colors.NC}")
    print(f"  5. Sync to EventCatalog: {Colors.BLUE}cd eventcatalog && npm run generate{Colors.NC}")
    print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Register Avro schemas to Confluent Schema Registry'
    )
    parser.add_argument(
        '--registry',
        default=os.environ.get('SCHEMA_REGISTRY_URL', 'http://localhost:8081'),
        help='Schema Registry URL (default: http://localhost:8081)'
    )
    parser.add_argument(
        '--schemas-dir',
        default='./schemas/avro',
        help='Directory containing .avsc schema files (default: ./schemas/avro)'
    )

    args = parser.parse_args()

    print_header()
    print(f"{Colors.YELLOW}Schema Registry URL:{Colors.NC} {args.registry}")
    print(f"{Colors.YELLOW}Schemas Directory:{Colors.NC} {args.schemas_dir}\n")

    # Check Schema Registry connectivity
    if not check_schema_registry(args.registry):
        sys.exit(1)

    # Find schema files
    schema_files = find_schema_files(args.schemas_dir)
    if not schema_files:
        sys.exit(1)

    # Register each schema
    print(f"{Colors.BLUE}[3/3] Registering schemas...{Colors.NC}\n")

    registered = 0
    failed = 0

    for schema_file in schema_files:
        success, schema_id = register_schema(args.registry, schema_file)
        if success:
            registered += 1
        else:
            failed += 1

    # Summary
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.GREEN}Registration complete!{Colors.NC}")
    print(f"  {Colors.GREEN}Successfully registered: {registered}{Colors.NC}")
    if failed > 0:
        print(f"  {Colors.RED}Failed: {failed}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")

    # Verify registration
    verify_registration(args.registry)

    # Show next steps
    print_next_steps(args.registry)

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
