#!/bin/bash
# BioPro Event Governance - Complete Startup Script
# Brings up all services and provides kcat monitoring interface

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════"
echo "   BioPro Event Governance POC - Starting All Services"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}"

# Function to check if a container is healthy
check_health() {
    local container=$1
    local status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")
    echo "$status"
}

# Function to wait for healthy status
wait_for_health() {
    local container=$1
    local max_wait=60
    local elapsed=0

    echo -n "  Waiting for $container to be healthy..."
    while [ $elapsed -lt $max_wait ]; do
        status=$(check_health "$container")
        if [ "$status" == "healthy" ]; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        elapsed=$((elapsed + 2))
    done
    echo -e " ${YELLOW}timeout (continuing anyway)${NC}"
    return 1
}

# Stop any existing containers
echo -e "${YELLOW}► Stopping existing containers...${NC}"
docker-compose down > /dev/null 2>&1 || true

# Build and start all services
echo -e "${BLUE}► Building and starting all services...${NC}"
docker-compose up -d --build

echo ""
echo -e "${BLUE}► Waiting for infrastructure services to be healthy...${NC}"

# Wait for critical infrastructure
wait_for_health "biopro-redpanda"

echo ""
echo -e "${BLUE}► Waiting for application services to be healthy...${NC}"

# Wait for application services
wait_for_health "biopro-orders-service"
wait_for_health "biopro-manufacturing-service"
wait_for_health "biopro-collections-service"

echo ""
echo -e "${GREEN}✓ All services started successfully!${NC}"
echo ""

# Show service status
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   Service Status${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep biopro

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   Service URLs${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Application Services:${NC}"
echo "  Orders Service:        http://localhost:8080"
echo "  Manufacturing Service: http://localhost:8082"
echo "  Collections Service:   http://localhost:8083"
echo ""
echo -e "${GREEN}Infrastructure:${NC}"
echo "  Schema Registry:       http://localhost:8081"
echo "  Prometheus:            http://localhost:9090"
echo "  Grafana:               http://localhost:3000"
echo ""
echo -e "${GREEN}Kafka Monitoring:${NC}"
echo "  kcat (CLI):            ./kcat.sh -L"
echo "  Kafka Monitor:         ./kafka-monitor.sh [command]"
echo ""

# Show Kafka status using kcat
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   Kafka Cluster Status (via kcat)${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

# Wait a moment for kcat to be ready
sleep 2

# Try to get Kafka status
if docker exec biopro-kcat kcat -b kafka:29092 -L 2>/dev/null | head -20; then
    echo ""
else
    echo -e "${YELLOW}Note: kcat not ready yet, try: ./kafka-monitor.sh brokers${NC}"
    echo ""
fi

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}   Quick Commands${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Kafka Monitoring:${NC}"
echo "  ./kafka-monitor.sh brokers       - Show broker info"
echo "  ./kafka-monitor.sh topics        - List all topics"
echo "  ./kafka-monitor.sh dlq           - View DLQ messages"
echo "  ./kafka-monitor.sh dlq-tail      - Monitor DLQ in real-time"
echo ""
echo -e "${GREEN}Docker Management:${NC}"
echo "  docker-compose logs -f orders-service    - View logs"
echo "  docker-compose down                      - Stop all services"
echo "  docker-compose restart kafka             - Restart a service"
echo ""
echo -e "${GREEN}Interactive Monitoring:${NC}"
echo "  ./kafka-ui.sh        - Launch interactive kcat UI"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup Complete! All services are running.${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Ask if user wants to launch interactive monitoring
read -p "Launch interactive Kafka monitoring UI? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./kafka-ui.sh
fi
