#!/bin/bash
# Test the Kafka fix applied by the agent

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Testing Kafka Fix - Confluent Metrics Reporter Removed       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Find project directory
if [ -d "/mnt/c/Users/MelvinJones/work/event-governance/poc" ]; then
    cd "/mnt/c/Users/MelvinJones/work/event-governance/poc"
else
    cd "$(dirname "$0")"
fi

echo -e "${BLUE}📍 Working directory: $(pwd)${NC}"
echo ""

echo -e "${YELLOW}STEP 1: Stopping existing containers...${NC}"
docker-compose down
echo ""

echo -e "${YELLOW}STEP 2: Starting Zookeeper...${NC}"
docker-compose up -d zookeeper
echo "Waiting 15 seconds for Zookeeper to be ready..."
sleep 15

echo ""
echo -e "${BLUE}Checking Zookeeper status:${NC}"
docker logs biopro-zookeeper 2>&1 | tail -10

if docker logs biopro-zookeeper 2>&1 | grep -q "binding to port"; then
    echo -e "${GREEN}✅ Zookeeper is running${NC}"
else
    echo -e "${RED}❌ Zookeeper failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}STEP 3: Starting Kafka (with fix applied)...${NC}"
docker-compose up -d kafka
echo "Waiting 30 seconds for Kafka to start..."
sleep 30

echo ""
echo -e "${BLUE}Checking Kafka status:${NC}"
docker-compose ps kafka

echo ""
echo -e "${BLUE}Last 30 lines of Kafka logs:${NC}"
docker logs biopro-kafka 2>&1 | tail -30

echo ""
echo -e "${BLUE}Checking for success indicators:${NC}"

# Check for Kafka started message
if docker logs biopro-kafka 2>&1 | grep -q "Kafka Server started"; then
    echo -e "${GREEN}✅ SUCCESS: Found 'Kafka Server started' message${NC}"
    SUCCESS=true
elif docker logs biopro-kafka 2>&1 | grep -q "started (kafka.server.KafkaServer)"; then
    echo -e "${GREEN}✅ SUCCESS: Found Kafka server startup message${NC}"
    SUCCESS=true
else
    echo -e "${YELLOW}⚠️  Kafka startup message not found yet (may still be starting)${NC}"
    SUCCESS=false
fi

echo ""
echo -e "${BLUE}Checking for errors:${NC}"

# Check for the ClassNotFoundException error that we fixed
if docker logs biopro-kafka 2>&1 | grep -q "ClassNotFoundException.*ConfluentMetricsReporter"; then
    echo -e "${RED}❌ FAILED: Still seeing ConfluentMetricsReporter error${NC}"
    echo -e "${RED}   The fix may not have been applied correctly${NC}"
    SUCCESS=false
else
    echo -e "${GREEN}✅ No ConfluentMetricsReporter errors (fix is working!)${NC}"
fi

# Check for other fatal errors
if docker logs biopro-kafka 2>&1 | grep -q "FATAL"; then
    echo -e "${RED}❌ Found FATAL errors:${NC}"
    docker logs biopro-kafka 2>&1 | grep FATAL
    SUCCESS=false
else
    echo -e "${GREEN}✅ No FATAL errors${NC}"
fi

echo ""
if [ "$SUCCESS" = true ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              KAFKA IS NOW RUNNING SUCCESSFULLY! 🎉             ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "${YELLOW}STEP 4: Starting Schema Registry...${NC}"
    docker-compose up -d schema-registry
    echo "Waiting 20 seconds for Schema Registry..."
    sleep 20

    echo ""
    echo -e "${BLUE}Schema Registry logs:${NC}"
    docker logs biopro-schema-registry 2>&1 | tail -20

    if docker logs biopro-schema-registry 2>&1 | grep -q "Server started"; then
        echo -e "${GREEN}✅ Schema Registry started successfully!${NC}"
    else
        echo -e "${YELLOW}⚠️  Schema Registry may still be starting...${NC}"
    fi

    echo ""
    echo -e "${YELLOW}STEP 5: Starting remaining services...${NC}"
    docker-compose up -d

    echo ""
    echo -e "${GREEN}✅ All services started!${NC}"
    echo ""
    echo -e "${BLUE}Final status:${NC}"
    docker-compose ps

    echo ""
    echo -e "${BLUE}🎯 Next steps:${NC}"
    echo "1. Wait 2-3 minutes for all services to be ready"
    echo "2. Test services:"
    echo "   curl http://localhost:8080/actuator/health  # Orders"
    echo "   curl http://localhost:8081/actuator/health  # Collections"
    echo "   curl http://localhost:8082/actuator/health  # Manufacturing"
    echo "3. View Grafana: http://localhost:3000"
    echo "4. View Kafka UI: http://localhost:8090"

else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                  KAFKA FAILED TO START                         ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Full Kafka logs:${NC}"
    docker logs biopro-kafka 2>&1

    echo ""
    echo -e "${YELLOW}Please share these logs for further troubleshooting${NC}"
fi
