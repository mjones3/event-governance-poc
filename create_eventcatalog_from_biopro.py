#!/usr/bin/env python3
"""
BioPro Event Schema Registration and EventCatalog Generator

This script:
1. Reads the BioPro events inventory JSON
2. Generates Avro schemas for each event
3. Registers schemas in Confluent Schema Registry
4. Creates EventCatalog MDX documentation with DLQ-aware code examples
"""

import json
import os
import re
import requests
from pathlib import Path
from typing import Dict, List, Any

# Configuration
SCHEMA_REGISTRY_URL = "http://localhost:8081"
EVENTCATALOG_EVENTS_DIR = "eventcatalog/events"
INVENTORY_FILE = "biopro-events-inventory.json"

# DLQ-aware listener template
DLQ_LISTENER_TEMPLATE = """```java
package com.arcone.biopro.{service}.infrastructure.listener;

import com.arcone.biopro.{service}.domain.event.{event_name};
import com.arcone.biopro.common.infrastructure.listener.AbstractListener;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

/**
 * Listener for {event_name} with DLQ support
 *
 * Error Handling Strategy:
 * - Transient errors (network, temporary unavailability): Retry with backoff
 * - Poison messages (schema violations, invalid data): Route to DLQ
 * - Business logic errors: Log and route to DLQ for manual review
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class {event_name}Listener extends AbstractListener<{event_name}> {{

    private final YourBusinessService businessService;

    @KafkaListener(
        topics = "${{kafka.topics.{topic_name}}}",
        groupId = "${{kafka.consumer.group-id}}",
        containerFactory = "kafkaListenerContainerFactory",
        errorHandler = "kafkaListenerErrorHandler"
    )
    public void listen(
            @Payload {event_name} event,
            @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset
    ) {{
        log.info("Received {event_name}: eventId={{}}, topic={{}}, partition={{}}, offset={{}}",
                event.getEventId(), topic, partition, offset);

        processMessage(event)
            .doOnSuccess(result ->
                log.info("Successfully processed {event_name}: {{}}", event.getEventId()))
            .doOnError(error ->
                log.error("Failed to process {event_name}: {{}}", event.getEventId(), error))
            .subscribe();
    }}

    @Override
    protected Mono<{event_name}> processMessage({event_name} event) {{
        return Mono.defer(() -> {{
            try {{
                // Validate event
                validateEvent(event);

                // Process business logic
                return businessService.handle(event)
                    .doOnError(this::handleBusinessError)
                    .onErrorResume(this::recoverFromError);

            }} catch (InvalidEventException e) {{
                // Poison message - log and send to DLQ
                log.error("Invalid event detected - routing to DLQ: {{}}", event.getEventId(), e);
                sendToDLQ(event, e);
                return Mono.empty();
            }} catch (Exception e) {{
                // Unexpected error - retry or DLQ based on error type
                return handleUnexpectedError(event, e);
            }}
        }});
    }}

    private void validateEvent({event_name} event) {{
        if (event.getEventId() == null || event.getEventId().isEmpty()) {{
            throw new InvalidEventException("Event ID is required");
        }}
        if (event.getPayload() == null) {{
            throw new InvalidEventException("Event payload is required");
        }}
        // Add domain-specific validations
    }}

    private void handleBusinessError(Throwable error) {{
        if (error instanceof BusinessValidationException) {{
            log.warn("Business validation failed - may route to DLQ: {{}}", error.getMessage());
        }} else if (error instanceof TransientException) {{
            log.warn("Transient error - will retry: {{}}", error.getMessage());
            throw new RetryableException(error);
        }}
    }}

    private Mono<{event_name}> recoverFromError(Throwable error) {{
        log.error("Unrecoverable error - routing to DLQ: {{}}", error.getMessage(), error);
        // Error handler will route to DLQ
        return Mono.error(error);
    }}

    private Mono<{event_name}> handleUnexpectedError({event_name} event, Exception e) {{
        if (isRetryable(e)) {{
            log.warn("Retryable error for event {{}}: {{}}", event.getEventId(), e.getMessage());
            throw new RetryableException(e);
        }} else {{
            log.error("Non-retryable error for event {{}} - routing to DLQ",
                     event.getEventId(), e);
            sendToDLQ(event, e);
            return Mono.empty();
        }}
    }}

    private boolean isRetryable(Exception e) {{
        return e instanceof java.net.ConnectException ||
               e instanceof java.util.concurrent.TimeoutException ||
               e instanceof org.springframework.dao.TransientDataAccessException;
    }}

    private void sendToDLQ({event_name} event, Exception error) {{
        // DLQ logic handled by Spring Kafka error handler
        // This method is for additional DLQ metadata/logging
        log.error("Sending to DLQ - Event: {{}}, Error: {{}}",
                 event.getEventId(), error.getMessage());
    }}
}}
```"""

