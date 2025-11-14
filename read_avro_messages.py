#!/usr/bin/env python3
"""
Simple script to read Avro messages from Kafka topic
"""

from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import json

# Configuration
KAFKA_BROKER = 'localhost:9092'
SCHEMA_REGISTRY = 'http://localhost:8081'
TOPIC = 'biopro.orders.events'

def main():
    # Schema Registry client
    schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY})

    # Get schema
    try:
        schema_str = schema_registry_client.get_latest_version('OrderCreatedEvent').schema.schema_str
        avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)
    except Exception as e:
        print(f"Error getting schema: {e}")
        return

    # Kafka consumer
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'avro-reader-group',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe([TOPIC])

    print(f"Reading messages from topic: {TOPIC}")
    print("=" * 80)

    message_count = 0
    try:
        while True:
            msg = consumer.poll(timeout=2.0)
            if msg is None:
                break
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Deserialize Avro message
            try:
                ctx = SerializationContext(TOPIC, MessageField.VALUE)
                value = avro_deserializer(msg.value(), ctx)
                message_count += 1

                print(f"\nMessage #{message_count}:")
                print(f"  Event ID: {value.get('eventId')}")
                print(f"  Event Type: {value.get('eventType')}")
                print(f"  Occurred On: {value.get('occurredOn')}")

                payload = value.get('payload', {})
                print(f"  Order ID: {payload.get('externalId')}")
                print(f"  Status: {payload.get('orderStatus')}")
                print(f"  Location: {payload.get('locationCode')}")
                print(f"  Priority: {payload.get('priority')}")

                order_items = payload.get('orderItems', [])
                if order_items:
                    for idx, item in enumerate(order_items):
                        print(f"  Item {idx + 1}:")
                        print(f"    Blood Type: {item.get('bloodType')}")
                        print(f"    Quantity: {item.get('quantity')}")

            except Exception as e:
                print(f"Error deserializing message: {e}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

    print("\n" + "=" * 80)
    print(f"Total messages read: {message_count}")

if __name__ == "__main__":
    main()
