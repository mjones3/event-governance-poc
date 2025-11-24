# Import AsyncAPI from SwaggerHub to Confluent Schema Registry

This guide explains how to import AsyncAPI schemas from SwaggerHub into your Confluent Schema Registry.

## Overview

SwaggerHub can host AsyncAPI specifications that define your event-driven architecture. This tool extracts message schemas from AsyncAPI specs and registers them in Schema Registry.

## Prerequisites

- Schema Registry running (http://localhost:8081)
- Python 3.7+
- SwaggerHub account (free or paid)
- Required Python packages: `requests`, `pyyaml`

## Installation

```bash
pip install requests pyyaml
```

## Usage

### 1. Get Your SwaggerHub API URL

Your AsyncAPI spec URL follows this format:
```
https://api.swaggerhub.com/apis/{owner}/{api-name}/{version}
```

Example:
```
https://api.swaggerhub.com/apis/biopro/shipment-events/1.0.0
```

### 2. Set Environment Variables

```bash
# Required
export SWAGGERHUB_API_URL='https://api.swaggerhub.com/apis/your-org/your-api/1.0.0'

# Optional (for private APIs)
export SWAGGERHUB_API_KEY='your-swaggerhub-api-key'

# Optional (if Schema Registry is not on localhost)
export SCHEMA_REGISTRY_URL='http://localhost:8081'
```

### 3. Run the Import Script

```bash
cd event-governance/poc
python import-asyncapi-to-schema-registry.py
```

## What It Does

1. **Fetches AsyncAPI Spec** - Downloads your AsyncAPI specification from SwaggerHub
2. **Extracts Message Schemas** - Identifies all message definitions in your spec
3. **Converts to Avro** - Transforms JSON Schema to Avro format (default)
4. **Registers Schemas** - Uploads each schema to Schema Registry

## AsyncAPI Structure Expected

The script expects AsyncAPI 2.x or 3.x format:

```yaml
asyncapi: '2.6.0'
info:
  title: BioPro Shipment Events API
  version: '1.0.0'

channels:
  shipments/completed:
    publish:
      message:
        name: ShipmentCompleted
        contentType: application/json
        payload:
          type: object
          properties:
            shipmentNumber:
              type: integer
              description: Unique shipment number
            orderNumber:
              type: integer
              description: Associated order number
            completedDate:
              type: string
              format: date-time
            destinationCode:
              type: string
          required:
            - shipmentNumber
            - orderNumber
```

## Output Example

```
============================================================
AsyncAPI to Schema Registry Importer
============================================================

Fetching AsyncAPI from: https://api.swaggerhub.com/apis/biopro/shipment-events/1.0.0
  -> Loaded AsyncAPI version: 2.6.0

Extracting message schemas...
  Channel: shipments/completed
  Channel: shipments/created

  -> Found 5 message schemas

============================================================
Registering Schemas
============================================================

Registering schema: ShipmentCompletedEvent
  -> Successfully registered with ID: 141

Registering schema: ShipmentCreatedEvent
  -> Successfully registered with ID: 142

============================================================
Import Summary
============================================================
Successfully registered: 5
Failed: 0
```

## Schema Naming Convention

By default, the script creates subjects in Schema Registry with this pattern:
- **Avro format**: `{MessageName}Event`
- **JSON Schema format**: `{MessageName}-value`

Example:
- AsyncAPI message name: `ShipmentCompleted`
- Schema Registry subject: `ShipmentCompletedEvent`

## Advanced Options

### Import as JSON Schema Instead of Avro

Edit the script and change:
```python
importer.import_from_swaggerhub(swaggerhub_url, convert_to_avro=False)
```

### Custom Subject Naming

Modify the `register_schema` section:
```python
subject = f"custom.prefix.{schema_name}"
```

## Verification

After import, verify schemas were registered:

```bash
# List all subjects
curl http://localhost:8081/subjects

# Get specific schema
curl http://localhost:8081/subjects/ShipmentCompletedEvent/versions/latest

# View in UI
open http://localhost:8000
```

## Integration with EventCatalog

After importing to Schema Registry, sync to EventCatalog:

```bash
cd eventcatalog
npm run sync  # If you have a sync script configured
```

Or manually create event pages using the schemas from Schema Registry.

## Troubleshooting

### Error: Cannot connect to Schema Registry
- Ensure Schema Registry is running: `docker-compose ps schema-registry`
- Check URL: `curl http://localhost:8081/subjects`

### Error: 401 Unauthorized from SwaggerHub
- Set SWAGGERHUB_API_KEY for private APIs
- Verify API key is valid in SwaggerHub settings

### Error: Failed to parse AsyncAPI spec
- Verify your AsyncAPI spec is valid
- Use AsyncAPI Studio to validate: https://studio.asyncapi.com/

### Schema conversion issues
- The basic converter handles simple types
- For complex schemas (oneOf, allOf, anyOf), manual conversion may be needed
- Consider using https://github.com/asyncapi/converter-js for complex conversions

## Alternative: Manual Export/Import

If the script doesn't work for your use case:

### 1. Export from SwaggerHub
1. Go to your API in SwaggerHub
2. Click "Export" → "Download API" → "YAML" or "JSON"
3. Save the file locally

### 2. Extract and Convert Schemas
Use online tools or libraries:
- AsyncAPI Generator: https://www.asyncapi.com/tools/generator
- JSON Schema to Avro: https://github.com/allegro/json-avro-converter

### 3. Register Manually
```bash
curl -X POST http://localhost:8081/subjects/MyEvent/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d @schema.json
```

## Best Practices

1. **Version Your AsyncAPI Specs** - Use semantic versioning
2. **Test Locally First** - Import to local Schema Registry before production
3. **Document Mappings** - Keep track of which SwaggerHub specs map to which subjects
4. **Automate** - Integrate into CI/CD pipeline for automatic imports
5. **Schema Evolution** - Ensure new versions maintain backward compatibility

## References

- [AsyncAPI Specification](https://www.asyncapi.com/docs/reference/specification/latest)
- [Confluent Schema Registry API](https://docs.confluent.io/platform/current/schema-registry/develop/api.html)
- [SwaggerHub API Documentation](https://app.swaggerhub.com/help/apis/api-docs)
