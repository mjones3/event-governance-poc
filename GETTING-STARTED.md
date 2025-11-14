# Getting Started - BioPro Event Governance POC

## 🎯 One Command to Rule Them All

```bash
./start-all.sh
```

That's it! This single script will:
1. ✓ Stop any running containers
2. ✓ Build all services (with latest code)
3. ✓ Start infrastructure (Kafka, Zookeeper, Schema Registry)
4. ✓ Wait for services to be healthy
5. ✓ Start your 3 microservices
6. ✓ Start monitoring tools
7. ✓ Display cluster status
8. ✓ Offer to launch interactive Kafka UI

## 📺 Interactive Kafka Monitoring UI

After services are running, launch the interactive menu:

```bash
./kafka-ui.sh
```

### Features:
- **[1] View Broker Status** - Check Kafka broker health
- **[2] List All Topics** - See all topics in cluster
- **[3] View DLQ Messages** - Inspect last 10 failed events
- **[4] Monitor DLQ in Real-Time** - Live tail of new failures
- **[5] Consume from Specific Topic** - Read any topic's messages
- **[6] Show Full Cluster Metadata** - Complete cluster info
- **[7] Produce Test Message** - Send test event to DLQ
- **[8] Check Service Health** - Docker container status
- **[9] View Container Logs** - Debug service issues
- **[0] Exit**

## 🚀 Typical Workflow

### 1. Start Everything
```bash
./start-all.sh
```

Wait for the startup script to complete (~30-60 seconds).

### 2. Verify Services Are Running

The script will show you:
```
═══════════════════════════════════════════════════════════
   Service Status
═══════════════════════════════════════════════════════════
NAMES                          STATUS
biopro-orders-service          Up 1 minute (healthy)
biopro-manufacturing-service   Up 1 minute (healthy)
biopro-collections-service     Up 1 minute (healthy)
biopro-kafka                   Up 2 minutes (healthy)
...
```

### 3. Launch Kafka Monitoring

When prompted, type `y` to launch the interactive UI, or run it manually:
```bash
./kafka-ui.sh
```

### 4. Monitor Your Kafka Cluster

From the menu:
- Press `1` to check broker status
- Press `2` to list topics
- Press `4` to monitor DLQ in real-time
- Press `0` to exit

## 📋 Quick Reference Commands

### Service Management
```bash
# Start everything
./start-all.sh

# Stop everything
docker-compose down

# Restart a specific service
docker-compose restart orders-service

# View service logs
docker-compose logs -f orders-service
```

### Kafka Monitoring (CLI)
```bash
# Interactive UI
./kafka-ui.sh

# Quick commands
./kafka-monitor.sh brokers       # Broker info
./kafka-monitor.sh topics        # List topics
./kafka-monitor.sh dlq           # View DLQ
./kafka-monitor.sh dlq-tail      # Monitor DLQ

# Direct kcat
./kcat.sh -L                     # Cluster metadata
```

### Health Checks
```bash
# All services
docker ps

# Specific service
curl http://localhost:8080/actuator/health

# Kafka connectivity
./kcat.sh -L
```

## 🌐 Service URLs

Once started, access these URLs in your browser:

**Applications:**
- Orders: http://localhost:8080/actuator/health
- Manufacturing: http://localhost:8082/actuator/health
- Collections: http://localhost:8083/actuator/health

**Monitoring:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

**Infrastructure:**
- Schema Registry: http://localhost:8081

## 🐛 Troubleshooting

### "Container not running" errors?
```bash
# Check what's running
docker ps

# Restart everything
docker-compose down
./start-all.sh
```

### Kafka UI (web) not working?
That's expected in corporate environments with Netskope. Use kcat instead:
```bash
./kafka-ui.sh
```

### Services failing health checks?
```bash
# Check logs
docker-compose logs orders-service

# Rebuild from scratch
docker-compose down -v
./start-all.sh
```

### Port conflicts?
```bash
# Check ports in use
netstat -an | findstr "8080 8081 8082 8083 9090 9092"

# Change ports in docker-compose.yml if needed
```

## 📚 Additional Documentation

- `README.md` - Complete project documentation
- `KCAT-QUICKSTART.md` - kcat command reference
- `README-KCAT.md` - Detailed kcat examples

## 🎓 Learning the System

### Step 1: Start and Explore
```bash
./start-all.sh
./kafka-ui.sh
```

### Step 2: Check Broker Health
Select option `[1]` from the menu

### Step 3: List Topics
Select option `[2]` - you should see:
- `biopro.orders.dlq`
- `_schemas`
- `__consumer_offsets`

### Step 4: Monitor DLQ
Select option `[4]` to watch for failed events in real-time

### Step 5: Test a Message
Select option `[7]` and enter a test message

### Step 6: View the Message
Select option `[3]` to see your test message in the DLQ

## ✨ That's It!

You now have a complete event-driven microservices platform with Kafka monitoring via kcat.

**Next Steps:**
- Test your services via their REST APIs
- Configure Grafana dashboards
- Add more topics as needed
- Monitor DLQ for failed events

Happy coding! 🚀