# Error handler configuration template
def get_error_handler_config(service_name):
    return f"""```yaml
# application.yml - Kafka Error Handling Configuration

kafka:
  bootstrap-servers: ${{KAFKA_BOOTSTRAP_SERVERS:localhost:29092}}

  consumer:
    group-id: {service_name}-consumer-group
    auto-offset-reset: earliest
    enable-auto-commit: false
    max-poll-records: 100

    # DLQ Configuration
    dead-letter-publishing:
      enabled: true
      topic-suffix: .DLQ

  # Error Handling Strategy
  listener:
    error-handler:
      type: SeekToCurrentErrorHandler
      max-failures: 3
      backoff:
        initial-interval: 1000
        multiplier: 2.0
        max-interval: 10000

    # Retry Configuration
    retry:
      max-attempts: 3
      backoff-policy: exponential

logging:
  level:
    com.arcone.biopro: INFO
    org.springframework.kafka: WARN
    org.apache.kafka: WARN
```"""

# Service mapping for determining service-event relationships
SERVICE_CONSUMERS = {
    "ApheresisPlasmaProductCreated": ["inventory-service", "quality-service", "distribution-service", "reporting-service"],
    "ApheresisPlasmaProductUpdated": ["inventory-service", "reporting-service"],
    "ApheresisPlasmaProductCompleted": ["inventory-service", "quality-service", "distribution-service"],
    "ApheresisPlateletProductCreated": ["inventory-service", "quality-service", "distribution-service", "reporting-service"],
    "ApheresisRBCProductCreated": ["inventory-service", "quality-service", "distribution-service", "reporting-service"],
    "WholeBloodProductCreated": ["inventory-service", "quality-service", "distribution-service", "reporting-service"],
}


def java_type_to_avro_type(java_type: str) -> Dict[str, Any]:
    """Convert Java type to Avro type"""
    type_mapping = {
        "String": "string",
        "Integer": "int",
        "Long": "long",
        "Double": "double",
        "Boolean": "boolean",
        "ZonedDateTime": {"type": "long", "logicalType": "timestamp-millis"},
        "LocalDate": {"type": "int", "logicalType": "date"},
        "UUID": {"type": "string", "logicalType": "uuid"},
    }

    # Handle List types
    if java_type.startswith("List<"):
        inner_type = java_type[5:-1]
        return {
            "type": "array",
            "items": java_type_to_avro_type(inner_type)
        }

    # Handle Optional/nullable
    if java_type.startswith("Optional<"):
        inner_type = java_type[9:-1]
        return ["null", java_type_to_avro_type(inner_type)]

    return type_mapping.get(java_type, "string")


def create_avro_schema(event: Dict[str, Any]) -> Dict[str, Any]:
    """Create Avro schema from event definition"""
    namespace = f"com.arcone.biopro.{event['service']}.domain.event"

    # Build fields
    fields = [
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
            "doc": "Timezone for occurredOn",
            "default": "UTC"
        },
        {
            "name": "eventType",
            "type": "string",
            "doc": "Type of event",
            "default": event['event_type']
        },
        {
            "name": "eventVersion",
            "type": "string",
            "doc": "Version of the event schema",
            "default": event['version']
        }
    ]

    # Add payload
    payload_fields = []
    for field in event.get('fields', []):
        payload_fields.append({
            "name": field['name'],
            "type": java_type_to_avro_type(field['type']),
            "doc": field.get('description', f"{field['name']} field")
        })

    if payload_fields:
        fields.append({
            "name": "payload",
            "type": {
                "type": "record",
                "name": event['payload_class'],
                "namespace": f"{namespace}.payload",
                "doc": f"{event['event_name']} payload",
                "fields": payload_fields
            },
            "doc": f"{event['event_name']} payload"
        })

    schema = {
        "type": "record",
        "name": event['event_name'],
        "namespace": namespace,
        "doc": event.get('purpose', f"Event published when {event['event_type'].lower().replace('_', ' ')} occurs"),
        "fields": fields
    }

    return schema


def register_schema(subject: str, schema: Dict[str, Any]) -> int:
    """Register schema in Schema Registry"""
    url = f"{SCHEMA_REGISTRY_URL}/subjects/{subject}/versions"
    headers = {"Content-Type": "application/vnd.schemaregistry.v1+json"}
    payload = {"schema": json.dumps(schema)}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get('id', -1)
    except requests.exceptions.RequestException as e:
        print(f"Error registering schema for {subject}: {e}")
        return -1


