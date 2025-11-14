# BioPro Event Governance - Docker Compose Guide

Complete guide for running the entire BioPro Event Governance stack with Docker Compose.

---

## 🎯 Overview

The Docker Compose setup includes:
- **Infrastructure**: Zookeeper, Kafka, Schema Registry, Kafka UI
- **Monitoring**: Prometheus, Grafana (with pre-loaded dashboards)
- **Services**: Orders, Collections, Manufacturing (all 3 Spring Boot apps)

Everything runs in a single command!

---

## 🚀 Quick Start

### 1. Build and Start Everything

```bash
cd C:\Users\MelvinJones\work\event-governance\poc

# Build and start all services
docker-compose up -d --build
```

**What happens:**
- Builds all 3 Spring Boot services from source (multi-stage Docker builds)
- Starts Kafka infrastructure
- Starts Prometheus and Grafana
- Waits for dependencies (healthchecks ensure proper startup order)

**First-time build:** ~5-10 minutes (Maven downloads dependencies)
**Subsequent builds:** ~2-3 minutes (Docker layer caching)

### 2. Check Status

```bash
# View all running containers
docker-compose ps

# Should show:
# - biopro-zookeeper
# - biopro-kafka
# - biopro-schema-registry
# - biopro-kafka-ui
# - biopro-prometheus
# - biopro-grafana
# - biopro-orders-service
# - biopro-collections-service
# - biopro-manufacturing-service
```

### 3. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f orders-service
docker-compose logs -f collections-service
docker-compose logs -f manufacturing-service

# Infrastructure only
docker-compose logs -f kafka schema-registry
```

---

## 🌐 Access Points

Once all services are running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Orders Service** | http://localhost:8080 | REST API + Actuator |
| **Collections Service** | http://localhost:8081 | REST API + Actuator |
| **Manufacturing Service** | http://localhost:8082 | REST API + Actuator |
| **Kafka UI** | http://localhost:8090 | Browse topics, messages, schemas |
| **Schema Registry** | http://localhost:8081 | Schema management |
| **Prometheus** | http://localhost:9090 | Metrics database |
| **Grafana** | http://localhost:3000 | Dashboards (BioPro DLQ pre-loaded) |

### Health Checks

```bash
# Check service health
curl http://localhost:8080/actuator/health
curl http://localhost:8081/actuator/health
curl http://localhost:8082/actuator/health

# View Prometheus metrics
curl http://localhost:8080/actuator/prometheus | grep biopro
curl http://localhost:8081/actuator/prometheus | grep biopro
curl http://localhost:8082/actuator/prometheus | grep biopro
```

---

## 📊 Monitoring

### Grafana Dashboards

1. **Access Grafana**: http://localhost:3000
   - No login required (anonymous auth enabled)
   - Pre-configured Prometheus datasource

2. **Pre-loaded Dashboard**: "BioPro Event Governance - DLQ Metrics"
   - Navigate to: Dashboards → BioPro folder
   - Panels include:
     - DLQ events by module
     - Schema validation rates
     - Processing duration (p95)
     - Reprocessing success/failure
     - Circuit breaker states
     - Retry attempts

### Prometheus

1. **Access Prometheus**: http://localhost:9090

2. **Check Targets**: http://localhost:9090/targets
   - Should show 3 targets (all UP):
     - `biopro-orders` → `orders-service:8080`
     - `biopro-collections` → `collections-service:8081`
     - `biopro-manufacturing` → `manufacturing-service:8082`

3. **Example Queries**:
   ```promql
   # Total DLQ events
   rate(biopro_dlq_events_total[5m])

   # Schema validation success rate
   rate(biopro_schema_validation{result="success"}[5m]) / rate(biopro_schema_validation[5m])

   # P95 processing duration
   histogram_quantile(0.95, rate(biopro_event_processing_duration_bucket[5m]))
   ```

---

## 🛠️ Common Operations

### Rebuild Services After Code Changes

```bash
# Rebuild and restart all services
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build orders-service
docker-compose up -d --build collections-service
docker-compose up -d --build manufacturing-service
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart orders-service
```

### Stop Everything

```bash
# Stop all containers (preserves data volumes)
docker-compose down

