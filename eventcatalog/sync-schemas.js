#!/usr/bin/env node

/**
 * Schema Registry to EventCatalog Sync Script
 *
 * Fetches schemas from Confluent Schema Registry and generates EventCatalog markdown files
 *
 * Usage:
 *   node sync-schemas.js
 */

import axios from 'axios';
import avro from 'avsc';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const SCHEMA_REGISTRY_URL = 'http://localhost:8081';

const DOMAIN_MAPPING = {
  'OrderCreatedEvent': 'Orders',
  'ApheresisPlasmaProductCreatedEvent': 'Manufacturing',
  'CollectionReceivedEvent': 'Collections'
};

const SERVICE_MAPPING = {
  'OrderCreatedEvent': 'orders-service',
  'ApheresisPlasmaProductCreatedEvent': 'manufacturing-service',
  'CollectionReceivedEvent': 'collections-service'
};

// Schema Registry Client
class SchemaRegistryClient {
  constructor(baseUrl) {
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 5000,
    });
  }

  async getAllSubjects() {
    const response = await this.client.get('/subjects');
    return response.data;
  }

  async getLatestSchema(subject) {
    try {
      const response = await this.client.get(`/subjects/${subject}/versions/latest`);
      return {
        id: response.data.id,
        subject: response.data.subject,
        version: response.data.version,
        schema: JSON.parse(response.data.schema)
      };
    } catch (error) {
      console.error(`Error fetching schema for ${subject}:`, error.message);
      return null;
    }
  }
}

// Generate example value from Avro type
function generateExampleValue(type) {
  if (typeof type === 'string') {
    switch (type) {
      case 'string': return 'example-string';
      case 'int': return 123;
      case 'long': return 1234567890;
      case 'float': return 123.45;
      case 'double': return 123.456789;
      case 'boolean': return true;
      case 'null': return null;
      default: return 'example';
    }
  }

  if (Array.isArray(type)) {
    const nonNullType = type.find(t => t !== 'null');
    return nonNullType ? generateExampleValue(nonNullType) : null;
  }

  if (type.type === 'array') {
    return [generateExampleValue(type.items)];
  }

  if (type.type === 'record') {
    const record = {};
    if (type.fields) {
      type.fields.forEach(field => {
        record[field.name] = generateExampleValue(field.type);
      });
    }
    return record;
  }

  if (type.type === 'map') {
    return { 'key1': generateExampleValue(type.values) };
  }

  return null;
}

// Generate example payload
function generateExamplePayload(schema) {
  const example = {};
  if (!schema.fields) return '{}';

  schema.fields.forEach(field => {
    example[field.name] = generateExampleValue(field.type);
  });

  return JSON.stringify(example, null, 2);
}

// Format Avro type
function formatAvroType(type) {
  if (typeof type === 'string') {
    return `\`${type}\``;
  }

  if (Array.isArray(type)) {
    const types = type.filter(t => t !== 'null');
    if (types.length === 1) {
      return formatAvroType(types[0]);
    }
    return `\`${type.join(' | ')}\``;
  }

  if (type.type === 'array') {
    return `array<${formatAvroType(type.items)}>`;
  }

  if (type.type === 'record') {
    return `\`${type.name || 'record'}\``;
  }

  if (type.type === 'map') {
    return `map<string, ${formatAvroType(type.values)}>`;
  }

  return `\`${type.type || 'unknown'}\``;
}

// Check if field is optional
function isOptionalField(type) {
  return Array.isArray(type) && type.includes('null');
}

// Build schema documentation table
function buildSchemaDocumentation(schema) {
  const fields = schema.fields || [];

  if (fields.length === 0) {
    return 'No fields documented.';
  }

  let doc = '| Field | Type | Required | Description |\n';
  doc += '|-------|------|----------|-------------|\n';

  fields.forEach(field => {
    const fieldName = field.name;
    const fieldType = formatAvroType(field.type);
    const isRequired = !isOptionalField(field.type);
    const description = field.doc || '';

    doc += `| \`${fieldName}\` | ${fieldType} | ${isRequired ? 'Yes' : 'No'} | ${description} |\n`;
  });

  return doc;
}

// Generate event markdown
function generateEventMarkdown(schemaData) {
  const { subject, schema, version, id } = schemaData;
  const eventName = subject.replace(/Event$/, '');
  const domain = DOMAIN_MAPPING[subject] || 'General';
  const service = SERVICE_MAPPING[subject] || 'unknown-service';
  const schemaDoc = buildSchemaDocumentation(schema);

  return `---
id: ${eventName}
name: ${eventName}
version: '${version}'
summary: Event ${eventName} - BioPro System
owners:
    - ${service}
producers:
    - ${service}
consumers: []
---

# ${eventName} Event

**Schema ID**: ${id}
**Schema Version**: ${version}
**Subject**: ${subject}
**Domain**: ${domain}

## Description

${schema.doc || 'Event published by the BioPro system.'}

## Schema

\`\`\`json
${JSON.stringify(schema, null, 2)}
\`\`\`

## Fields

${schemaDoc}

## Schema Evolution

This event uses Avro schema validation through Confluent Schema Registry.

- **Schema ID**: ${id}
- **Version**: ${version}
- **Compatibility**: BACKWARD (default)

## Producers

- **Service**: ${service}
- **Topic**: \`biopro.${domain.toLowerCase()}.events\`

## Message Format

Messages are serialized using **Avro** with the schema ID embedded in the message header (magic byte + schema ID).

## Example Payload

\`\`\`json
${generateExamplePayload(schema)}
\`\`\`

<NodeGraph />
`;
}

