#!/bin/bash
# Fix port conflicts and restart BioPro stack

echo "🔧 BioPro Port Conflict Fixer"
echo "=============================="
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

echo "📍 Current directory: $(pwd)"
echo ""

# Stop all containers first
echo "🛑 Stopping all containers..."
docker-compose down
echo ""

# Check for port conflicts (Windows style in WSL)
echo "🔍 Checking for port conflicts..."
echo ""

echo "Port 2181 (Zookeeper):"
netstat.exe -ano | findstr.exe :2181 || echo "  ✅ Port 2181 is free"
echo ""

echo "Port 9092 (Kafka):"
netstat.exe -ano | findstr.exe :9092 || echo "  ✅ Port 9092 is free"
echo ""

echo "Port 8080 (Orders):"
netstat.exe -ano | findstr.exe :8080 || echo "  ✅ Port 8080 is free"
echo ""

echo "Port 8081 (Collections/Schema Registry):"
netstat.exe -ano | findstr.exe :8081 || echo "  ✅ Port 8081 is free"
echo ""

echo "Port 8082 (Manufacturing):"
netstat.exe -ano | findstr.exe :8082 || echo "  ✅ Port 8082 is free"
echo ""

# If ports are in use, show how to kill them
if netstat.exe -ano | findstr.exe :2181 > /dev/null; then
    echo "⚠️  Port 2181 is in use!"
    echo "   Run this in PowerShell as Administrator:"
    PID=$(netstat.exe -ano | findstr.exe :2181 | awk '{print $5}' | head -1)
    echo "   Stop-Process -Id $PID -Force"
    echo ""
fi

if netstat.exe -ano | findstr.exe :9092 > /dev/null; then
    echo "⚠️  Port 9092 is in use!"
    echo "   Run this in PowerShell as Administrator:"
    PID=$(netstat.exe -ano | findstr.exe :9092 | awk '{print $5}' | head -1)
    echo "   Stop-Process -Id $PID -Force"
    echo ""
fi

# Offer to continue or abort
read -p "Continue with startup? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "🧹 Cleaning up old volumes..."
docker-compose down -v

echo ""
echo "🚀 Starting BioPro stack..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting 30 seconds for services to start..."
sleep 30

echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "✅ Done!"
echo ""
echo "To check logs: docker-compose logs -f"
echo "To check Kafka: docker-compose logs kafka | grep 'Kafka Server started'"
