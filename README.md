# BioPro Event Governance POC

Event-driven microservices architecture with Kafka, Schema Registry, and comprehensive monitoring.

## 🚀 Quick Start

### Start Everything at Once

```bash
./start-all.sh
```

This single command will:
- ✓ Stop any existing containers
- ✓ Build all services with latest changes
- ✓ Start all infrastructure (Zookeeper, Kafka, Schema Registry)
- ✓ Wait for services to be healthy
- ✓ Start all application services (Orders, Manufacturing, Collections)
- ✓ Start monitoring tools (Prometheus, Grafana, kcat)
- ✓ Show cluster status and available commands
- ✓ Optionally launch interactive Kafka UI

### Interactive Kafka Monitoring UI

```bash
./kafka-ui.sh
```

Menu-driven interface for monitoring Kafka using kcat.

## 📋 Services Overview

**Application Services:**
- Orders Service (8080)
- Manufacturing Service (8082)  
- Collections Service (8083)

**Infrastructure:**
- Kafka (9092)
- Schema Registry (8081)
- kcat (CLI monitoring)

**Monitoring:**
- Prometheus (9090)
- Grafana (3000)

## 🛠️ Common Commands

```bash
# Start everything
./start-all.sh

# Interactive Kafka UI
./kafka-ui.sh

# Quick Kafka commands
./kafka-monitor.sh brokers
./kafka-monitor.sh topics
./kafka-monitor.sh dlq

# Stop everything
docker-compose down
```

See KCAT-QUICKSTART.md for detailed kcat usage.
