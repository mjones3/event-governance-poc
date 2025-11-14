# BioPro Event Governance - START HERE

Complete startup guide for running the BioPro Event Governance stack.

---

## 🚨 PREREQUISITE: Docker Desktop Must Be Running

### Windows:
1. **Start Docker Desktop**
   - Open Docker Desktop application
   - Wait for the whale icon in system tray to show "Docker Desktop is running"
   - Verify by opening PowerShell and running:
     ```powershell
     docker ps
     ```
   - Should show a table (even if empty) - if you get an error, Docker isn't running

### Linux/WSL2:
```bash
# Check if Docker daemon is running
docker ps

# If not running, start it
sudo systemctl start docker

# Or if using Docker Desktop on WSL2
# Open Docker Desktop app on Windows
```

---

## 🚀 Quick Start (After Docker is Running)

### 1. Navigate to Project Directory

**Windows PowerShell:**
```powershell
cd C:\Users\MelvinJones\work\event-governance\poc
```

**WSL/Linux:**
```bash
cd /mnt/c/Users/MelvinJones/work/event-governance/poc
```

### 2. Start All Services

```bash
docker-compose up -d --build
```

**This will:**
- Build all 3 Spring Boot services (Orders, Collections, Manufacturing)
- Start Kafka infrastructure
- Start Prometheus + Grafana monitoring
- **First time:** Takes ~5-10 minutes (Maven downloads dependencies)
- **Subsequent starts:** Takes ~2-3 minutes

### 3. Wait for Startup

**IMPORTANT:** Wait 2-3 minutes for all services to be ready!

```bash
# Watch the logs (Ctrl+C to exit)
docker-compose logs -f

# Look for these success messages:
# ✅ Kafka: "Kafka Server started"
# ✅ Orders: "Started OrdersApplication"
# ✅ Collections: "Started CollectionsApplication"
# ✅ Manufacturing: "Started ManufacturingApplication"
```

### 4. Verify Everything is Running

```bash
# Check container status
docker-compose ps

# All containers should show "Up" status
```

---

## 🔍 Step-by-Step Verification

### Step 1: Check Docker is Running

```powershell
# Windows PowerShell
docker ps

# Expected: Table showing containers (or empty table if none running)
# Error: "The system cannot find the file specified" = Docker not running!
```

### Step 2: Check Kafka Logs

```bash
docker-compose logs kafka | grep "Kafka Server started"
```

**If you see this message:** ✅ Kafka is running!

**If not, check for errors:**
```bash
# See last 50 lines
docker-compose logs --tail=50 kafka

# Common issues:
# - "Connection refused" to Zookeeper = Zookeeper not ready
# - "Address already in use" = Port 9092 is taken
# - Nothing logged = Container didn't start (check Docker Desktop)
```

### Step 3: Verify Zookeeper First

Kafka depends on Zookeeper, so check it first:

```bash
# Check Zookeeper logs
docker-compose logs zookeeper | grep "binding to port"

# Should see: "binding to port 0.0.0.0/0.0.0.0:2181"
```

### Step 4: Check Spring Boot Services

```bash
# Health checks (wait until Kafka is ready)
curl http://localhost:8080/actuator/health  # Orders
curl http://localhost:8081/actuator/health  # Collections
curl http://localhost:8082/actuator/health  # Manufacturing

# Expected response: {"status":"UP"}
```

### Step 5: Verify Prometheus Metrics

```bash
curl http://localhost:8080/actuator/prometheus | grep biopro

# Should see metrics like:
# biopro_dlq_events_total
# biopro_schema_validation_total
```

### Step 6: Check Grafana

Open browser: http://localhost:3000
- Should load Grafana UI (no login required)
- Navigate to Dashboards → BioPro folder

---

## 🐛 Common Issues & Solutions

### Issue 1: Docker Desktop Not Running

**Error:**
```
error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine...
The system cannot find the file specified.
```

**Solution:**
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon stops animating)
3. Try `docker ps` again

---

### Issue 2: Kafka Won't Start

**Check Zookeeper first:**
```bash
docker-compose logs zookeeper
```

**If Zookeeper has errors, restart it:**
```bash
docker-compose restart zookeeper
sleep 10
docker-compose restart kafka
```

**Check if port 9092 is already in use:**
```powershell
# Windows
netstat -ano | findstr :9092

# If something is using it, kill it or change the port in docker-compose.yml
```

**Check Kafka logs for specific error:**
```bash
docker-compose logs kafka | grep -i error
```

---

### Issue 3: Spring Boot Services Won't Build

**Maven errors during build:**
```bash
# View build logs
docker-compose logs orders-service | grep ERROR
docker-compose logs collections-service | grep ERROR
docker-compose logs manufacturing-service | grep ERROR
```

**Common fixes:**
```bash
# Clean rebuild
docker-compose build --no-cache orders-service

# If SSL/Maven errors persist:
# The Docker build should work even with local Maven issues
# Just let Docker handle the build
```

