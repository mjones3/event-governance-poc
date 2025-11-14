# BioPro Event Governance Framework - Kubernetes Deployment Guide

Complete guide for deploying the BioPro Event Governance Framework to Kubernetes with Tilt.

---

## 🎯 What Changed

The POC has been **completely upgraded** with real BioPro production schemas and Kubernetes deployment:

### ✅ Real Schemas Integrated

Extracted from actual BioPro production services:

**Collections Service** (`biopro-interface/backend/collections`):
- `CollectionReceivedEvent` - Blood collection received (14 fields + nested Volume objects)
- `CollectionUpdatedEvent` - Blood collection updates
- Enums: `DonationType` (ALLOGENEIC, AUTOLOGOUS), `VolumeType` (12 types)

**Orders Service** (`biopro-distribution/backend/order`):
- `OrderCreatedEvent` - New blood product orders (envelope pattern with UUID + Instant timestamps)
- 23 fields including orderNumber, externalId, orderStatus, orderItems[], transactionId

**Manufacturing Service** (`biopro-manufacturing/backend/apheresisplasma`):
- `ApheresisPlasmaProductCreatedEvent` - Manufactured plasma products (45+ fields!)
- Complex nested objects: Weight, Volume, InputProduct[], ProductStep[]
- ZonedDateTime with timezone fields

### ✅ Kubernetes-Native Deployment

- **Complete K8s manifests** for all services
- **Tiltfile** for local development (like existing BioPro projects)
- **Multi-stage Dockerfiles** for efficient builds
- **Namespace isolation** (`biopro-dlq`, `biopro-kafka`)
- **Service mesh ready** with proper labels

---

## 📋 Prerequisites

1. **Kubernetes Cluster**
   - Docker Desktop with Kubernetes enabled, OR
   - Minikube, OR
   - Kind (Kubernetes in Docker)

2. **Tilt Installed**
   ```bash
   # macOS
   brew install tilt

   # Windows (Scoop)
   scoop install tilt

   # Linux
   curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash
   ```

3. **kubectl Configured**
   ```bash
   kubectl cluster-info
   ```

4. **Docker Running**
   ```bash
   docker ps
   ```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Start Tilt

```bash
cd C:\Users\MelvinJones\work\event-governance\poc
tilt up
```

**What Happens**:
1. Tilt UI opens in browser (`http://localhost:10350`)
2. Infrastructure deploys (Zookeeper → Kafka → Schema Registry → Kafka UI)
3. Services build Docker images
4. Services deploy to Kubernetes
5. Port forwarding is configured automatically

### Step 2: Wait for Green

In the Tilt UI, wait for all resources to turn green (~2-3 minutes first time):

```
✅ zookeeper
✅ kafka
✅ schema-registry
✅ kafka-ui
✅ collections-service
✅ orders-service
✅ manufacturing-service
```

### Step 3: Verify Deployment

```bash
# Check all pods
kubectl get pods -n biopro-dlq
kubectl get pods -n biopro-kafka

# Check services
kubectl get svc -n biopro-dlq
kubectl get svc -n biopro-kafka
```

### Step 4: Access Services

**Service Endpoints**:
- Collections: http://localhost:8081
- Orders: http://localhost:8080
- Manufacturing: http://localhost:8082
- Kafka UI: http://localhost:8090

**Health Checks**:
```bash
curl http://localhost:8081/actuator/health  # Collections
curl http://localhost:8080/actuator/health  # Orders
curl http://localhost:8082/actuator/health  # Manufacturing
```

---

## 🏗️ Architecture

### Kubernetes Resources

```
Namespaces:
├── biopro-kafka (Infrastructure)
│   ├── zookeeper (StatefulSet)
│   ├── kafka (StatefulSet)
│   ├── schema-registry (Deployment)
│   └── kafka-ui (Deployment)
└── biopro-dlq (Application Services)
    ├── collections-service (Deployment + Service)
    ├── orders-service (Deployment + Service)
    └── manufacturing-service (Deployment + Service)
```

### Service Ports

| Service | Internal Port | External Port | Purpose |
|---------|--------------|---------------|---------|
| Collections | 8081 | 8081 | Collections API |
| Orders | 8080 | 8080 | Orders API |
| Manufacturing | 8082 | 8082 | Manufacturing API |
| Kafka | 9092 | 29092 | Kafka broker |
| Schema Registry | 8081 | 8081 | Schema management |
| Kafka UI | 8080 | 8090 | Kafka visualization |
| Zookeeper | 2181 | 2181 | Kafka coordination |

### Resource Limits

