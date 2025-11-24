#!/usr/bin/env python3
"""
Import AsyncAPI schemas from SwaggerHub to Confluent Schema Registry

This script:
1. Fetches AsyncAPI specs from SwaggerHub
2. Extracts message schemas from AsyncAPI
3. Converts them to Avro/JSON Schema format
4. Registers them in Confluent Schema Registry
"""

import os
import json
import requests
import yaml
from typing import Dict, Any, List
from pathlib import Path

# Configuration
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
SWAGGERHUB_API_KEY = os.getenv("SWAGGERHUB_API_KEY", "")  # Optional for public APIs

class AsyncAPIImporter:
    def __init__(self, schema_registry_url: str):
        self.schema_registry_url = schema_registry_url

    def fetch_asyncapi_from_swaggerhub(self, api_url: str) -> Dict[str, Any]:
        """Fetch AsyncAPI spec from SwaggerHub"""
        print(f"Fetching AsyncAPI from: {api_url}")

        headers = {}
        if SWAGGERHUB_API_KEY:
            headers["Authorization"] = SWAGGERHUB_API_KEY

        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        # SwaggerHub returns YAML or JSON
        content_type = response.headers.get('content-type', '')

        if 'yaml' in content_type or api_url.endswith('.yaml'):
            spec = yaml.safe_load(response.text)
        else:
            spec = response.json()

        print(f"  -> Loaded AsyncAPI version: {spec.get('asyncapi', 'unknown')}")
        return spec

    def extract_message_schemas(self, asyncapi_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract message schemas from AsyncAPI spec"""
        print("\nExtracting message schemas...")

        schemas = []
        channels = asyncapi_spec.get('channels', {})

        for channel_name, channel in channels.items():
            print(f"  Channel: {channel_name}")

            # Check publish operations (messages sent to this channel)
            if 'publish' in channel:
                message = channel['publish'].get('message')
                if message:
                    schema = self._extract_schema_from_message(message, channel_name, 'publish')
                    if schema:
                        schemas.append(schema)

            # Check subscribe operations (messages received from this channel)
            if 'subscribe' in channel:
                message = channel['subscribe'].get('message')
                if message:
                    schema = self._extract_schema_from_message(message, channel_name, 'subscribe')
                    if schema:
                        schemas.append(schema)

        # Also check components/messages
        components = asyncapi_spec.get('components', {})
        messages = components.get('messages', {})

        for message_name, message in messages.items():
            schema = self._extract_schema_from_message(message, message_name, 'component')
            if schema:
                schemas.append(schema)

        print(f"\n  -> Found {len(schemas)} message schemas")
        return schemas

    def _extract_schema_from_message(self, message: Dict[str, Any], context: str, operation: str) -> Dict[str, Any]:
        """Extract schema from a message definition"""

        # Handle message reference
        if '$ref' in message:
            # Would need to resolve reference
            print(f"    Warning: Message reference found but not resolved: {message['$ref']}")
            return None

        # Get schema from payload
        payload = message.get('payload', {})

        if '$ref' in payload:
            print(f"    Warning: Payload reference found but not resolved: {payload['$ref']}")
            return None

        if not payload:
            return None

        # Extract schema name
        schema_name = message.get('name') or payload.get('title') or context

        return {
            'name': schema_name,
            'context': context,
            'operation': operation,
            'schema': payload,
            'content_type': message.get('contentType', 'application/json'),
            'description': message.get('description', '')
        }

    def convert_json_schema_to_avro(self, json_schema: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Convert JSON Schema to Avro schema"""

        # Basic conversion - this is simplified
        # For production, use a proper converter library

        avro_schema = {
            "type": "record",
            "name": name,
            "namespace": "com.biopro.asyncapi",
            "doc": json_schema.get('description', ''),
            "fields": []
        }

        properties = json_schema.get('properties', {})
        required = json_schema.get('required', [])

        for prop_name, prop_schema in properties.items():
            field = self._convert_property_to_avro_field(
                prop_name,
                prop_schema,
                prop_name in required
            )
            avro_schema['fields'].append(field)

        return avro_schema

    def _convert_property_to_avro_field(self, name: str, schema: Dict[str, Any], required: bool) -> Dict[str, Any]:
        """Convert a JSON Schema property to an Avro field"""

        json_type = schema.get('type', 'string')

        # Map JSON Schema types to Avro types
        type_mapping = {
            'string': 'string',
            'integer': 'long',
            'number': 'double',
            'boolean': 'boolean',
            'array': {'type': 'array', 'items': 'string'},
            'object': {'type': 'map', 'values': 'string'}
        }

        avro_type = type_mapping.get(json_type, 'string')

        # Make optional if not required
        if not required:
            avro_type = ['null', avro_type]

        field = {
            'name': name,
            'type': avro_type,
            'doc': schema.get('description', '')
        }

        # Add default for optional fields
        if not required and 'default' not in schema:
            field['default'] = None

        return field

    def register_schema(self, subject: str, schema: Dict[str, Any]) -> bool:
        """Register schema to Schema Registry"""

        print(f"\nRegistering schema: {subject}")

        payload = {
            "schema": json.dumps(schema)
        }

        try:
            response = requests.post(
                f"{self.schema_registry_url}/subjects/{subject}/versions",
                json=payload,
                headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
                timeout=10
            )

            if response.status_code in [200, 201]:
                result = response.json()
                schema_id = result.get('id')
                print(f"  -> Successfully registered with ID: {schema_id}")
                return True
            else:
                print(f"  -> Failed: {response.status_code}")
                print(f"     {response.text}")
                return False

        except Exception as e:
            print(f"  -> Error: {e}")
            return False

    def import_from_swaggerhub(self, swaggerhub_url: str, convert_to_avro: bool = True):
        """Main import process"""

        print("=" * 60)
        print("AsyncAPI to Schema Registry Importer")
        print("=" * 60)
        print()

        # 1. Fetch AsyncAPI spec
        try:
            asyncapi_spec = self.fetch_asyncapi_from_swaggerhub(swaggerhub_url)
        except Exception as e:
            print(f"ERROR: Failed to fetch AsyncAPI spec: {e}")
            return

        # 2. Extract message schemas
        message_schemas = self.extract_message_schemas(asyncapi_spec)

        if not message_schemas:
            print("No message schemas found in AsyncAPI spec")
            return

        # 3. Convert and register each schema
        print("\n" + "=" * 60)
        print("Registering Schemas")
        print("=" * 60)

        success_count = 0
        failed_count = 0

        for msg_schema in message_schemas:
            schema_name = msg_schema['name']
            json_schema = msg_schema['schema']

            # Convert to Avro if requested
            if convert_to_avro:
                schema_to_register = self.convert_json_schema_to_avro(
                    json_schema,
                    schema_name
                )
                subject = f"{schema_name}Event"
            else:
                # Register as JSON Schema
                schema_to_register = json_schema
                subject = f"{schema_name}-value"

            # Register to Schema Registry
            if self.register_schema(subject, schema_to_register):
                success_count += 1
            else:
                failed_count += 1

        # Summary
        print("\n" + "=" * 60)
        print("Import Summary")
        print("=" * 60)
        print(f"Successfully registered: {success_count}")
        print(f"Failed: {failed_count}")
        print()


def main():
    """Main function"""

    # Example SwaggerHub URLs:
    # https://app.swaggerhub.com/apis/{owner}/{api}/{version}
    # https://api.swaggerhub.com/apis/{owner}/{api}/{version}

    # For testing - you would replace with your actual SwaggerHub URL
    swaggerhub_url = os.getenv(
        "SWAGGERHUB_API_URL",
        "https://api.swaggerhub.com/apis/your-org/your-asyncapi/1.0.0"
    )

    if "your-org" in swaggerhub_url:
        print("=" * 60)
        print("Please set SWAGGERHUB_API_URL environment variable")
        print("=" * 60)
        print()
        print("Example:")
        print("  export SWAGGERHUB_API_URL='https://api.swaggerhub.com/apis/myorg/myapi/1.0.0'")
        print("  python import-asyncapi-to-schema-registry.py")
        print()
        print("Or for private APIs, also set:")
        print("  export SWAGGERHUB_API_KEY='your-api-key'")
        print()
        return 1

    importer = AsyncAPIImporter(SCHEMA_REGISTRY_URL)
    importer.import_from_swaggerhub(swaggerhub_url, convert_to_avro=True)

    return 0


if __name__ == "__main__":
    exit(main())
