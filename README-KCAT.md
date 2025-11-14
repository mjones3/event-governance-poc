# kcat - Kafka CLI Tool Guide

kcat successfully bypasses Netskope and connects to your Kafka cluster!

## Quick Reference Commands

### 1. List All Topics and Brokers
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -L
```

### 2. List Just Topics
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -L | grep "topic \""
```

### 3. Consume Messages from a Topic (from beginning)
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -C -t biopro.orders.dlq -o beginning
```

### 4. Consume Last 10 Messages
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -C -t biopro.orders.dlq -o -10
```

### 5. Consume with Detailed Formatting
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -C -t biopro.orders.dlq -f 'Topic: %t\nPartition: %p\nOffset: %o\nTimestamp: %T\nKey: %k\nValue: %s\n---\n'
```

### 6. Produce a Message to a Topic
```bash
echo '{"orderId": "123", "status": "created"}' | docker run -i --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -P -t biopro.orders.dlq
```

### 7. Produce Message with Key
```bash
echo 'order-123:{"orderId": "123", "status": "created"}' | docker run -i --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -P -t biopro.orders.dlq -K:
```

### 8. Get Topic Details
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -L -t biopro.orders.dlq
```

### 9. Query Topic Offsets (watermarks)
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -Q -t biopro.orders.dlq:0:-1
```

### 10. Consume with JSON Envelope
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -C -t biopro.orders.dlq -J
```

### 11. Monitor in Real-Time (tail -f style)
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -C -t biopro.orders.dlq -o end
```

### 12. Consume and Exit After N Messages
```bash
docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092 -C -t biopro.orders.dlq -c 5 -o beginning
```

## Tips

- **Replace topic name**: Change `biopro.orders.dlq` to any topic you want to query
- **Offset options**:
  - `beginning` - from start
  - `end` - only new messages
  - `-10` - last 10 messages
  - `100` - from offset 100
- **Exit consumer**: Press `Ctrl+C`
- **Create alias** (optional):
  ```bash
  alias kcat='docker run --rm --network poc_biopro-network edenhill/kcat:1.7.1 -b kafka:29092'
  # Then use: kcat -L
  ```

## Current Topics in Your Cluster

- `biopro.orders.dlq` - Dead Letter Queue for failed orders
- `_schemas` - Schema Registry metadata
- `__consumer_offsets` - Kafka consumer group offsets
