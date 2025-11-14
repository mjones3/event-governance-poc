#!/bin/bash

# BioPro Event Governance Framework - Demo Test Script
# This script demonstrates the POC functionality

set -e

echo "========================================"
echo "BioPro Event Governance Framework Demo"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ORDERS_SERVICE_URL="http://localhost:8080"
KAFKA_UI_URL="http://localhost:8090"
SCHEMA_REGISTRY_URL="http://localhost:8081"

# Function to check if service is ready
check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1

    echo -e "${YELLOW}Checking if $name is ready...${NC}"

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is ready!${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "${RED}✗ $name failed to start${NC}"
    return 1
}

# Step 1: Check infrastructure
echo "Step 1: Checking infrastructure..."
echo "-----------------------------------"
check_service "$SCHEMA_REGISTRY_URL" "Schema Registry"
check_service "$KAFKA_UI_URL" "Kafka UI"
echo ""

# Step 2: Check Orders service
echo "Step 2: Checking Orders service..."
echo "-----------------------------------"
if check_service "$ORDERS_SERVICE_URL/actuator/health" "Orders Service"; then
    echo ""
else
    echo -e "${YELLOW}Orders service not running. Start it with: cd biopro-demo-orders && mvn spring-boot:run${NC}"
    echo ""
fi

# Step 3: Publish valid order event
echo "Step 3: Publishing VALID order event..."
echo "-----------------------------------"
RESPONSE=$(curl -s -X POST "$ORDERS_SERVICE_URL/api/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-VALID-001",
    "bloodType": "O_POSITIVE",
    "quantity": 2,
    "priority": "URGENT",
    "facilityId": "FAC-001",
    "requestedBy": "DR-SMITH"
  }')

if echo "$RESPONSE" | grep -q "success.*true"; then
    echo -e "${GREEN}✓ Valid order event published successfully${NC}"
    echo "Response: $RESPONSE"
else
    echo -e "${RED}✗ Failed to publish order event${NC}"
    echo "Response: $RESPONSE"
fi
echo ""

# Step 4: Publish emergency order
echo "Step 4: Publishing EMERGENCY order event..."
echo "-----------------------------------"
RESPONSE=$(curl -s -X POST "$ORDERS_SERVICE_URL/api/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-EMERGENCY-002",
    "bloodType": "AB_NEGATIVE",
    "quantity": 5,
    "priority": "LIFE_THREATENING",
    "facilityId": "FAC-002",
    "requestedBy": "DR-JONES"
  }')

if echo "$RESPONSE" | grep -q "success.*true"; then
    echo -e "${GREEN}✓ Emergency order event published successfully${NC}"
    echo "Response: $RESPONSE"
else
    echo -e "${RED}✗ Failed to publish order event${NC}"
    echo "Response: $RESPONSE"
fi
echo ""

# Step 5: Check metrics
echo "Step 5: Checking metrics..."
echo "-----------------------------------"
METRICS=$(curl -s "$ORDERS_SERVICE_URL/actuator/metrics")
if echo "$METRICS" | grep -q "biopro"; then
    echo -e "${GREEN}✓ BioPro metrics are being collected${NC}"
    echo ""
    echo "Available metrics:"
    echo "$METRICS" | grep -o '"name":"biopro[^"]*"' | head -5
else
    echo -e "${YELLOW}⚠ BioPro metrics not yet available${NC}"
fi
echo ""

# Step 6: Check Prometheus metrics
echo "Step 6: Checking Prometheus metrics..."
echo "-----------------------------------"
PROM_METRICS=$(curl -s "$ORDERS_SERVICE_URL/actuator/prometheus" | grep "^biopro_" | head -10)
if [ -n "$PROM_METRICS" ]; then
    echo -e "${GREEN}✓ Prometheus metrics available${NC}"
    echo "Sample metrics:"
    echo "$PROM_METRICS"
else
    echo -e "${YELLOW}⚠ Prometheus metrics not yet available${NC}"
fi
echo ""

# Summary
echo "========================================"
echo "Demo Test Summary"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. View events in Kafka UI: $KAFKA_UI_URL"
echo "2. Check main events topic: biopro.orders.events"
echo "3. Check DLQ topic: biopro.orders.dlq"
echo "4. View metrics: $ORDERS_SERVICE_URL/actuator/metrics"
echo "5. View Prometheus metrics: $ORDERS_SERVICE_URL/actuator/prometheus"
echo ""
echo -e "${GREEN}✓ Demo completed successfully!${NC}"
echo ""