---

### Issue 4: Schema Registry Can't Connect

**Symptoms:**
```
TimeoutException: Timed out waiting for a node assignment
```

**Solution:**
```bash
# 1. Verify Kafka is running
docker exec biopro-kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# 2. If Kafka is ready, restart Schema Registry
docker-compose restart schema-registry

# 3. Check Schema Registry logs
docker-compose logs -f schema-registry
```

---

### Issue 5: Services Can't Resolve DNS "kafka"

**Error in logs:**
```
java.net.UnknownHostException: kafka
```

**This is NORMAL during startup!**
- Services start before Kafka is ready
- They retry automatically
- **Wait 2-3 minutes** - errors will resolve

**If errors persist after 5 minutes:**
```bash
# Check network
docker network inspect biopro-network

# Verify Kafka container name
docker ps | grep kafka

# Restart problematic service
docker-compose restart orders-service
```

---

## 📊 Expected Startup Sequence

```
Time    Service           Status
-----   ---------------   --------------------------------
0:00    Zookeeper         Starting...
0:10    Zookeeper         ✅ Ready (port 2181)
0:10    Kafka             Starting...
0:30    Kafka             ✅ Ready (port 9092)
0:30    Schema Registry   Starting...
0:45    Schema Registry   ✅ Ready (port 8081)
0:45    Prometheus        ✅ Ready (port 9090)
0:45    Grafana           ✅ Ready (port 3000)
1:00    Orders Service    Building...
1:30    Orders Service    ✅ Ready (port 8080)
1:30    Collections       ✅ Ready (port 8081)
1:30    Manufacturing     ✅ Ready (port 8082)
2:00    Kafka UI          ✅ Ready (port 8090)
```

**Total time:** 2-3 minutes (first build takes 5-10 minutes)

---

## 🎯 Success Checklist

Run these commands to verify everything is working:

```bash
# ✅ Check all containers are up
docker-compose ps

# ✅ Check Kafka is ready
docker exec biopro-kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# ✅ Check Schema Registry
curl http://localhost:8081/subjects

# ✅ Check Spring Boot services
curl http://localhost:8080/actuator/health
curl http://localhost:8081/actuator/health
curl http://localhost:8082/actuator/health

# ✅ Check Prometheus targets (all should be UP)
# Open: http://localhost:9090/targets

# ✅ Check Grafana
# Open: http://localhost:3000

# ✅ Check metrics are exposed
curl http://localhost:8080/actuator/prometheus | grep biopro_dlq
```

**If all checks pass:** 🎉 You're ready to use the system!

---

## 🔄 Clean Restart (Nuclear Option)

If nothing works, try this complete reset:

```bash
# Stop everything
docker-compose down

# Remove ALL data (WARNING: Deletes Kafka messages, metrics, etc.)
docker-compose down -v

# Remove Docker network
docker network rm biopro-network 2>/dev/null || true

# Rebuild everything from scratch
docker-compose build --no-cache

# Start with proper timing
docker-compose up -d zookeeper
echo "Waiting for Zookeeper..."
sleep 15

docker-compose up -d kafka
echo "Waiting for Kafka..."
sleep 30

docker-compose up -d schema-registry prometheus grafana
echo "Waiting for infrastructure..."
sleep 15

docker-compose up -d orders-service collections-service manufacturing-service
echo "Waiting for services..."
sleep 30

docker-compose up -d kafka-ui

# Check status
docker-compose ps
```

---

## 📝 Quick Commands Reference

```bash
# Start everything
docker-compose up -d --build

# Stop everything
docker-compose down

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f kafka
docker-compose logs -f orders-service

# Restart specific service
docker-compose restart kafka
docker-compose restart orders-service

# Rebuild specific service
docker-compose build orders-service
docker-compose up -d orders-service

# Check container status
docker-compose ps

# Execute command in container
docker exec -it biopro-kafka kafka-topics --bootstrap-server localhost:9092 --list
```

---

## 🆘 Still Having Issues?

1. **Check Docker Desktop Resources:**
   - Settings → Resources
   - Memory: At least 4GB (8GB recommended)
   - CPU: At least 2 cores (4 recommended)
   - Disk: At least 20GB free

2. **Check Firewall/Antivirus:**
   - Ensure Docker has network access
   - Ports 8080-8082, 9090, 3000, 8090, 9092, 2181 aren't blocked

3. **View detailed logs:**
   ```bash
   docker-compose logs > full-logs.txt
   # Review full-logs.txt for errors
   ```

4. **Check TROUBLESHOOTING.md** for more detailed solutions

---

## 🎓 Next Steps (After Everything is Running)

1. **Test the system:** See [TESTING_GUIDE.md](TESTING_GUIDE.md)
2. **Publish test events:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. **View metrics in Grafana:** http://localhost:3000
4. **Monitor with Prometheus:** http://localhost:9090

---

**Document Version**: 1.0
**Last Updated**: November 5, 2025
