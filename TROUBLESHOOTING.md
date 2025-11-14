# BioPro Event Governance - Troubleshooting Guide

Quick reference for common issues and solutions.

---

## 🔴 Current Errors in Logs

### 1. Kafka DNS Resolution Errors

**Symptoms:**
```
java.net.UnknownHostException: kafka: Name or service not known
Couldn't resolve server kafka:29092 from bootstrap.servers
```

**Cause:** Services starting before Kafka is ready (timing issue)

**Solution:**
These errors are **normal during startup** and will resolve automatically. Services retry the connection.

**Wait 2-3 minutes**, then check:
```bash
# Check if Kafka is running
docker ps | grep biopro-kafka

# Check Kafka logs
docker logs biopro-kafka | tail -20

# Verify Kafka is ready
docker exec -it biopro-kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

---

### 2. Grafana Dashboard Directory Missing

**Symptoms:**
```
error="stat /etc/grafana/provisioning/dashboards/json: no such file or directory"
```

**Cause:** Missing directory in the mount path

**Solution:**
✅ **Already Fixed!** Created `grafana/provisioning/dashboards/json/` directory.

Restart Grafana:
```bash
docker-compose restart grafana
```

---

## 🛠️ Common Issues

### Services Won't Start

**Check container status:**
```bash
docker-compose ps
```

**View logs for specific service:**
```bash
docker-compose logs kafka
docker-compose logs schema-registry
docker-compose logs orders-service
```

**Restart specific service:**
```bash
docker-compose restart kafka
docker-compose restart orders-service
```

---

### Kafka Not Ready

**Symptoms:** Schema Registry, Kafka UI can't connect

**Solution:**
```bash
# 1. Check if Kafka container is running
docker-compose ps kafka

# 2. Check Kafka logs for errors
docker-compose logs kafka | grep -i error

# 3. Wait for Kafka to be fully ready (can take 30-60 seconds)
docker-compose logs -f kafka

# Look for: "Kafka Server started"

# 4. Restart dependent services after Kafka is ready
docker-compose restart schema-registry kafka-ui
```

---

### Schema Registry Connection Issues

**Symptoms:**
```
TimeoutException: Timed out waiting for a node assignment
```

**Solution:**
```bash
# 1. Ensure Kafka is running and healthy
docker exec -it biopro-kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# 2. Restart Schema Registry
docker-compose restart schema-registry

# 3. Check Schema Registry logs
docker-compose logs -f schema-registry
```

---

### Spring Boot Services Won't Start

**Build errors:**
```bash
# Rebuild specific service
docker-compose build orders-service

# Rebuild all services
docker-compose build
```

**Runtime errors:**
```bash
# Check service logs
docker-compose logs orders-service
docker-compose logs collections-service
docker-compose logs manufacturing-service

# Look for:
# - "Started OrdersApplication" = success
# - Java exceptions = compilation/runtime errors
```

---

### Port Conflicts

**Symptoms:**
```
Error starting userland proxy: listen tcp 0.0.0.0:8080: bind: address already in use
```

**Solution:**
```bash
# Find process using the port (Windows)
netstat -ano | findstr :8080

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change ports in docker-compose.yml
```

---

## ✅ Verification Steps

### 1. Check All Containers Running

```bash
docker-compose ps
```

**Expected:** All containers should show "Up" status

### 2. Verify Infrastructure

```bash
# Kafka
curl http://localhost:9092
# Should connect (even if it returns binary data)

# Schema Registry
curl http://localhost:8081/subjects
# Should return: []

# Kafka UI
curl http://localhost:8090
# Should return HTML

# Prometheus
curl http://localhost:9090
# Should return HTML

# Grafana
curl http://localhost:3000
# Should return HTML or redirect
```

### 3. Verify Spring Boot Services

```bash
# Orders
curl http://localhost:8080/actuator/health
# Expected: {"status":"UP"}

# Collections
curl http://localhost:8081/actuator/health
# Expected: {"status":"UP"}

# Manufacturing
curl http://localhost:8082/actuator/health
# Expected: {"status":"UP"}
```

### 4. Verify Prometheus Metrics

```bash
curl http://localhost:8080/actuator/prometheus | grep biopro
curl http://localhost:8081/actuator/prometheus | grep biopro
curl http://localhost:8082/actuator/prometheus | grep biopro
```

**Expected:** Should see `biopro_*` metrics

### 5. Check Prometheus Targets

Open: http://localhost:9090/targets

**Expected:** All 3 targets (orders, collections, manufacturing) showing as **UP**

---

## 🔄 Complete Restart Procedure

If things aren't working, try this:

```bash
# 1. Stop everything
docker-compose down

# 2. Remove volumes (WARNING: deletes all data)
docker-compose down -v

# 3. Rebuild images
docker-compose build --no-cache

# 4. Start infrastructure first (wait for each to be ready)
docker-compose up -d zookeeper
sleep 10
docker-compose up -d kafka
sleep 20
docker-compose up -d schema-registry
sleep 10

# 5. Start monitoring
docker-compose up -d prometheus grafana

# 6. Start services
docker-compose up -d orders-service collections-service manufacturing-service

# 7. Start UI tools
docker-compose up -d kafka-ui

# 8. Check logs
docker-compose logs -f
```

---

## 📊 Startup Timing

**Expected startup times:**

| Service | Time to Ready | Check Command |
|---------|---------------|---------------|
| Zookeeper | 5-10s | `docker logs biopro-zookeeper` |
| Kafka | 20-30s | `docker exec biopro-kafka kafka-broker-api-versions --bootstrap-server localhost:9092` |
| Schema Registry | 10-15s | `curl http://localhost:8081` |
| Prometheus | 5-10s | `curl http://localhost:9090` |
| Grafana | 10-15s | `curl http://localhost:3000` |
| Spring Boot Services | 30-45s | `curl http://localhost:8080/actuator/health` |

**Total time for full stack:** ~2-3 minutes

---

## 🔍 Useful Commands

### View All Logs
```bash
docker-compose logs -f
```

### View Specific Service Logs
```bash
docker-compose logs -f kafka
docker-compose logs -f orders-service
docker-compose logs -f prometheus
```

### Check Last 50 Lines
```bash
docker-compose logs --tail=50 orders-service
```

### Follow Logs (real-time)
```bash
docker-compose logs -f orders-service
```

### Execute Command in Container
```bash
# Kafka commands
docker exec -it biopro-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Check Schema Registry
docker exec -it biopro-schema-registry curl http://localhost:8081/subjects

# Check service health
docker exec -it biopro-orders-service curl http://localhost:8080/actuator/health
```

---

## 🐛 Debug Mode

Enable verbose logging in application.yml:

```yaml
logging:
  level:
    com.biopro: DEBUG
    org.springframework.kafka: DEBUG
    org.apache.kafka: DEBUG
```

Then rebuild:
```bash
docker-compose up -d --build orders-service
docker-compose logs -f orders-service
```

---

## 📞 Still Having Issues?

1. **Check Docker resources:**
   - Ensure Docker has enough memory (4GB+ recommended)
   - Ensure Docker has enough disk space

2. **Check network:**
   ```bash
   docker network ls
   docker network inspect biopro-network
   ```

3. **Clean everything and start fresh:**
   ```bash
   docker-compose down -v
   docker system prune -a
   docker-compose up -d --build
   ```

---

**Document Version**: 1.0
**Last Updated**: November 4, 2025
