#!/bin/bash

# BioPro Event Governance - Reset Validation State
# Clears all previous validation events and metrics

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Reset Validation State                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}⚠ This will delete all events and reset metrics!${NC}"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi
echo ""

# 1. Delete schema from Schema Registry
echo -e "${BLUE}Step 1: Clearing Schema Registry...${NC}"

echo "Deleting OrderCreatedEvent schema..."
docker exec biopro-schema-registry curl -X DELETE \
  http://localhost:8081/subjects/OrderCreatedEvent 2>/dev/null || echo "Schema doesn't exist or already deleted"

# Permanently delete (hard delete)
echo "Permanently deleting schema..."
docker exec biopro-schema-registry curl -X DELETE \
  "http://localhost:8081/subjects/OrderCreatedEvent?permanent=true" 2>/dev/null || echo "Already permanently deleted"

echo -e "${GREEN}✓ Schema Registry cleared${NC}"
echo ""

# 2. Delete and recreate Kafka topics
echo -e "${BLUE}Step 2: Resetting Kafka topics...${NC}"

# Delete orders events topic
echo "Deleting biopro.orders.events topic..."
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic biopro.orders.events 2>/dev/null || echo "Topic doesn't exist or already deleted"

# Delete DLQ topic
echo "Deleting biopro.orders.dlq topic..."
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic biopro.orders.dlq 2>/dev/null || echo "Topic doesn't exist or already deleted"

# Wait for deletion
echo "Waiting for topics to be deleted..."
sleep 3

# Recreate orders events topic
echo "Creating biopro.orders.events topic..."
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic biopro.orders.events \
  --partitions 3 \
  --replication-factor 1

# Recreate DLQ topic
echo "Creating biopro.orders.dlq topic..."
docker exec biopro-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic biopro.orders.dlq \
  --partitions 1 \
  --replication-factor 1

echo -e "${GREEN}✓ Kafka topics reset${NC}"
echo ""

# 3. Restart orders-service to reset in-memory metrics
echo -e "${BLUE}Step 3: Restarting orders-service to reset metrics...${NC}"
docker-compose restart orders-service

echo "Waiting for orders-service to start..."
sleep 10

# Check if service is up
HEALTH_CHECK=$(docker exec biopro-schema-registry curl -s http://orders-service:8080/actuator/health | grep -o "UP" || echo "DOWN")
if [ "$HEALTH_CHECK" == "UP" ]; then
    echo -e "${GREEN}✓ Orders-service restarted successfully${NC}"
else
    echo -e "${YELLOW}⚠ Orders-service may still be starting...${NC}"
fi
echo ""

# 4. Optional: Clear Prometheus data (if you want to reset time-series data)
echo -e "${BLUE}Step 4: Prometheus data${NC}"
read -p "Do you want to clear Prometheus time-series data? (yes/no): " CLEAR_PROM

if [ "$CLEAR_PROM" == "yes" ]; then
    echo "Restarting Prometheus (this will clear in-memory data)..."
    docker-compose restart prometheus
    echo -e "${GREEN}✓ Prometheus restarted${NC}"
    echo -e "${YELLOW}Note: Persistent data still exists in Prometheus volume${NC}"
    echo "To fully clear Prometheus data, run: docker volume rm poc_prometheus-data"
else
    echo "Keeping Prometheus data"
fi
echo ""

# 5. Verify reset
echo -e "${BLUE}Step 5: Verifying reset...${NC}"

# Check topic offsets
ORDERS_OFFSET=$(docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.events 2>/dev/null | awk -F ":" '{sum += $3} END {print sum}')
echo "Orders events topic messages: $ORDERS_OFFSET"

DLQ_OFFSET=$(docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.dlq 2>/dev/null | awk -F ":" '{sum += $3} END {print sum}')
echo "DLQ topic messages: $DLQ_OFFSET"

echo ""

# 5. Summary
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Reset Complete!                                           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "What was reset:"
echo "  ✓ Schema Registry cleared (OrderCreatedEvent schema deleted)"
echo "  ✓ Kafka topics deleted and recreated (all events cleared)"
echo "  ✓ Orders-service restarted (in-memory metrics reset)"
if [ "$CLEAR_PROM" == "yes" ]; then
    echo "  ✓ Prometheus restarted"
fi
echo ""
echo "You can now start fresh with new validation tests!"
