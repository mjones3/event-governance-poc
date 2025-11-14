# -*- mode: Python -*-
# BioPro Event Governance Framework - Tiltfile
# Local Kubernetes Development Environment

# Load extensions
load('ext://namespace', 'namespace_create', 'namespace_inject')

# Print startup message
print("""
╔══════════════════════════════════════════════════════════════════════════╗
║ BioPro Event Governance Framework - Local K8s Environment                ║
║                                                                            ║
║ Services:                                                                  ║
║  - Collections  (port 8081) - http://localhost:8081                      ║
║  - Orders       (port 8080) - http://localhost:8080                      ║
║  - Manufacturing (port 8082) - http://localhost:8082                      ║
║                                                                            ║
║ Infrastructure:                                                            ║
║  - Kafka UI     (port 8090) - http://localhost:8090                      ║
║  - Schema Registry (port 8081) - http://localhost:8081                   ║
║  - Prometheus   (port 9090) - http://localhost:9090                      ║
║  - Grafana      (port 3000) - http://localhost:3000                      ║
║                                                                            ║
║ Metrics:                                                                   ║
║  - Prometheus endpoint: /actuator/prometheus                              ║
║  - Custom BioPro metrics with biopro.* prefix                             ║
║                                                                            ║
║ Tip: Run 'tilt up' to start all services                                  ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

# Create namespaces
def create_namespaces():
    k8s_yaml('k8s/common/namespace.yaml')

# Deploy Kafka infrastructure
def deploy_kafka_infrastructure():
    print("📦 Deploying Kafka infrastructure...")

    # Zookeeper
    k8s_yaml('k8s/common/zookeeper.yaml')
    k8s_resource(
        'zookeeper',
        port_forwards='2181:2181',
        labels=['infrastructure']
    )

    # Kafka
    k8s_yaml('k8s/common/kafka.yaml')
    k8s_resource(
        'kafka',
        port_forwards='29092:29092',
        resource_deps=['zookeeper'],
        labels=['infrastructure']
    )

    # Schema Registry
    k8s_yaml('k8s/common/schema-registry.yaml')
    k8s_resource(
        'schema-registry',
        port_forwards='8081:8081',
        resource_deps=['kafka'],
        labels=['infrastructure']
    )

    # Kafka UI
    k8s_yaml('k8s/common/kafka-ui.yaml')
    k8s_resource(
        'kafka-ui',
        port_forwards='8090:8080',
        resource_deps=['kafka', 'schema-registry'],
        labels=['infrastructure']
    )

    # Prometheus
    k8s_yaml('k8s/common/prometheus.yaml')
    k8s_resource(
        'prometheus',
        port_forwards='9090:9090',
        labels=['monitoring']
    )

    # Grafana
    k8s_yaml('k8s/common/grafana.yaml')
    k8s_yaml('k8s/common/grafana-dashboard.yaml')
    k8s_resource(
        'grafana',
        port_forwards='3000:3000',
        resource_deps=['prometheus'],
        labels=['monitoring']
    )

# Build and deploy Collections service
def deploy_collections_service():
    print("🩸 Building Collections service...")

    # Build Docker image
    docker_build(
        'local/biopro-collections',
        context='.',
        dockerfile='biopro-demo-collections/Dockerfile',
        only=[
            'biopro-common-core/',
            'biopro-common-config/',
            'biopro-common-integration/',
            'biopro-common-security/',
            'biopro-common-monitoring/',
            'biopro-dlq-spring-boot-starter/',
            'biopro-demo-collections/',
            'pom.xml'
        ]
    )

    # Deploy to K8s
    k8s_yaml('k8s/collections/deployment.yaml')
    k8s_yaml('k8s/collections/service.yaml')
    k8s_resource(
        'collections-service',
        port_forwards='8081:8081',
        resource_deps=['kafka', 'schema-registry'],
        labels=['services']
    )

# Build and deploy Orders service
def deploy_orders_service():
    print("📦 Building Orders service...")

    # Build Docker image
    docker_build(
        'local/biopro-orders',
        context='.',
        dockerfile='biopro-demo-orders/Dockerfile',
        only=[
            'biopro-common-core/',
            'biopro-common-config/',
            'biopro-common-integration/',
            'biopro-common-security/',
            'biopro-common-monitoring/',
            'biopro-dlq-spring-boot-starter/',
            'biopro-demo-orders/',
            'pom.xml'
        ]
    )

    # Deploy to K8s
    k8s_yaml('k8s/orders/deployment.yaml')
    k8s_yaml('k8s/orders/service.yaml')
    k8s_resource(
        'orders-service',
        port_forwards='8080:8080',
        resource_deps=['kafka', 'schema-registry'],
        labels=['services']
    )

# Build and deploy Manufacturing service
def deploy_manufacturing_service():
    print("🏭 Building Manufacturing service...")

    # Build Docker image
    docker_build(
        'local/biopro-manufacturing',
        context='.',
        dockerfile='biopro-demo-manufacturing/Dockerfile',
        only=[
            'biopro-common-core/',
            'biopro-common-config/',
            'biopro-common-integration/',
            'biopro-common-security/',
            'biopro-common-monitoring/',
            'biopro-dlq-spring-boot-starter/',
            'biopro-demo-manufacturing/',
            'pom.xml'
        ]
    )

    # Deploy to K8s
    k8s_yaml('k8s/manufacturing/deployment.yaml')
    k8s_yaml('k8s/manufacturing/service.yaml')
    k8s_resource(
        'manufacturing-service',
        port_forwards='8082:8082',
        resource_deps=['kafka', 'schema-registry'],
        labels=['services']
    )

# Execute deployment
create_namespaces()
deploy_kafka_infrastructure()
deploy_collections_service()
deploy_orders_service()
deploy_manufacturing_service()

print("""
✅ Tilt configuration loaded successfully!

🚀 Starting services... This will take 2-3 minutes for first-time setup.

📝 Next steps:
  1. Wait for all services to turn green in the Tilt UI
  2. Visit http://localhost:8090 to view Kafka UI
  3. Visit http://localhost:3000 to view Grafana (BioPro dashboards pre-loaded)
  4. Visit http://localhost:9090 to view Prometheus
  5. Test the services:
     - Collections: curl http://localhost:8081/actuator/health
     - Orders: curl http://localhost:8080/actuator/health
     - Manufacturing: curl http://localhost:8082/actuator/health
  6. Check Prometheus metrics:
     - curl http://localhost:8080/actuator/prometheus
     - curl http://localhost:8081/actuator/prometheus
     - curl http://localhost:8082/actuator/prometheus

📊 Monitoring configured: PROMETHEUS (local dev)
   Switch to Dynatrace: Set biopro.monitoring.type=dynatrace in application.yml

📖 For more details, see README.md
""")