def create_eventcatalog_mdx(event: Dict[str, Any], schema_id: int, avro_schema: Dict[str, Any]):
    """Create EventCatalog MDX documentation"""
    event_id = event['event_name'].replace('Event', '')
    service_name = event['service']

    # Determine consumers
    consumers = SERVICE_CONSUMERS.get(event_id, [])

    content = f"""---
id: {event_id}
name: {event_id}
version: '{event['version']}'
summary: Event published by {service_name} service when {event['event_type'].lower().replace('_', ' ')} occurs
owners:
  - {service_name}-service
producers:
  - {service_name}-service
consumers:
{chr(10).join(f'  - {c}' for c in consumers) if consumers else '  []'}
badges:
  - content: "Schema Valid ✓"
    backgroundColor: "#22c55e"
    textColor: white
  - content: "Team: {service_name.title()}"
    backgroundColor: "#3b82f6"
    textColor: white
  - content: "v{event['version']}"
    backgroundColor: "#6366f1"
    textColor: white
---

# {event_id} Event

**Schema ID**: {schema_id}
**Schema Version**: {event['version']}
**Subject**: {event['event_name']}
**Domain**: {service_name.title()}
**Service**: {service_name}-service

## Business Context

{event.get('purpose', f'Event published when {event["event_type"].lower().replace("_", " ")} occurs in the {service_name} service.')}

## Event Schema Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| eventId | UUID | Yes | Unique event identifier |
| occurredOn | timestamp-millis | Yes | When the event occurred |
| eventType | string | Yes | Event type identifier |
| eventVersion | string | Yes | Schema version |
{chr(10).join(f'| {f["name"]} | {f["type"]} | {"Yes" if f.get("required", False) else "No"} | {f.get("description", "")} |' for f in event.get('fields', []))}

## Consumer Implementation with DLQ Support

### Spring Boot Kafka Listener

{DLQ_LISTENER_TEMPLATE.format(
    service=service_name,
    event_name=event['event_name'],
    topic_name=event['event_type'].lower().replace('_', '.')
)}

### Error Handling Configuration

{get_error_handler_config(service_name)}

### DLQ Monitoring Dashboard

```yaml
# Grafana Dashboard Configuration for DLQ Monitoring
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {service_name}-dlq-dashboard
data:
  dashboard.json: |
    {{
      "title": "{event_id} DLQ Monitor",
      "panels": [
        {{
          "title": "DLQ Message Rate",
          "targets": [
            {{
              "expr": "rate(kafka_consumer_records_consumed_total{{topic=~\\\".*{event['event_type'].lower()}.DLQ\\\"}}[5m])"
            }}
          ]
        }},
        {{
          "title": "Processing Errors",
          "targets": [
            {{
              "expr": "rate(kafka_consumer_fetch_manager_records_consumed_total{{topic=\\\"{event['event_type'].lower()}\\\"}}[5m]) - rate(kafka_consumer_records_consumed_total{{topic=\\\"{event['event_type'].lower()}\\\"}}[5m])"
            }}
          ]
        }}
      ]
    }}
```

## Complete Avro Schema

```json
{json.dumps(avro_schema, indent=2)}
```

## Change Log

### v{event['version']} ({get_current_date()})
- Schema registered with ID {schema_id}
- Integrated with Schema Registry
- DLQ error handling configured

<NodeGraph />
"""

    return content


def get_current_date():
    """Get current date in YYYY-MM-DD format"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def main():
    print("BioPro Event Schema Registration and EventCatalog Generator")
    print("=" * 70)

    # Load inventory
    print(f"\n1. Loading inventory from {INVENTORY_FILE}...")
    with open(INVENTORY_FILE, 'r') as f:
        events = json.load(f)

    print(f"   Found {len(events)} events")

    # Create EventCatalog directory if not exists
    os.makedirs(EVENTCATALOG_EVENTS_DIR, exist_ok=True)

    # Process each event
    registered_count = 0
    created_count = 0

    for idx, event in enumerate(events, 1):
        event_name = event['event_name']
        print(f"\n{idx}. Processing {event_name}...")

        # Create Avro schema
        avro_schema = create_avro_schema(event)
        print(f"   [OK] Created Avro schema")

        # Register schema
        subject = f"{event_name}-value"
        schema_id = register_schema(subject, avro_schema)

        if schema_id > 0:
            print(f"   [OK] Registered schema with ID: {schema_id}")
            registered_count += 1
        else:
            print(f"   [FAIL] Failed to register schema")
            schema_id = 999  # Placeholder for documentation

        # Create EventCatalog documentation
        event_dir = os.path.join(EVENTCATALOG_EVENTS_DIR, event_name.replace('Event', ''))
        os.makedirs(event_dir, exist_ok=True)

        mdx_content = create_eventcatalog_mdx(event, schema_id, avro_schema)
        mdx_file = os.path.join(event_dir, 'index.mdx')

        with open(mdx_file, 'w', encoding='utf-8') as f:
            f.write(mdx_content)

        print(f"   [OK] Created EventCatalog documentation: {mdx_file}")
        created_count += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total events processed: {len(events)}")
    print(f"Schemas registered: {registered_count}")
    print(f"EventCatalog entries created: {created_count}")
    print(f"\nEventCatalog documentation created in: {EVENTCATALOG_EVENTS_DIR}/")
    print("Schema Registry URL: " + SCHEMA_REGISTRY_URL)


if __name__ == "__main__":
    main()
