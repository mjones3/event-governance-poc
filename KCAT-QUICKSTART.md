# kcat Quick Start Guide

kcat is now automatically started when you run `docker-compose up -d`!

## 🚀 Quick Commands

### Using the kafka-monitor helper script (Easiest):

```bash
# Show broker information
./kafka-monitor.sh brokers

# List all topics
./kafka-monitor.sh topics

# View last 10 DLQ messages
./kafka-monitor.sh dlq

# Monitor DLQ in real-time (Ctrl+C to stop)
./kafka-monitor.sh dlq-tail

# Consume from any topic
./kafka-monitor.sh consume biopro.orders.dlq

# Show full cluster metadata
./kafka-monitor.sh metadata
```

### Using the kcat wrapper directly:

```bash
# List brokers and topics
./kcat.sh -L

# Consume from beginning
./kcat.sh -C -t biopro.orders.dlq -o beginning

# Consume last 10 messages
./kcat.sh -C -t biopro.orders.dlq -o -10

# Produce a message
echo '{"test": "data"}' | ./kcat.sh -P -t biopro.orders.dlq
```

### Using docker exec directly:

```bash
# Any kcat command
docker exec biopro-kcat kcat -b kafka:29092 -L
```

## 📋 Available Topics

- `biopro.orders.dlq` - Dead Letter Queue for failed orders
- `_schemas` - Schema Registry metadata
- `__consumer_offsets` - Kafka internal consumer offsets

## 🔄 Docker Compose Integration

kcat starts automatically with all other services:

```bash
# Start everything (including kcat)
docker-compose up -d

# Stop everything
docker-compose down

# View kcat logs
docker logs biopro-kcat

# Check kcat status
docker ps | grep kcat
```

## 💡 Common Use Cases

### Monitor DLQ for Errors
```bash
./kafka-monitor.sh dlq-tail
```

### Check Broker Health
```bash
./kafka-monitor.sh brokers
```

### Consume and Format Messages
```bash
./kcat.sh -C -t biopro.orders.dlq -f 'Offset: %o\nTime: %T\nKey: %k\nValue: %s\n---\n'
```

### Produce Test Message
```bash
echo '{"orderId": "test-123", "status": "pending"}' | ./kcat.sh -P -t biopro.orders.dlq
```

## 📖 Full kcat Documentation

For complete kcat options, run:
```bash
docker exec biopro-kcat kcat -h
```

Or see: https://github.com/edenhill/kcat

## 🎯 Why kcat Works (and Kafka UI doesn't)

- ✅ **kcat**: Uses standard Kafka consumer/producer protocols - bypasses Netskope
- ❌ **Kafka UI**: Uses Kafka AdminClient protocol - blocked by Netskope

All your application services (orders, manufacturing, collections) work perfectly because they use the same protocols as kcat!
