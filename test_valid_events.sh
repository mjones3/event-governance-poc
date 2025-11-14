#!/bin/bash

# Test Valid Events - Different Scenarios
# This script sends various valid events to test the system

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Testing Valid Events                                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Urgent Blood Order
echo -e "${BLUE}Test 1: Urgent O+ Blood Order${NC}"
RESPONSE1=$(docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-URGENT-001",
    "facilityId": "FAC-ER-01",
    "bloodType": "O+",
    "quantity": 4,
    "priority": "URGENT",
    "requestedBy": "Dr. Sarah Johnson"
  }')

if echo "$RESPONSE1" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Success${NC}"
    echo "$RESPONSE1" | jq .
else
    echo "Response: $RESPONSE1"
fi
echo ""
sleep 1

# Test 2: Routine AB- Blood Order
echo -e "${BLUE}Test 2: Routine AB- Blood Order${NC}"
RESPONSE2=$(docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-ROUTINE-001",
    "facilityId": "FAC-MAIN-01",
    "bloodType": "AB-",
    "quantity": 2,
    "priority": "ROUTINE",
    "requestedBy": "Dr. Michael Chen"
  }')

if echo "$RESPONSE2" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Success${NC}"
    echo "$RESPONSE2" | jq .
else
    echo "Response: $RESPONSE2"
fi
echo ""
sleep 1

# Test 3: Life-Threatening A+ Order
echo -e "${BLUE}Test 3: Life-Threatening A+ Blood Order${NC}"
RESPONSE3=$(docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-CRITICAL-001",
    "facilityId": "FAC-ICU-01",
    "bloodType": "A+",
    "quantity": 6,
    "priority": "LIFE_THREATENING",
    "requestedBy": "Dr. Lisa Martinez"
  }')

if echo "$RESPONSE3" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Success${NC}"
    echo "$RESPONSE3" | jq .
else
    echo "Response: $RESPONSE3"
fi
echo ""
sleep 1

# Test 4: B- Blood Order (Rare Type)
echo -e "${BLUE}Test 4: B- Blood Order (Rare Type)${NC}"
RESPONSE4=$(docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-RARE-001",
    "facilityId": "FAC-SURGERY-01",
    "bloodType": "B-",
    "quantity": 1,
    "priority": "URGENT",
    "requestedBy": "Dr. James Wilson"
  }')

if echo "$RESPONSE4" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Success${NC}"
    echo "$RESPONSE4" | jq .
else
    echo "Response: $RESPONSE4"
fi
echo ""
sleep 2

# Check results
echo -e "${BLUE}Checking Results...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count successful events
SUCCESS_COUNT=$(docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.events 2>/dev/null | awk -F ":" '{sum += $3} END {print sum}' || echo "0")
echo "Total events in biopro.orders.events: $SUCCESS_COUNT"

# Count DLQ events (should be 0 for valid events)
DLQ_COUNT=$(docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.dlq 2>/dev/null | awk -F ":" '{sum += $3} END {print sum}' || echo "0")
echo "Total events in biopro.orders.dlq: $DLQ_COUNT"

# Check recent logs
echo ""
echo -e "${BLUE}Recent Logs:${NC}"
docker-compose logs --tail=10 orders-service | grep -E "(Successfully published|validation failed)" || echo "No recent logs found"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Test Complete!                                            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
