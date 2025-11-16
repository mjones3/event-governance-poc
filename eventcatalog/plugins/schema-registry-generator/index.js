import axios from 'axios';
import avro from 'avsc';

/**
 * EventCatalog Generator Plugin for Confluent Schema Registry
 *
 * This plugin:
 * 1. Connects to Confluent Schema Registry
 * 2. Fetches all registered schemas
 * 3. Parses Avro schemas
 * 4. Generates EventCatalog events, services, and domains
 */

class SchemaRegistryClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 5000,
    });
  }

  /**
   * Get all subjects (schema names) from registry
   */
  async getAllSubjects() {
    try {
      const response = await this.client.get('/subjects');
      return response.data;
    } catch (error) {
      console.error('Error fetching subjects from Schema Registry:', error.message);
      throw error;
    }
  }

  /**
   * Get latest version of a schema by subject name
   */
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

  /**
   * Get all versions of a schema
   */
  async getSchemaVersions(subject) {
    try {
      const response = await this.client.get(`/subjects/${subject}/versions`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching versions for ${subject}:`, error.message);
      return [];
    }
  }
}

/**
 * Convert Avro schema to EventCatalog event documentation
 */
function avroToEventCatalog(schemaData, config) {
  const { subject, schema, version, id } = schemaData;
  const { domainMapping, serviceMapping } = config;

  // Parse Avro schema
  const avroType = avro.Type.forSchema(schema);

  // Extract event name (remove 'Event' suffix if present for cleaner naming)
  const eventName = subject.replace(/Event$/, '');

  // Get domain and service from config
  const domain = domainMapping[subject] || 'General';
  const service = serviceMapping[subject] || 'unknown-service';

  // Build schema documentation
  const schemaDoc = buildSchemaDocumentation(schema, avroType);

  // Create event object for EventCatalog
  return {
    name: eventName,
    version: version.toString(),
    summary: `Event: ${eventName}`,
    markdown: `
# ${eventName} Event

**Schema ID**: ${id}
**Schema Version**: ${version}
**Subject**: ${subject}

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
`,
    badges: [
      {
        content: `v${version}`,
        backgroundColor: 'blue',
        textColor: 'white',
      },
      {
        content: `Schema ID: ${id}`,
        backgroundColor: 'green',
        textColor: 'white',
      }
    ],
    owners: [service],
    producers: [service],
    consumers: [],
    domain: domain,
  };
}

/**
 * Build field documentation from Avro schema
 */
function buildSchemaDocumentation(schema, avroType) {
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

/**
 * Format Avro type for documentation
 */
function formatAvroType(type) {
  if (typeof type === 'string') {
    return `\`${type}\``;
  }

  if (Array.isArray(type)) {
    // Union type (e.g., ["null", "string"] for optional fields)
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

/**
 * Check if field is optional (union with null)
 */
function isOptionalField(type) {
  return Array.isArray(type) && type.includes('null');
}

/**
 * Generate example payload from Avro schema
 */
function generateExamplePayload(schema) {
  const example = {};

  if (!schema.fields) {
    return '{}';
  }

  schema.fields.forEach(field => {
    example[field.name] = generateExampleValue(field.type);
  });

  return JSON.stringify(example, null, 2);
}

/**
 * Generate example value based on Avro type
 */
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
    // Union type - use first non-null type
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

/**
 * Create service documentation
 */
function createServiceDoc(serviceName, events, domain) {
  return {
    id: serviceName,
    name: serviceName,
    version: '1.0.0',
    summary: `${serviceName} - BioPro Event Producer`,
    markdown: `
# ${serviceName}

BioPro microservice that publishes events to Kafka.

## Published Events

${events.map(e => `- **${e.name}Event** (v${e.version})`).join('\n')}

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
`,
    owners: ['BioPro Platform Team'],
    domain: domain,
  };
}

/**
 * Create domain documentation
 */
function createDomainDoc(domainName, events, services) {
  return {
    id: domainName,
    name: domainName,
    version: '1.0.0',
    summary: `${domainName} Domain - BioPro Event Governance`,
    markdown: `
# ${domainName} Domain

Domain containing events and services related to ${domainName.toLowerCase()} operations in the BioPro system.

## Events

${events.map(e => `- **${e.name}Event** (v${e.version})`).join('\n')}

## Services

${services.map(s => `- ${s.id}`).join('\n')}

## Event Governance

All events in this domain:
- Are validated against registered Avro schemas
- Use Confluent Schema Registry for schema management
- Support schema evolution with compatibility checks
- Include DLQ routing for validation failures
- Publish metrics for monitoring
`,
    owners: ['BioPro Platform Team'],
  };
}

/**
 * Main generator function
 */
export default async function schemaRegistryGenerator(config) {
  const { schemaRegistryUrl, domainMapping, serviceMapping } = config;

  console.log(`\n🔄 Fetching schemas from Schema Registry: ${schemaRegistryUrl}`);

  const client = new SchemaRegistryClient(schemaRegistryUrl);

  try {
    // Get all subjects (schema names)
    const subjects = await client.getAllSubjects();

    // Filter out auto-registered topic-value schemas (we only want named event schemas)
    const eventSchemas = subjects.filter(s => !s.includes('-value') && !s.includes('-key'));

    console.log(`📋 Found ${eventSchemas.length} event schema(s): ${eventSchemas.join(', ')}`);

    // Fetch all schemas
    const events = [];
    const servicesMap = new Map();
    const domainsMap = new Map();

    for (const subject of eventSchemas) {
      const schemaData = await client.getLatestSchema(subject);

      if (!schemaData) {
        console.warn(`⚠️  Skipping ${subject} - could not fetch schema`);
        continue;
      }

      console.log(`✅ Loaded schema: ${subject} (ID: ${schemaData.id}, Version: ${schemaData.version})`);

      // Convert to EventCatalog format
      const event = avroToEventCatalog(schemaData, config);
      events.push(event);

      // Track services
      const serviceName = serviceMapping[subject] || 'unknown-service';
      if (!servicesMap.has(serviceName)) {
        servicesMap.set(serviceName, []);
      }
      servicesMap.get(serviceName).push(event);

      // Track domains
      const domainName = event.domain;
      if (!domainsMap.has(domainName)) {
        domainsMap.set(domainName, { events: [], services: new Set() });
      }
      domainsMap.get(domainName).events.push(event);
      domainsMap.get(domainName).services.add(serviceName);
    }

    // Create service docs
    const services = Array.from(servicesMap.entries()).map(([serviceName, serviceEvents]) => {
      const domain = serviceEvents[0]?.domain || 'General';
      return createServiceDoc(serviceName, serviceEvents, domain);
    });

    // Create domain docs
    const domains = Array.from(domainsMap.entries()).map(([domainName, data]) => {
      const domainServices = services.filter(s => s.domain === domainName);
      return createDomainDoc(domainName, data.events, domainServices);
    });

    console.log(`\n✨ Generated ${events.length} event(s), ${services.length} service(s), ${domains.length} domain(s)\n`);

    return {
      events,
      services,
      domains,
    };

  } catch (error) {
    console.error('❌ Error generating catalog from Schema Registry:', error.message);

    // Return empty catalog on error
    return {
      events: [],
      services: [],
      domains: [],
    };
  }
};
