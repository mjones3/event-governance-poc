#!/bin/bash
# BioPro Event Governance - Health Check Script

echo "🔍 BioPro Event Governance - Health Check"
echo "=========================================="
echo ""

# Check if Docker Compose is running
echo "📦 Checking Docker containers..."
docker-compose ps

echo ""
echo "🔍 Checking service health..."
echo ""

# Function to check HTTP endpoint
check_endpoint() {
    local name=$1
    local url=$2

    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|302"; then
        echo "✅ $name: UP"
        return 0
    else
        echo "❌ $name: DOWN"
        return 1
    fi
}

# Check infrastructure
echo "Infrastructure:"
check_endpoint "Kafka UI" "http://localhost:8090"
check_endpoint "Schema Registry" "http://localhost:8081"
check_endpoint "Prometheus" "http://localhost:9090"
check_endpoint "Grafana" "http://localhost:3000"

echo ""
echo "BioPro Services:"
check_endpoint "Orders Service" "http://localhost:8080/actuator/health"
check_endpoint "Collections Service" "http://localhost:8081/actuator/health"
check_endpoint "Manufacturing Service" "http://localhost:8082/actuator/health"

echo ""
echo "📊 Prometheus Metrics:"
if curl -s "http://localhost:8080/actuator/prometheus" | grep -q "biopro"; then
    echo "✅ BioPro metrics exposed"
else
    echo "❌ BioPro metrics not found"
fi

echo ""
echo "🔍 Kafka Topics:"
docker exec -it biopro-kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null || echo "❌ Kafka not ready"

echo ""
echo "=========================================="
echo "Health check complete!"
