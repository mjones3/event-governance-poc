#!/bin/bash

# BioPro Event Governance - Complete Workflow Test Script
# This script demonstrates the end-to-end validation workflow

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     BioPro Event Governance Test Workflow                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Check Schema Registration
echo -e "${BLUE}Step 1: Verifying schema registration...${NC}"
SCHEMA_CHECK=$(docker exec biopro-schema-registry curl -s http://localhost:8081/subjects/OrderCreatedEvent/versions/1)
if echo "$SCHEMA_CHECK" | grep -q "id"; then
    echo -e "${GREEN}✓ Schema registered successfully${NC}"
    echo "$SCHEMA_CHECK" | jq .
else
    echo -e "${RED}✗ Schema not found${NC}"
    exit 1
fi
echo ""

# 2. Send Valid Event
echo -e "${BLUE}Step 2: Sending valid event...${NC}"
VALID_RESPONSE=$(docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "TEST-VALID-001",
    "facilityId": "FAC-001",
    "bloodType": "AB+",
    "quantity": 2,
    "priority": "ROUTINE",
    "requestedBy": "Test User"
  }')

if echo "$VALID_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ Valid event accepted${NC}"
    echo "$VALID_RESPONSE" | jq .
else
    echo -e "${RED}✗ Valid event rejected${NC}"
    echo "$VALID_RESPONSE"
fi
echo ""

# 3. Send Invalid Event
echo -e "${BLUE}Step 3: Sending invalid event (missing required fields)...${NC}"
INVALID_RESPONSE=$(docker exec biopro-schema-registry curl -s -X POST http://orders-service:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "wrongField": "wrong value",
    "anotherWrong": "also wrong"
  }')

if echo "$INVALID_RESPONSE" | grep -q '"success":true'; then
    echo -e "${YELLOW}⚠ Invalid event accepted (will be routed to DLQ)${NC}"
    echo "$INVALID_RESPONSE" | jq .
else
    echo -e "${RED}✗ Unexpected response${NC}"
    echo "$INVALID_RESPONSE"
fi
echo ""

# 4. Wait for processing
echo -e "${BLUE}Step 4: Waiting 3 seconds for event processing...${NC}"
sleep 3
echo ""

# 5. Check validation logs
echo -e "${BLUE}Step 5: Checking validation logs...${NC}"
VALIDATION_LOGS=$(docker-compose logs --tail=20 orders-service 2>&1 | grep -E "(validation|Successfully published)" || echo "No validation logs found")
if echo "$VALIDATION_LOGS" | grep -q "validation failed"; then
    echo -e "${GREEN}✓ Validation failure detected in logs${NC}"
    echo "$VALIDATION_LOGS" | grep "validation failed"
else
    echo -e "${YELLOW}⚠ No validation failures in recent logs${NC}"
fi

if echo "$VALIDATION_LOGS" | grep -q "Successfully published"; then
    echo -e "${GREEN}✓ Successful publication detected in logs${NC}"
    echo "$VALIDATION_LOGS" | grep "Successfully published" | head -1
fi
echo ""

# 6. Check DLQ
echo -e "${BLUE}Step 6: Checking DLQ for failed events...${NC}"
DLQ_EVENT=$(docker exec biopro-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic biopro.orders.dlq \
  --from-beginning \
  --max-messages 1 \
  --timeout-ms 5000 2>/dev/null || echo '{"error": "No DLQ events found"}')

if echo "$DLQ_EVENT" | grep -q "dlqEventId"; then
    echo -e "${GREEN}✓ DLQ event found${NC}"
    echo "$DLQ_EVENT" | jq '{
      dlqEventId: .dlqEventId,
      originalEventId: .originalEventId,
      errorMessage: .errorMessage,
      priority: .priority,
      status: .status
    }'
else
    echo -e "${YELLOW}⚠ No DLQ events found yet${NC}"
fi
echo ""

# 7. Check Prometheus metrics
echo -e "${BLUE}Step 7: Checking Prometheus metrics...${NC}"
METRICS=$(curl -s http://localhost:8080/actuator/prometheus | grep "biopro_schema_validation_total" || echo "No metrics found")
if echo "$METRICS" | grep -q "biopro_schema_validation_total"; then
    echo -e "${GREEN}✓ Validation metrics found${NC}"
    echo "$METRICS" | head -5
else
    echo -e "${RED}✗ No validation metrics available${NC}"
fi
echo ""

# 8. Summary Statistics
echo -e "${BLUE}Step 8: Summary Statistics${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count DLQ messages
DLQ_COUNT=$(docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.dlq 2>/dev/null | awk -F ":" '{sum += $3} END {print sum}' || echo "0")
echo "Total DLQ Events: $DLQ_COUNT"

# Count successful events
SUCCESS_COUNT=$(docker exec biopro-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic biopro.orders.events 2>/dev/null | awk -F ":" '{sum += $3} END {print sum}' || echo "0")
echo "Total Successful Events: $SUCCESS_COUNT"

# Extract metrics counts
if echo "$METRICS" | grep -q "result=\"success\""; then
    SUCCESS_VALIDATIONS=$(echo "$METRICS" | grep 'result="success"' | grep -v "#" | awk '{print $2}')
    echo "Schema Validations (Success): $SUCCESS_VALIDATIONS"
fi

if echo "$METRICS" | grep -q "result=\"failure\""; then
    FAILED_VALIDATIONS=$(echo "$METRICS" | grep 'result="failure"' | grep -v "#" | awk '{print $2}')
    echo "Schema Validations (Failure): $FAILED_VALIDATIONS"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 9. Access Information
echo -e "${BLUE}Step 9: Access Information${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Prometheus UI:      http://localhost:9090"
echo "Grafana UI:         http://localhost:3000 (admin/admin)"
echo "Schema Registry:    http://localhost:8081"
echo "Metrics Endpoint:   http://localhost:8080/actuator/prometheus"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Test Workflow Complete!                                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Next Steps:"
echo "1. Open Prometheus (http://localhost:9090) and run queries from the guide"
echo "2. Open Grafana (http://localhost:3000) and create dashboards"
echo "3. Check the DLQ topic for failed events"
echo "4. Review the VALIDATION_WORKFLOW_GUIDE.md for detailed information"