# Stop and remove volumes (DELETES ALL DATA)
docker-compose down -v
```

### Scale Services (Optional)

```bash
# Run multiple instances of a service
docker-compose up -d --scale orders-service=3
```

---

## 🔍 Troubleshooting

### Services Won't Start

**Check logs:**
```bash
docker-compose logs orders-service
docker-compose logs collections-service
docker-compose logs manufacturing-service
```

**Common issues:**
- **Kafka not ready**: Wait for `kafka` healthcheck to pass
  ```bash
  docker-compose ps kafka
  # Wait for "healthy" status
  ```
- **Schema Registry not ready**: Depends on Kafka
  ```bash
  docker-compose ps schema-registry
  ```

### Build Failures

**Maven SSL issues:**
```bash
# The Dockerfiles include workarounds for corporate proxies
# If builds fail, check the Maven build stage logs:
docker-compose logs orders-service | grep -i error
```

**Clean rebuild:**
```bash
# Remove all containers and images, rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port Conflicts

**If ports are already in use:**
```bash
# Check what's using the port
netstat -ano | findstr :8080

# Option 1: Stop the conflicting process
# Option 2: Change ports in docker-compose.yml
```

### Kafka Connection Issues

**Verify Kafka is accessible:**
```bash
# From host
docker exec -it biopro-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Test from service container
docker exec -it biopro-orders-service wget -qO- http://kafka:29092
```

---

## 📋 Service Environment Variables

All services are configured with:

```yaml
environment:
  SPRING_KAFKA_BOOTSTRAP_SERVERS: kafka:29092
  SPRING_KAFKA_SCHEMA_REGISTRY_URL: http://schema-registry:8081
  BIOPRO_MONITORING_TYPE: prometheus
```

**To switch to Dynatrace:**
```yaml
# In docker-compose.yml, change:
BIOPRO_MONITORING_TYPE: dynatrace

# And add:
DYNATRACE_URI: ${DYNATRACE_URI}
DYNATRACE_API_TOKEN: ${DYNATRACE_API_TOKEN}
```

---

## 🐳 Docker Compose Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Network                         │
│                  (biopro-network)                        │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐        │
│  │Zookeeper │──│  Kafka   │──│ Schema Registry│        │
│  │  :2181   │  │  :9092   │  │     :8081      │        │
│  └──────────┘  └────┬─────┘  └───────┬────────┘        │
│                     │                 │                  │
│       ┌─────────────┴─────────────────┴────────┐        │
│       │                                         │        │
│  ┌────▼────┐  ┌──────────┐  ┌──────────────┐  │        │
│  │ Orders  │  │Collections│  │Manufacturing │  │        │
│  │  :8080  │  │   :8081   │  │    :8082     │  │        │
│  └────┬────┘  └─────┬─────┘  └──────┬───────┘  │        │
│       │             │                │          │        │
│       └─────────────┴────────────────┼──────────┘        │
│                                      │                   │
│                                 ┌────▼─────┐            │
│                                 │Prometheus│            │
│                                 │  :9090   │            │
│                                 └────┬─────┘            │
│                                      │                   │
│                                 ┌────▼─────┐            │
│                                 │ Grafana  │            │
│                                 │  :3000   │            │
│                                 └──────────┘            │
│                                                           │
│  ┌──────────┐                                            │
│  │Kafka UI  │                                            │
│  │  :8090   │                                            │
│  └──────────┘                                            │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 Additional Resources

- **Main README**: [README.md](README.md)
- **Monitoring Guide**: [MONITORING_GUIDE.md](MONITORING_GUIDE.md)
- **Schema Registration**: [SCHEMA_REGISTRATION_GUIDE.md](SCHEMA_REGISTRATION_GUIDE.md)
- **Kubernetes Deployment**: [K8S_DEPLOYMENT_GUIDE.md](K8S_DEPLOYMENT_GUIDE.md)

---

## 🎓 Best Practices

### 1. Development Workflow

```bash
# Start infrastructure only (first time)
docker-compose up -d zookeeper kafka schema-registry

# Run services locally (for faster development)
mvn spring-boot:run -pl biopro-demo-orders

# Or run everything in Docker
docker-compose up -d --build
```

### 2. Resource Management

```bash
# Monitor resource usage
docker stats

# Clean up unused images/volumes
docker system prune -a
```

### 3. Data Persistence

All data is persisted in Docker volumes:
- `zookeeper-data` - Zookeeper state
- `kafka-data` - Kafka messages
- `prometheus-data` - Metrics time-series
- `grafana-data` - Dashboards and settings

**To reset everything:**
```bash
docker-compose down -v
docker-compose up -d --build
```

---

**Document Version**: 1.0
**Last Updated**: November 4, 2025
**Author**: Event Governance Team
