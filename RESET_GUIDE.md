# How to Clear Previous Validations

This guide shows you how to reset all validation state and start fresh.

---

## Quick Reset (Automated Script)

```bash
# Run the automated reset script
chmod +x reset_validation_state.sh
./reset_validation_state.sh
```

The script will:
1. Delete the schema from Schema Registry
2. Delete and recreate Kafka topics
3. Restart orders-service to reset metrics
4. Optionally restart Prometheus

---

## Manual Reset Commands

### 1. Clear Schema Registry

```bash
# Soft delete the schema (can be recovered)
docker exec biopro-schema-registry curl -X DELETE \
  http://localhost:8081/subjects/OrderCreatedEvent

# Hard delete (permanent - required to register incompatible schema)
docker exec biopro-schema-registry curl -X DELETE \
  "http://localhost:8081/subjects/OrderCreatedEvent?permanent=true"

# Verify schema is deleted
docker exec biopro-schema-registry curl http://localhost:8081/subjects
```

**Why?** Schema Registry enforces compatibility by default. If you want to register a new incompatible schema version, you must delete the old one first.

### 2. Clear Kafka Topics

#### Delete Orders Events Topic

```bash
# Delete topic
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic biopro.orders.events

# Recreate topic
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic biopro.orders.events \
  --partitions 3 \
  --replication-factor 1
```

#### Delete DLQ Topic

```bash
# Delete topic
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic biopro.orders.dlq

# Recreate topic
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic biopro.orders.dlq \
  --partitions 1 \
  --replication-factor 1
```

#### Verify Topics

```bash
# List topics
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list

# Check topic offsets (should be 0)
docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.events

docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.dlq
```

### 3. Reset Application Metrics

```bash
# Restart orders-service to reset in-memory metrics
docker-compose restart orders-service

# Wait for service to start
sleep 10

# Verify service is healthy
docker exec biopro-schema-registry curl http://orders-service:8080/actuator/health
```

### 4. Clear Prometheus Data (Optional)

#### Option A: Restart Prometheus (clears in-memory data)

```bash
docker-compose restart prometheus
```

#### Option B: Delete Prometheus Volume (full reset)

```bash
# Stop Prometheus
docker-compose stop prometheus

# Remove volume
docker volume rm poc_prometheus-data

# Start Prometheus (creates new volume)
docker-compose up -d prometheus
```

### 5. Clear Grafana Dashboards (Optional)

```bash
# Restart Grafana to refresh data
docker-compose restart grafana

# Or remove Grafana volume to reset all dashboards
docker-compose stop grafana
docker volume rm poc_grafana-data
docker-compose up -d grafana
```

---

## Common Scenarios

### Scenario 1: Schema Compatibility Error

**Problem:**
```
{"error_code":409,"message":"Schema being registered is incompatible with an earlier schema"}
```

**Solution:**
```bash
# Delete schema permanently
docker exec biopro-schema-registry curl -X DELETE \
  "http://localhost:8081/subjects/OrderCreatedEvent?permanent=true"

# Now you can register the new incompatible schema
```

### Scenario 2: Too Many Test Events in Kafka

**Problem:** Kafka topics have thousands of test messages making it hard to see new events.

**Solution:**
```bash
# Delete and recreate topics
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic biopro.orders.events

docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic biopro.orders.dlq

# Recreate (see commands above)
```

### Scenario 3: Metrics Not Resetting

**Problem:** Old validation counts still showing in Prometheus.

**Solution:**
```bash
# Restart orders-service to reset counters
docker-compose restart orders-service

# Or restart Prometheus to clear time-series data
docker-compose restart prometheus
```

### Scenario 4: Start Completely Fresh

**Problem:** Want to reset everything to a clean slate.

**Solution:**
```bash
# Stop all services
docker-compose down

# Remove all volumes (WARNING: deletes all data!)
docker volume rm poc_kafka-data poc_zookeeper-data poc_prometheus-data poc_grafana-data

# Start services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Register schema again (see VALIDATION_WORKFLOW_GUIDE.md)
```

---

## Verification Commands

### Check What's Currently Stored

```bash
# List schemas
docker exec biopro-schema-registry curl http://localhost:8081/subjects

# List topics
docker exec biopro-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Count messages in orders events topic
docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.events | awk -F ":" '{sum += $3} END {print "Total messages:", sum}'

# Count messages in DLQ topic
docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.dlq | awk -F ":" '{sum += $3} END {print "Total DLQ messages:", sum}'

# Check current metrics
curl -s http://localhost:8080/actuator/prometheus | grep biopro_schema_validation_total
```

---

## Quick Commands Cheat Sheet

```bash
# Delete schema permanently
docker exec biopro-schema-registry curl -X DELETE "http://localhost:8081/subjects/OrderCreatedEvent?permanent=true"

# Delete orders events topic
docker exec biopro-kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic biopro.orders.events

# Delete DLQ topic
docker exec biopro-kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic biopro.orders.dlq

# Recreate orders events topic
docker exec biopro-kafka kafka-topics --bootstrap-server localhost:9092 --create --topic biopro.orders.events --partitions 3 --replication-factor 1

# Recreate DLQ topic
docker exec biopro-kafka kafka-topics --bootstrap-server localhost:9092 --create --topic biopro.orders.dlq --partitions 1 --replication-factor 1

# Restart services
docker-compose restart orders-service prometheus grafana

# Full reset (nuclear option - deletes everything!)
docker-compose down && docker volume prune -f && docker-compose up -d
```

---

## Windows-Specific Notes

If running from Windows Command Prompt or PowerShell, use:

```batch
REM Instead of ./reset_validation_state.sh, use:
bash reset_validation_state.sh

REM Or convert line endings first:
dos2unix reset_validation_state.sh
./reset_validation_state.sh
```

---

## After Reset

Once you've reset everything:

1. **Register Schema** - Follow Step 1 in `VALIDATION_WORKFLOW_GUIDE.md`
2. **Test Valid Event** - Send a proper event to verify setup
3. **Test Invalid Event** - Verify DLQ routing works
4. **Check Prometheus** - Confirm metrics are collecting

---

## Troubleshooting

### Script Won't Run

```bash
# Make executable
chmod +x reset_validation_state.sh

# Fix line endings (if needed)
dos2unix reset_validation_state.sh
```

### Schema Still Exists After Delete

```bash
# Use permanent delete flag
docker exec biopro-schema-registry curl -X DELETE \
  "http://localhost:8081/subjects/OrderCreatedEvent?permanent=true"

# Verify deletion
docker exec biopro-schema-registry curl http://localhost:8081/subjects
```

### Topic Delete Fails

```bash
# Check if topic actually exists
docker exec biopro-kafka kafka-topics --bootstrap-server localhost:9092 --list

# If stuck, restart Kafka
docker-compose restart kafka

# Wait and try again
sleep 10
docker exec biopro-kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic biopro.orders.events
```

### Services Won't Restart

```bash
# Check container status
docker-compose ps

# View logs for errors
docker-compose logs orders-service --tail=50

# Full restart
docker-compose restart
```

---

## Summary

- Use **`reset_validation_state.sh`** for automated full reset
- Delete **Schema Registry** entries to fix compatibility errors
- Delete **Kafka topics** to clear old events
- Restart **orders-service** to reset metrics
- Restart **Prometheus** to clear time-series data
- Use **`docker-compose down`** + volume removal for complete reset

For detailed validation testing, see `VALIDATION_WORKFLOW_GUIDE.md`.
