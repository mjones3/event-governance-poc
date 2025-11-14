#!/bin/bash
# Rebuild all services with Prometheus metrics support

echo "🔨 Rebuilding BioPro services with Prometheus metrics..."
echo ""

# Navigate to project directory
if [ -d "/mnt/c/Users/MelvinJones/work/event-governance/poc" ]; then
    cd "/mnt/c/Users/MelvinJones/work/event-governance/poc"
else
    cd "$(dirname "$0")"
fi

echo "📍 Working directory: $(pwd)"
echo ""

echo "🛑 Stopping services..."
docker-compose stop orders-service collections-service manufacturing-service

echo ""
echo "🔨 Rebuilding Orders service..."
docker-compose build --no-cache orders-service

echo ""
echo "🔨 Rebuilding Collections service..."
docker-compose build --no-cache collections-service

echo ""
echo "🔨 Rebuilding Manufacturing service..."
docker-compose build --no-cache manufacturing-service

echo ""
echo "🚀 Starting services..."
docker-compose up -d orders-service collections-service manufacturing-service

echo ""
echo "⏳ Waiting 45 seconds for services to start..."
sleep 45

echo ""
echo "✅ Testing Prometheus endpoints..."
echo ""

echo "📊 Orders Service:"
curl -s http://localhost:8080/actuator/prometheus | head -5
if curl -s http://localhost:8080/actuator/prometheus | grep -q "jvm_memory"; then
    echo "✅ Prometheus metrics are working!"
else
    echo "❌ No metrics found"
fi

echo ""
echo "📊 Collections Service:"
curl -s http://localhost:8081/actuator/prometheus | head -5
if curl -s http://localhost:8081/actuator/prometheus | grep -q "jvm_memory"; then
    echo "✅ Prometheus metrics are working!"
else
    echo "❌ No metrics found"
fi

echo ""
echo "📊 Manufacturing Service:"
curl -s http://localhost:8082/actuator/prometheus | head -5
if curl -s http://localhost:8082/actuator/prometheus | grep -q "jvm_memory"; then
    echo "✅ Prometheus metrics are working!"
else
    echo "❌ No metrics found"
fi

echo ""
echo "🎉 Done! All services rebuilt with Prometheus support."
echo ""
echo "Test metrics with:"
echo "  curl http://localhost:8080/actuator/prometheus | grep biopro"
echo "  curl http://localhost:8081/actuator/prometheus | grep biopro"
echo "  curl http://localhost:8082/actuator/prometheus | grep biopro"
