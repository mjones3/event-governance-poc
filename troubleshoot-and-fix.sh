#!/bin/bash
# BioPro Event Governance - Complete Troubleshooting and Fix Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  BioPro Event Governance - Troubleshooting & Auto-Fix         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Find the correct path (works in both WSL and Linux)
if [ -d "/mnt/c/Users/MelvinJones/work/event-governance/poc" ]; then
    PROJECT_DIR="/mnt/c/Users/MelvinJones/work/event-governance/poc"
elif [ -d "C:/Users/MelvinJones/work/event-governance/poc" ]; then
    PROJECT_DIR="C:/Users/MelvinJones/work/event-governance/poc"
else
    PROJECT_DIR="$(pwd)"
fi

echo -e "${BLUE}📍 Project Directory: $PROJECT_DIR${NC}"
cd "$PROJECT_DIR" 2>/dev/null || {
    echo -e "${RED}❌ Cannot find project directory${NC}"
    echo "Please run this script from: /mnt/c/Users/MelvinJones/work/event-governance/poc"
    exit 1
}

# Create diagnostic log file
LOG_FILE="troubleshooting-$(date +%Y%m%d-%H%M%S).log"
echo "Creating diagnostic log: $LOG_FILE"
echo ""

# Function to log and display
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 1: Checking Docker Status${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

if ! docker ps > /dev/null 2>&1; then
    log "${RED}❌ Docker is not running or not accessible${NC}"
    log "${YELLOW}Please start Docker Desktop and try again${NC}"
    exit 1
else
    log "${GREEN}✅ Docker is running${NC}"
fi

log ""
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 2: Stopping All Existing Containers${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

docker-compose down 2>&1 | tee -a "$LOG_FILE"
log "${GREEN}✅ Containers stopped${NC}"

log ""
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 3: Checking Port Conflicts${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

PORTS=(2181 9092 8080 8081 8082 9090 3000 8090)
CONFLICTS=0

for port in "${PORTS[@]}"; do
    if command -v netstat.exe &> /dev/null; then
        # WSL - use Windows netstat
        RESULT=$(netstat.exe -ano 2>/dev/null | grep ":$port " | grep LISTENING || true)
    else
        # Linux
        RESULT=$(netstat -tuln 2>/dev/null | grep ":$port " || true)
    fi

    if [ -n "$RESULT" ]; then
        log "${RED}❌ Port $port is in use:${NC}"
        log "$RESULT"
        CONFLICTS=$((CONFLICTS + 1))
    else
        log "${GREEN}✅ Port $port is available${NC}"
    fi
done

if [ $CONFLICTS -gt 0 ]; then
    log ""
    log "${YELLOW}⚠️  Found $CONFLICTS port conflict(s)${NC}"
    log "${YELLOW}Attempting to kill conflicting processes...${NC}"

    # Try to kill via Docker
    docker ps -a -q | xargs -r docker rm -f 2>&1 | tee -a "$LOG_FILE" || true

    log "${YELLOW}If ports are still in use, run this in PowerShell as Administrator:${NC}"
    log "${YELLOW}Get-NetTCPConnection -LocalPort 2181,9092,8080,8081,8082 | ForEach-Object { Stop-Process -Id \$_.OwningProcess -Force }${NC}"
    log ""
    read -p "Press Enter after killing processes, or Ctrl+C to abort..."
fi

log ""
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 4: Cleaning Old Volumes and Networks${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

docker-compose down -v 2>&1 | tee -a "$LOG_FILE"
docker network prune -f 2>&1 | tee -a "$LOG_FILE" || true
log "${GREEN}✅ Cleaned up old resources${NC}"

log ""
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 5: Checking Docker Compose Configuration${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

if [ ! -f "docker-compose.yml" ]; then
    log "${RED}❌ docker-compose.yml not found!${NC}"
    exit 1
fi

docker-compose config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    log "${GREEN}✅ docker-compose.yml is valid${NC}"
else
    log "${RED}❌ docker-compose.yml has syntax errors${NC}"
    docker-compose config 2>&1 | tee -a "$LOG_FILE"
    exit 1
fi

log ""
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 6: Starting Infrastructure (Zookeeper → Kafka → Schema Registry)${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

# Start Zookeeper first
log "${BLUE}Starting Zookeeper...${NC}"
docker-compose up -d zookeeper 2>&1 | tee -a "$LOG_FILE"
log "Waiting 15 seconds for Zookeeper to be ready..."
sleep 15

# Check Zookeeper
docker-compose ps zookeeper | tee -a "$LOG_FILE"
docker logs biopro-zookeeper 2>&1 | tail -20 | tee -a "$LOG_FILE"

if docker logs biopro-zookeeper 2>&1 | grep -q "binding to port"; then
    log "${GREEN}✅ Zookeeper started successfully${NC}"
else
    log "${RED}❌ Zookeeper failed to start${NC}"
    log "${YELLOW}Zookeeper logs:${NC}"
    docker logs biopro-zookeeper 2>&1 | tee -a "$LOG_FILE"
    exit 1
fi

# Start Kafka
log ""
log "${BLUE}Starting Kafka...${NC}"
docker-compose up -d kafka 2>&1 | tee -a "$LOG_FILE"
log "Waiting 30 seconds for Kafka to be ready..."
sleep 30

# Check Kafka detailed
log ""
log "${BLUE}Checking Kafka status...${NC}"
docker-compose ps kafka | tee -a "$LOG_FILE"

log ""
log "${BLUE}Last 50 lines of Kafka logs:${NC}"
docker logs biopro-kafka 2>&1 | tail -50 | tee -a "$LOG_FILE"

if docker logs biopro-kafka 2>&1 | grep -q "Kafka Server started"; then
    log "${GREEN}✅ Kafka started successfully!${NC}"
elif docker logs biopro-kafka 2>&1 | grep -q "started (kafka.server.KafkaServer)"; then
    log "${GREEN}✅ Kafka started successfully!${NC}"
else
    log "${RED}❌ Kafka failed to start${NC}"
    log ""
    log "${YELLOW}Analyzing Kafka logs for errors...${NC}"

    # Check for specific errors
    if docker logs biopro-kafka 2>&1 | grep -q "Address already in use"; then
        log "${RED}ERROR: Port already in use${NC}"
        log "Run: netstat -ano | findstr :9092"
        log "Then kill the process using that port"
    fi

    if docker logs biopro-kafka 2>&1 | grep -q "Unable to connect to zookeeper"; then
        log "${RED}ERROR: Cannot connect to Zookeeper${NC}"
        log "Checking Zookeeper..."
        docker logs biopro-zookeeper 2>&1 | tail -30 | tee -a "$LOG_FILE"
    fi

    if docker logs biopro-kafka 2>&1 | grep -q "FATAL"; then
        log "${RED}FATAL error found:${NC}"
        docker logs biopro-kafka 2>&1 | grep FATAL | tee -a "$LOG_FILE"
    fi

    log ""
    log "${YELLOW}Full Kafka logs saved to: $LOG_FILE${NC}"
    exit 1
fi

# Start Schema Registry
log ""
log "${BLUE}Starting Schema Registry...${NC}"
docker-compose up -d schema-registry 2>&1 | tee -a "$LOG_FILE"
log "Waiting 15 seconds for Schema Registry..."
sleep 15

if docker logs biopro-schema-registry 2>&1 | grep -q "Server started"; then
    log "${GREEN}✅ Schema Registry started successfully${NC}"
else
    log "${YELLOW}⚠️  Schema Registry may still be starting...${NC}"
fi

log ""
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 7: Starting Monitoring (Prometheus + Grafana)${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

docker-compose up -d prometheus grafana 2>&1 | tee -a "$LOG_FILE"
log "${GREEN}✅ Monitoring services started${NC}"

log ""
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 8: Building and Starting Spring Boot Services${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

log "${BLUE}Building services (this may take 5-10 minutes first time)...${NC}"
docker-compose build orders-service collections-service manufacturing-service 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    log "${GREEN}✅ Services built successfully${NC}"

    log ""
    log "${BLUE}Starting services...${NC}"
    docker-compose up -d orders-service collections-service manufacturing-service 2>&1 | tee -a "$LOG_FILE"

    log "Waiting 30 seconds for services to start..."
    sleep 30
else
    log "${RED}❌ Build failed${NC}"
    log "Check the log file for details: $LOG_FILE"
    exit 1
fi

log ""
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 9: Starting Kafka UI${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

docker-compose up -d kafka-ui 2>&1 | tee -a "$LOG_FILE"
log "${GREEN}✅ Kafka UI started${NC}"

log ""
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log "${YELLOW}STEP 10: Final Status Check${NC}"
log "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

log ""
log "${BLUE}All Containers:${NC}"
docker-compose ps | tee -a "$LOG_FILE"

log ""
log "${BLUE}Testing Service Endpoints:${NC}"

# Test Orders
if curl -s -f http://localhost:8080/actuator/health > /dev/null 2>&1; then
    log "${GREEN}✅ Orders Service: UP (http://localhost:8080)${NC}"
else
    log "${RED}❌ Orders Service: DOWN${NC}"
    docker logs biopro-orders-service 2>&1 | tail -20 | tee -a "$LOG_FILE"
fi

# Test Collections
if curl -s -f http://localhost:8081/actuator/health > /dev/null 2>&1; then
    log "${GREEN}✅ Collections Service: UP (http://localhost:8081)${NC}"
else
    log "${RED}❌ Collections Service: DOWN${NC}"
    docker logs biopro-collections-service 2>&1 | tail -20 | tee -a "$LOG_FILE"
fi

# Test Manufacturing
if curl -s -f http://localhost:8082/actuator/health > /dev/null 2>&1; then
    log "${GREEN}✅ Manufacturing Service: UP (http://localhost:8082)${NC}"
else
    log "${RED}❌ Manufacturing Service: DOWN${NC}"
    docker logs biopro-manufacturing-service 2>&1 | tail -20 | tee -a "$LOG_FILE"
fi

# Test Schema Registry
if curl -s -f http://localhost:8081/subjects > /dev/null 2>&1; then
    log "${GREEN}✅ Schema Registry: UP (http://localhost:8081)${NC}"
else
    log "${YELLOW}⚠️  Schema Registry: May still be starting...${NC}"
fi

# Test Prometheus
if curl -s -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    log "${GREEN}✅ Prometheus: UP (http://localhost:9090)${NC}"
else
    log "${YELLOW}⚠️  Prometheus: Check at http://localhost:9090${NC}"
fi

# Test Grafana
if curl -s -f http://localhost:3000/api/health > /dev/null 2>&1; then
    log "${GREEN}✅ Grafana: UP (http://localhost:3000)${NC}"
else
    log "${YELLOW}⚠️  Grafana: Check at http://localhost:3000${NC}"
fi

log ""
log "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
log "${GREEN}║                    TROUBLESHOOTING COMPLETE                    ║${NC}"
log "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
log ""
log "${BLUE}📊 Access Points:${NC}"
log "   Orders:          http://localhost:8080/actuator/health"
log "   Collections:     http://localhost:8081/actuator/health"
log "   Manufacturing:   http://localhost:8082/actuator/health"
log "   Kafka UI:        http://localhost:8090"
log "   Prometheus:      http://localhost:9090"
log "   Grafana:         http://localhost:3000"
log ""
log "${BLUE}📝 Logs saved to: $LOG_FILE${NC}"
log ""
log "${BLUE}🔍 Check service logs:${NC}"
log "   docker-compose logs -f kafka"
log "   docker-compose logs -f orders-service"
log ""
log "${BLUE}🛑 Stop everything:${NC}"
log "   docker-compose down"
log ""

# Show any containers that aren't running
UNHEALTHY=$(docker-compose ps | grep -v "Up" | grep -v "NAME" | grep -v "^$" || true)
if [ -n "$UNHEALTHY" ]; then
    log "${YELLOW}⚠️  Some containers are not running:${NC}"
    log "$UNHEALTHY"
    log ""
    log "${YELLOW}Check logs with: docker-compose logs [service-name]${NC}"
fi

log "${GREEN}✅ Done!${NC}"