// Generate service markdown
function generateServiceMarkdown(serviceName, events, domain) {
  const publishesYaml = events.map(e => `    - id: ${e.name}\n      version: '${e.version}'`).join('\n');

  return `---
id: ${serviceName}
name: ${serviceName}
version: 1.0.0
summary: ${serviceName} - BioPro Event Producer
owners:
    - BioPro Platform Team
publishes:
${publishesYaml}
subscribes: []
---

# ${serviceName}

BioPro microservice that publishes events to Kafka.

## Published Events

${events.map(e => `- **${e.name}** (v${e.version})`).join('\n')}

## Domain

**${domain}**

## Infrastructure

- **Kafka Broker**: Redpanda
- **Schema Registry**: Confluent Schema Registry
- **Serialization**: Avro with schema validation
- **DLQ**: Dead Letter Queue for failed messages

## Metrics

- Schema validation success/failure rates
- Event publish success/failure rates
- DLQ routing metrics

<NodeGraph />
`;
}

// Generate domain markdown
function generateDomainMarkdown(domainName, events, services) {
  return `---
id: ${domainName}
name: ${domainName}
version: 1.0.0
summary: ${domainName} Domain - BioPro Event Governance
owners:
    - BioPro Platform Team
---

# ${domainName} Domain

Domain containing events and services related to ${domainName.toLowerCase()} operations in the BioPro system.

## Events

${events.map(e => `- **${e.name}** (v${e.version})`).join('\n')}

## Services

${services.map(s => `- ${s.id}`).join('\n')}

## Event Governance

All events in this domain:
- Are validated against registered Avro schemas
- Use Confluent Schema Registry for schema management
- Support schema evolution with compatibility checks
- Include DLQ routing for validation failures
- Publish metrics for monitoring

<NodeGraph />
`;
}

// Main function
async function main() {
  console.log(`\n🔄 Fetching schemas from Schema Registry: ${SCHEMA_REGISTRY_URL}`);

  const client = new SchemaRegistryClient(SCHEMA_REGISTRY_URL);

  try {
    // Get all subjects
    const subjects = await client.getAllSubjects();
    const eventSchemas = subjects.filter(s => !s.includes('-value') && !s.includes('-key'));

    console.log(`📋 Found ${eventSchemas.length} event schema(s): ${eventSchemas.join(', ')}`);

    const events = [];
    const servicesMap = new Map();
    const domainsMap = new Map();

    // Fetch and process each schema
    for (const subject of eventSchemas) {
      const schemaData = await client.getLatestSchema(subject);

      if (!schemaData) {
        console.warn(`⚠️  Skipping ${subject} - could not fetch schema`);
        continue;
      }

      console.log(`✅ Loaded schema: ${subject} (ID: ${schemaData.id}, Version: ${schemaData.version})`);

      const eventName = subject.replace(/Event$/, '');
      const domain = DOMAIN_MAPPING[subject] || 'General';
      const serviceName = SERVICE_MAPPING[subject] || 'unknown-service';

      // Create event directory and write markdown
      const eventDir = path.join(__dirname, 'events', eventName);
      await fs.mkdir(eventDir, { recursive: true });

      const eventMarkdown = generateEventMarkdown(schemaData);
      await fs.writeFile(path.join(eventDir, 'index.md'), eventMarkdown);
      console.log(`  ✍️  Written: events/${eventName}/index.md`);

      // Track for services and domains
      events.push({ name: eventName, version: schemaData.version, domain });

      if (!servicesMap.has(serviceName)) {
        servicesMap.set(serviceName, []);
      }
      servicesMap.get(serviceName).push({ name: eventName, version: schemaData.version });

      if (!domainsMap.has(domain)) {
        domainsMap.set(domain, { events: [], services: new Set() });
      }
      domainsMap.get(domain).events.push({ name: eventName, version: schemaData.version });
      domainsMap.get(domain).services.add(serviceName);
    }

    // Generate service markdown
    for (const [serviceName, serviceEvents] of servicesMap.entries()) {
      const domain = serviceEvents[0]?.domain || events.find(e => serviceEvents.some(se => se.name === e.name))?.domain || 'General';
      const serviceDir = path.join(__dirname, 'services', serviceName);
      await fs.mkdir(serviceDir, { recursive: true });

      const serviceMarkdown = generateServiceMarkdown(serviceName, serviceEvents, domain);
      await fs.writeFile(path.join(serviceDir, 'index.md'), serviceMarkdown);
      console.log(`  ✍️  Written: services/${serviceName}/index.md`);
    }

    // Generate domain markdown
    for (const [domainName, data] of domainsMap.entries()) {
      const domainServices = Array.from(data.services).map(s => ({ id: s }));
      const domainDir = path.join(__dirname, 'domains', domainName);
      await fs.mkdir(domainDir, { recursive: true });

      const domainMarkdown = generateDomainMarkdown(domainName, data.events, domainServices);
      await fs.writeFile(path.join(domainDir, 'index.md'), domainMarkdown);
      console.log(`  ✍️  Written: domains/${domainName}/index.md`);
    }

    console.log(`\n✨ Successfully synced ${events.length} event(s), ${servicesMap.size} service(s), ${domainsMap.size} domain(s)\n`);

  } catch (error) {
    console.error('❌ Error syncing schemas:', error.message);
    process.exit(1);
  }
}

main();