Each service pod:
- **Requests**: 256Mi memory, 250m CPU
- **Limits**: 512Mi memory, 500m CPU

Infrastructure pods use defaults (no limits for local dev).

---

## 📦 Testing with Real Schemas

### Collections Service

**Publish Collection Received Event**:

```bash
curl -X POST http://localhost:8081/api/collections/received \
  -H "Content-Type: application/json" \
  -d '{
    "unitNumber": "W036202412345",
    "status": "RECEIVED",
    "bagType": "CPDA-1",
    "drawTime": 1699027200000,
    "drawTimeZone": "America/New_York",
    "withdrawalTime": 1699030800000,
    "withdrawalTimeZone": "America/New_York",
    "donationType": "ALLOGENEIC",
    "procedureType": "WHOLE_BLOOD",
    "collectionLocation": "NYC-001",
    "aboRh": "OP",
    "volumes": [
      {
        "type": "WHOLE_BLOOD",
        "amount": 450,
        "excludeInCalculation": false
      },
      {
        "type": "ANTICOAGULANT",
        "amount": 63,
        "excludeInCalculation": false
      }
    ]
  }'
```

**Verify in Kafka UI**:
1. Go to http://localhost:8090
2. Click "Topics"
3. Find `biopro.collections.received`
4. View messages

### Orders Service

**Publish Order Created Event**:

```bash
curl -X POST http://localhost:8080/api/orders/created \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "550e8400-e29b-41d4-a716-446655440000",
    "occurredOn": 1699027200000,
    "payload": {
      "orderNumber": 12345,
      "orderStatus": "NEW",
      "locationCode": "NYC-001",
      "createDate": 1699027200000,
      "createDateTimeZone": "America/New_York",
      "priority": "ROUTINE",
      "transactionId": "650e8400-e29b-41d4-a716-446655440001",
      "orderItems": [
        {
          "productFamily": "RBC",
          "bloodType": "O_POSITIVE",
          "quantity": 2,
          "comments": "Urgent request"
        }
      ]
    }
  }'
```

### Manufacturing Service

**Publish Product Created Event**:

```bash
curl -X POST http://localhost:8082/api/manufacturing/product-created \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "750e8400-e29b-41d4-a716-446655440000",
    "occurredOn": 1699027200000,
    "occurredOnTimeZone": "America/New_York",
    "payload": {
      "unitNumber": "W036202412345",
      "productCode": "E086900",
      "productDescription": "PLASMA APHERESIS FFP",
      "productFamily": "PLASMA",
      "completionStage": "FINAL",
      "volume": {
        "value": 250,
        "unit": "MILLILITERS"
      },
      "drawTime": 1699027200000,
      "drawTimeZone": "America/New_York",
      "procedureType": "APHERESIS_PLASMA",
      "collectionLocation": "NYC-001",
      "aboRh": "OP",
      "createDate": 1699027200000,
      "createDateTimeZone": "America/New_York"
    }
  }'
```

---

## 🔧 Development Workflow

### Live Development with Tilt

1. **Edit Code**:
   ```bash
   # Edit any Java file
   vim biopro-demo-collections/src/main/java/...
   ```

2. **Tilt Auto-Rebuilds**:
   - Tilt watches for changes
   - Automatically rebuilds Docker image
   - Redeploys to Kubernetes
   - Shows progress in UI

3. **View Logs**:
   ```bash
   # In Tilt UI, click service name to see logs
   # Or use kubectl:
   kubectl logs -f -n biopro-dlq deployment/collections-service
   ```

### Manual Build and Deploy

```bash
# Build specific service
docker build -t local/biopro-collections:latest -f biopro-demo-collections/Dockerfile .

# Apply K8s manifests
kubectl apply -f k8s/collections/

# Force restart
kubectl rollout restart deployment/collections-service -n biopro-dlq
```

### Schema Updates

1. **Edit Avro Schema**:
   ```bash
   vim biopro-common-integration/src/main/resources/avro/CollectionReceivedEvent.avsc
   ```

2. **Rebuild to Generate Java Classes**:
   ```bash
   mvn clean compile
   ```

3. **Tilt Auto-Redeploys** with new schema

4. **Verify Schema in Registry**:
   ```bash
   curl http://localhost:8081/subjects/collections-received-value/versions/latest
   ```

---

## 📊 Monitoring and Observability

### Kafka UI

Access: http://localhost:8090

**Features**:
- Browse topics
- View messages
- Monitor consumer groups
- Inspect schemas
- See broker metrics

### Service Metrics

Each service exposes Prometheus metrics:

```bash
# Collections metrics
curl http://localhost:8081/actuator/metrics

# Specific metric
curl http://localhost:8081/actuator/metrics/biopro.dlq.events.total

# Prometheus format (for scraping)
curl http://localhost:8081/actuator/prometheus
```

### Kubernetes Dashboard (Optional)

```bash
# Install dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Create admin user
kubectl create serviceaccount dashboard-admin -n kubernetes-dashboard
kubectl create clusterrolebinding dashboard-admin --clusterrole=cluster-admin --serviceaccount=kubernetes-dashboard:dashboard-admin

# Get token
kubectl -n kubernetes-dashboard create token dashboard-admin

# Start proxy
kubectl proxy

# Access: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

---

## 🛠️ Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n biopro-dlq

# Describe pod for events
kubectl describe pod <pod-name> -n biopro-dlq

# Check logs
kubectl logs <pod-name> -n biopro-dlq

# Check previous container logs (if crashing)
kubectl logs <pod-name> -n biopro-dlq --previous
```

### Image Pull Errors

```bash
# Verify image exists
docker images | grep biopro

# Rebuild image
tilt trigger collections-service

# Check ImagePullPolicy
kubectl get deployment collections-service -n biopro-dlq -o yaml | grep imagePullPolicy
```

### Schema Registry Connection Issues

```bash
# Check Schema Registry is running
kubectl get pods -n biopro-kafka | grep schema-registry

# Check Schema Registry logs
kubectl logs -n biopro-kafka deployment/schema-registry

# Test from pod
kubectl exec -it -n biopro-dlq deployment/collections-service -- curl http://schema-registry.biopro-kafka.svc.cluster.local:8081/subjects
```

### Port Forwarding Issues

```bash
# Check Tilt port forwards
tilt describe collections-service

# Manual port forward
kubectl port-forward -n biopro-dlq deployment/collections-service 8081:8081
```

### Clean Restart

```bash
# Delete everything
tilt down

# Remove namespaces
kubectl delete namespace biopro-dlq biopro-kafka

# Restart
tilt up
```

---

## 🔒 Production Considerations

### Security

1. **Add Network Policies**:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: biopro-dlq-policy
     namespace: biopro-dlq
   spec:
     podSelector:
       matchLabels:
         app: collections
     policyTypes:
       - Ingress
       - Egress
     ingress:
       - from:
           - namespaceSelector:
               matchLabels:
                 name: biopro-dlq
   ```

2. **Add Pod Security Policies**
3. **Enable RBAC**
4. **Use Secrets for Sensitive Data**

### High Availability

1. **Increase Replicas**:
   ```yaml
   spec:
     replicas: 3  # Instead of 1
   ```

2. **Add Pod Disruption Budgets**:
   ```yaml
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata:
     name: collections-pdb
   spec:
     minAvailable: 2
     selector:
       matchLabels:
         app: collections
   ```

3. **Use StatefulSets for Kafka** (instead of Deployments)

### Resource Management

1. **Set appropriate limits based on load testing**
2. **Enable HorizontalPodAutoscaler**:
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: collections-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: collections-service
     minReplicas: 2
     maxReplicas: 10
     metrics:
       - type: Resource
         resource:
           name: cpu
           target:
             type: Utilization
             averageUtilization: 70
   ```

### Persistent Storage

For production Kafka and Schema Registry, add persistent volumes:

```yaml
volumeMounts:
  - name: kafka-data
    mountPath: /var/lib/kafka/data
volumes:
  - name: kafka-data
    persistentVolumeClaim:
      claimName: kafka-pvc
```

---

## 📚 Additional Resources

- **Schema Registration**: See [SCHEMA_REGISTRATION_GUIDE.md](SCHEMA_REGISTRATION_GUIDE.md)
- **Architecture Details**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Schema Analysis**: See [KAFKA_SCHEMAS_ANALYSIS.md](KAFKA_SCHEMAS_ANALYSIS.md)
- **Main Documentation**: See [README.md](README.md)

---

## ✅ Success Checklist

- [ ] Kubernetes cluster running
- [ ] Tilt installed and configured
- [ ] `tilt up` executed successfully
- [ ] All pods green in Tilt UI
- [ ] Kafka UI accessible (http://localhost:8090)
- [ ] Services health checks passing
- [ ] Test events published successfully
- [ ] Events visible in Kafka UI
- [ ] Schemas registered in Schema Registry

---

**Document Version**: 1.0
**Last Updated**: November 4, 2025
**Author**: Event Governance Team
**Status**: ✅ Production-Ready

**Ready for Demo!** 🎉
