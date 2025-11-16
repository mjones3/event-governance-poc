# BioPro Event Catalog

Event documentation automatically generated from Confluent Schema Registry.

## Overview

This EventCatalog instance provides auto-generated documentation for all events registered in the BioPro Schema Registry. It includes:

- **Events**: Detailed documentation for each event schema
- **Services**: Information about services that produce events
- **Domains**: Logical grouping of events by business domain (Orders, Manufacturing, Collections)

## Quick Start

### 1. Sync Schemas from Schema Registry

Run the sync script to fetch latest schemas and generate documentation:

```bash
cd eventcatalog
npm run sync
```

This will:
- Connect to Schema Registry at `http://localhost:8081`
- Fetch all registered event schemas
- Generate markdown documentation for events, services, and domains
- Place files in `events/`, `services/`, and `domains/` directories

### 2. Build and View Catalog

```bash
# Development mode with hot reload
npm run dev

# Build static site
npm run build

# Serve built site
npm run serve
```

The catalog will be available at `http://localhost:3000`

## Scripts

- `npm run sync` - Sync schemas from Schema Registry and generate documentation
- `npm run dev` - Start development server (http://localhost:3000)
- `npm run build` - Build static EventCatalog site
- `npm run serve` - Serve the built static site

## Architecture

### Sync Process

1. **Fetch Schemas**: Connects to Confluent Schema Registry REST API
2. **Parse Avro**: Uses `avsc` library to parse Avro schemas
3. **Generate Markdown**: Creates EventCatalog-compatible markdown files
4. **Organize**: Structures documentation by events, services, and domains

### Directory Structure

```
eventcatalog/
├── events/                    # Event documentation
│   ├── OrderCreated/
│   │   └── index.md
│   ├── ApheresisPlasmaProductCreated/
│   │   └── index.md
│   └── CollectionReceived/
│       └── index.md
├── services/                  # Service documentation
│   ├── orders-service/
│   ├── manufacturing-service/
│   └── collections-service/
├── domains/                   # Domain documentation
│   ├── Orders/
│   ├── Manufacturing/
│   └── Collections/
├── sync-schemas.js           # Schema sync script
├── eventcatalog.config.js    # EventCatalog configuration
└── package.json
```

## Configuration

### Schema Registry URL

The sync script connects to Schema Registry at `http://localhost:8081` by default. To change this, edit `sync-schemas.js`:

```javascript
const SCHEMA_REGISTRY_URL = 'http://your-schema-registry:8081';
```

### Domain Mapping

Edit `DOMAIN_MAPPING` in `sync-schemas.js` to map schemas to business domains:

```javascript
const DOMAIN_MAPPING = {
  'OrderCreatedEvent': 'Orders',
  'ApheresisPlasmaProductCreatedEvent': 'Manufacturing',
  'CollectionReceivedEvent': 'Collections'
};
```

### Service Mapping

Edit `SERVICE_MAPPING` in `sync-schemas.js` to map schemas to services:

```javascript
const SERVICE_MAPPING = {
  'OrderCreatedEvent': 'orders-service',
  'ApheresisPlasmaProductCreatedEvent': 'manufacturing-service',
  'CollectionReceivedEvent': 'collections-service'
};
```

## Features

### Generated Documentation Includes:

**For Events:**
- Schema ID and version
- Full Avro schema (JSON)
- Field-level documentation table
- Example payload
- Schema evolution info
- Producing services
- Kafka topics

**For Services:**
- List of published events
- Infrastructure details
- Metrics information
- Domain association

**For Domains:**
- Events in the domain
- Associated services
- Governance policies

## Automation

### Continuous Sync

To keep documentation in sync with Schema Registry, you can:

1. **Manual**: Run `npm run sync` whenever schemas change
2. **Git Hook**: Add to pre-commit or pre-push hook
3. **CI/CD**: Run as part of deployment pipeline
4. **Scheduled**: Use cron job or scheduled task

Example cron (every hour):
```bash
0 * * * * cd /path/to/eventcatalog && npm run sync
```

## Integration with POC

This EventCatalog integrates with the BioPro Event Governance POC:

- **Schema Registry**: `http://localhost:8081`
- **Schemas**: OrderCreatedEvent, ApheresisPlasmaProductCreatedEvent, CollectionReceivedEvent
- **Services**: orders-service (8080), manufacturing-service (8082), collections-service (8083)
- **Kafka**: Redpanda on port 19092
- **Monitoring**: Grafana on port 3000

## Troubleshooting

### Schema Registry Connection Error

If sync fails with connection error:
1. Verify Schema Registry is running: `curl http://localhost:8081/subjects`
2. Check docker-compose services: `docker-compose ps`
3. Verify network connectivity

### No Schemas Found

If sync finds 0 schemas:
1. Check schemas are registered: `curl http://localhost:8081/subjects`
2. Register schemas using the registration scripts in the POC
3. Verify schema naming (script filters out `-value` and `-key` subjects)

### EventCatalog Won't Start

If `npm run dev` fails:
1. Run `npm install` to ensure dependencies are installed
2. Check Node.js version (requires Node 16+)
3. Clear cache: `rm -rf node_modules package-lock.json && npm install`

## Resources

- [EventCatalog Documentation](https://www.eventcatalog.dev/)
- [Confluent Schema Registry API](https://docs.confluent.io/platform/current/schema-registry/develop/api.html)
- [Apache Avro](https://avro.apache.org/)
- [BioPro POC Repository](https://github.com/mjones3/event-governance-poc)
