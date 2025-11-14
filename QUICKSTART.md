# BioPro Event Governance Framework - Quick Start Guide

Get up and running with the BioPro Event Governance Framework in 5 minutes!

## Prerequisites

- Java 17+ installed
- Maven 3.9+ installed
- Docker Desktop running

## Step-by-Step Guide

### 1. Start Infrastructure (2 minutes)

Open a terminal and navigate to the project directory:

```bash
cd C:\Users\MelvinJones\work\event-governance\poc
docker-compose up -d
```

Wait for all services to start (about 30-60 seconds):

```bash
docker-compose ps
```

All services should show status "Up" or "Up (healthy)".

### 2. Build the Project (2 minutes)

```bash
mvn clean install
```

This will:
- Compile all modules
- Generate Avro classes
- Run unit tests
- Package artifacts

### 3. Run the Orders Demo Service (1 minute)

Open a new terminal:

```bash
cd biopro-demo-orders
mvn spring-boot:run
```

Wait for the log message:
```
┌─────────────────────────────────────────────────────────┐
│  BioPro Event Governance Framework Initialized          │
└─────────────────────────────────────────────────────────┘
```

The service is now running on `http://localhost:8080`

### 4. Test the Service

#### Option A: Use the Test Script

**Windows:**
```bash
test-demo.bat
```

**Linux/Mac:**
```bash
chmod +x test-demo.sh
./test-demo.sh
```

#### Option B: Manual Testing

Create a test order:

```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-12345",
    "bloodType": "O_POSITIVE",
    "quantity": 2,
    "priority": "URGENT",
    "facilityId": "FAC-001",
    "requestedBy": "DR-SMITH"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Order event published successfully",
  "orderId": "ORD-12345"
}
```

### 5. Verify Everything is Working

#### Check Kafka Topics

1. Open Kafka UI: http://localhost:8090
2. Navigate to Topics
3. You should see:
   - `biopro.orders.events` - Main events
   - `biopro.orders.dlq` - Dead letter queue

#### Check Metrics

View available metrics:
```bash
curl http://localhost:8080/actuator/metrics
```

View specific metric:
```bash
curl http://localhost:8080/actuator/metrics/biopro.dlq.events.total
```

**Note**: Metrics are automatically exported to Dynatrace OneAgent. Configure Dynatrace in production by setting:
```yaml
management:
  metrics:
    export:
      dynatrace:
        uri: ${DYNATRACE_URI}
        api-token: ${DYNATRACE_API_TOKEN}
```

#### Check Health

```bash
curl http://localhost:8080/actuator/health
```

## What's Next?

### Explore the Demo

1. **Publish Multiple Events**
   ```bash
   # Routine order
   curl -X POST http://localhost:8080/api/orders \
     -H "Content-Type: application/json" \
     -d '{"orderId":"ORD-001","bloodType":"A_POSITIVE","quantity":1,"priority":"ROUTINE","facilityId":"FAC-001","requestedBy":"DR-DOE"}'

   # Emergency order
   curl -X POST http://localhost:8080/api/orders \
     -H "Content-Type: application/json" \
     -d '{"orderId":"ORD-002","bloodType":"AB_NEGATIVE","quantity":5,"priority":"LIFE_THREATENING","facilityId":"FAC-002","requestedBy":"DR-JANE"}'
   ```

2. **View Events in Kafka UI**
   - Go to http://localhost:8090
   - Click on Topics → `biopro.orders.events`
   - View messages

3. **Monitor Metrics**
   - Open http://localhost:8080/actuator/metrics
   - Search for `biopro.dlq` or `biopro.schema`

### Run Other Demo Services

**Collections Service** (Terminal 2):
```bash
cd biopro-demo-collections
mvn spring-boot:run
```
Service runs on port 8081

**Manufacturing Service** (Terminal 3):
```bash
cd biopro-demo-manufacturing
mvn spring-boot:run
```
Service runs on port 8082

### Integrate Into Your Project

Add the starter to your `pom.xml`:

```xml
<dependency>
    <groupId>com.biopro</groupId>
    <artifactId>biopro-dlq-spring-boot-starter</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</dependency>
```

Configure in `application.yml`:

```yaml
biopro:
  dlq:
    enabled: true
    module-name: your-module-name
```

That's it! The framework auto-configures everything else.

## Troubleshooting

### Infrastructure Not Starting

If Docker Compose fails:

```bash
# Stop everything
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Build Failures

Clear Maven cache:

```bash
mvn clean
rm -rf ~/.m2/repository/com/biopro
mvn install
```

### Port Conflicts

If ports are already in use, modify `docker-compose.yml`:

```yaml
# Change port mappings, e.g.:
ports:
  - "9093:9092"  # Instead of 9092:9092
```

### Can't Connect to Kafka

Ensure Docker networking is working:

```bash
docker network ls
docker network inspect poc_biopro-network
```

## Cleanup

### Stop Services

```bash
# Stop Spring Boot app
Ctrl+C in the terminal

# Stop Docker services
docker-compose down

# Stop and remove volumes (complete cleanup)
docker-compose down -v
```

## Need Help?

- Review the main README: [README.md](README.md)
- Check architecture docs: [ARCHITECTURE.md](ARCHITECTURE.md)
- View logs: `docker-compose logs -f`
- Check application logs in the terminal running Spring Boot

## Success Checklist

- ✅ Docker Compose services running
- ✅ Maven build successful
- ✅ Orders service started
- ✅ Test event published successfully
- ✅ Events visible in Kafka UI
- ✅ Metrics endpoint responding
- ✅ Health check passing

**Congratulations! You've successfully set up the BioPro Event Governance Framework!** 🎉
