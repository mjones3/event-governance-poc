# BioPro Event Governance & Interface Exception Collector
## Metrics Collection Briefing for IBM Consultants

**Date**: November 17, 2025
**Purpose**: Comprehensive inventory of all metrics collected across BioPro Event Governance Framework and Interface Exception Collector
**Audience**: IBM Consulting Team - Observability & Monitoring

---

## Table of Contents

1. [Event Governance Framework Metrics](#event-governance-framework-metrics)
2. [Interface Exception Collector Metrics](#interface-exception-collector-metrics)
3. [Metrics Export & Access](#metrics-export--access)
4. [Recommended Dashboards & Alerts](#recommended-dashboards--alerts)

---

# Event Governance Framework Metrics

**Services**: Orders, Collections, Manufacturing (3 microservices)
**Monitoring Stack**: Prometheus + Grafana

## 1. Custom BioPro Metrics

### 1.1 Dead Letter Queue (DLQ) Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `biopro.dlq.events.total` | Counter | Tracks total events routed to Dead Letter Queue | Tags: `module=orders`, `eventType=OrderCreatedEvent`, `errorType=SCHEMA_VALIDATION` |
| `biopro.dlq.reprocessing.success` | Counter | Successfully reprocessed events from DLQ | Tags: `module=manufacturing`, `eventType=PlasmaProductCreated` |
| `biopro.dlq.reprocessing.failure` | Counter | Failed DLQ reprocessing attempts | Tags: `module=collections`, `eventType=CollectionReceived`, `reason=INVALID_DATA` |
| `biopro.dlq.business.event` | Counter | Dynatrace business events for DLQ operations | Tags: `module=orders`, `eventType=OrderCreated`, `priority=CRITICAL`, `errorCategory=SCHEMA`, `environment=prod` |
| `biopro.dlq.reprocessing` | Counter | Generic DLQ reprocessing outcome tracking | Tags: `module=manufacturing`, `eventType=PlasmaProductUpdated`, `outcome=success` |

**Business Value**: Track event failures, identify poison messages, measure recovery success rates

---

### 1.2 Event Processing Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `biopro.event.processing.duration` | Timer | Measures end-to-end event processing time with percentiles (p50, p95, p99) | Tags: `module=orders`, `eventType=OrderCreated`<br>Example: p95=150ms, p99=300ms |

**Business Value**: Identify slow event processing, detect performance degradation, SLA monitoring

---

### 1.3 Schema Validation & Registry Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `biopro.schema.validation` | Counter | Schema validation success and failure rates | Tags: `module=orders`, `result=success`<br>Tags: `module=collections`, `result=failure` |
| `biopro.event.schema.version` | Counter | Events by schema version for evolution tracking | Tags: `module=manufacturing`, `eventType=PlasmaProductCreated`, `version=2.0` |
| `biopro.schema.operations` | Counter | Schema Registry operations (registration, validation, compatibility) | Tags: `module=orders`, `operation=register`, `result=success` |

**Business Value**: Monitor schema evolution adoption, detect breaking changes, track validation failures

---

### 1.4 Circuit Breaker Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `biopro.circuit.breaker.state` | Gauge | Current circuit breaker state | Value: `0` (CLOSED), `0.5` (HALF_OPEN), `1` (OPEN)<br>Tags: `circuit=schema-registry`, `state=OPEN` |

**Configuration**:
- Failure threshold: 50%
- Minimum calls: 10
- Wait duration (open): 1 minute
- Sliding window: 100 calls

**Business Value**: Prevent cascading failures, automatic recovery, dependency health monitoring

---

### 1.5 Retry Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `biopro.retry.attempts` | Counter | Retry attempts before DLQ routing | Tags: `module=orders`, `eventType=OrderCreated`, `attemptNumber=3` |

**Configuration**:
- Max attempts: 3
- Initial delay: 1 second
- Backoff: Exponential (1s → 2s → 4s)

**Business Value**: Track transient failures, measure retry effectiveness, identify persistent issues

---

## 2. Spring Boot Actuator Metrics (Auto-configured)

### 2.1 JVM Metrics

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| `jvm.memory.used` | Gauge | JVM memory usage by area | Value: `512MB` (heap.used) |
| `jvm.memory.max` | Gauge | Maximum JVM memory | Value: `2048MB` (heap.max) |
| `jvm.gc.pause` | Timer | Garbage collection pause time | p99=50ms |
| `jvm.threads.live` | Gauge | Live thread count | Value: `45` |
| `jvm.classes.loaded` | Gauge | Loaded class count | Value: `12543` |

**Business Value**: Memory leak detection, GC tuning, thread leak detection

---

### 2.2 System Metrics

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| `system.cpu.usage` | Gauge | System-wide CPU usage | Value: `0.65` (65%) |
| `system.cpu.count` | Gauge | Available CPU cores | Value: `8` |
| `process.cpu.usage` | Gauge | Application CPU usage | Value: `0.12` (12%) |
| `process.uptime` | Gauge | Application uptime in seconds | Value: `86400` (24 hours) |

**Business Value**: Resource utilization tracking, capacity planning

---

### 2.3 HTTP Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `http.server.requests` | Timer | HTTP request duration and count | Tags: `uri=/api/orders`, `method=POST`, `status=200`<br>p95=100ms, count=15000 |

**Business Value**: API performance monitoring, error rate tracking, endpoint usage analysis

---

## 3. Kafka Metrics (Auto-configured via Spring Kafka)

### 3.1 Producer Metrics

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| `kafka.producer.request.total` | Counter | Total producer requests | Value: `25000` |
| `kafka.producer.request.rate` | Gauge | Producer requests per second | Value: `150/sec` |
| `kafka.producer.record.send.total` | Counter | Total records sent | Value: `24950` |
| `kafka.producer.record.error.total` | Counter | Producer errors | Value: `50` |
| `kafka.producer.record.retry.total` | Counter | Producer retries | Value: `25` |
| `kafka.producer.request.latency.avg` | Gauge | Average request latency | Value: `15ms` |
| `kafka.producer.request.latency.max` | Gauge | Maximum request latency | Value: `250ms` |
| `kafka.producer.batch.size.avg` | Gauge | Average batch size | Value: `16KB` |

**Configuration**: ACKS=all, Retries=3, Idempotence=enabled

**Business Value**: Message delivery reliability, throughput monitoring, latency tracking

---

### 3.2 Consumer Metrics

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| `kafka.consumer.fetch.total` | Counter | Total fetch requests | Value: `12000` |
| `kafka.consumer.fetch.rate` | Gauge | Fetch requests per second | Value: `50/sec` |
| `kafka.consumer.records.consumed.total` | Counter | Total records consumed | Value: `24800` |
| `kafka.consumer.records.consumed.rate` | Gauge | Consumption rate | Value: `100/sec` |
| `kafka.consumer.fetch.latency.avg` | Gauge | Average fetch latency | Value: `25ms` |
| `kafka.consumer.records.lag` | Gauge | Consumer lag per partition | Value: `150` messages |
| `kafka.consumer.commit.total` | Counter | Total offset commits | Value: `2400` |

**Configuration**: Auto-offset-reset=earliest, Auto-commit=false (manual), Max-poll=100, Concurrency=3

**Business Value**: Consumer lag monitoring, throughput tracking, rebalance detection

---

## 4. Resilience4j Metrics (Auto-configured)

### 4.1 Circuit Breaker Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `resilience4j.circuitbreaker.calls` | Counter | Circuit breaker calls by outcome | Tags: `name=schema-registry`, `kind=successful`<br>Tags: `name=schema-registry`, `kind=failed` |
| `resilience4j.circuitbreaker.state` | Gauge | Current state (numeric) | Value: `0` (CLOSED), `1` (OPEN), `2` (HALF_OPEN) |
| `resilience4j.circuitbreaker.failure.rate` | Gauge | Failure rate percentage | Value: `0.15` (15%) |
| `resilience4j.circuitbreaker.buffered.calls` | Gauge | Buffered calls in sliding window | Value: `87/100` |

**Business Value**: Service dependency health, automatic failure isolation

---

### 4.2 Retry Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `resilience4j.retry.calls` | Counter | Retry calls by outcome | Tags: `name=kafka-producer`, `kind=successful_without_retry`<br>Tags: `name=kafka-producer`, `kind=successful_with_retry`<br>Tags: `name=kafka-producer`, `kind=failed_with_retry` |

**Business Value**: Retry effectiveness, transient failure detection

---

## 5. Schema Registry Metrics

### 5.1 Client-Side Cache Metrics

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| Caffeine Cache Stats | Various | In-memory schema cache performance | Hit rate: `95%`, Size: `84/1000`, Evictions: `12` |

**Configuration**: Max size=1000 schemas, TTL=1 minute (testing)

**Business Value**: Cache effectiveness, network call reduction

---

## 6. Metrics Export Configuration

### 6.1 Prometheus (Default - Local Development)

**Endpoints**:
- Orders Service: `http://localhost:8080/actuator/prometheus`
- Collections Service: `http://localhost:8081/actuator/prometheus`
- Manufacturing Service: `http://localhost:8082/actuator/prometheus`

**Scrape Configuration** (`prometheus.yml`):
```yaml
scrape_interval: 15s
jobs:
  - biopro-orders (port 8080)
  - biopro-collections (port 8081)
  - biopro-manufacturing (port 8082)
```

**Global Tags**:
- `application`: Service name (e.g., biopro-orders-service)
- `environment`: dev/staging/production
- `module`: orders/collections/manufacturing

---

### 6.2 Dynatrace (Production-Ready, Currently Disabled)

**Configuration** (`application.yml`):
```yaml
management.metrics.export.dynatrace:
  enabled: false  # Enable in production
  uri: ${DYNATRACE_URI}
  api-token: ${DYNATRACE_API_TOKEN}
  v2.metric-key-prefix: biopro
```

---

## 7. Pre-built Grafana Dashboard

**Dashboard**: `biopro-dlq-dashboard.json`
**Access**: http://localhost:3000

### Dashboard Panels

| Panel | Metric Query | Purpose |
|-------|-------------|---------|
| Total Successful Validations | `biopro_schema_validation_total{result="success"}` | Schema validation health |
| DLQ Events by Module | `rate(biopro_dlq_events_total[5m])` | DLQ traffic by service |
| Schema Validation Success Rate | `(success / total) * 100` | Validation effectiveness |
| Event Processing Duration (p95) | `histogram_quantile(0.95, biopro_event_processing_duration_bucket)` | Performance SLA tracking |
| Reprocessing Success vs Failure | Time series comparison | DLQ recovery rate |
| Circuit Breaker State | `biopro_circuit_breaker_state` | Dependency health |
| Retry Attempts | `rate(biopro_retry_attempts[5m])` | Transient failure rate |

---

# Interface Exception Collector Metrics

**Technology**: Spring Boot + GraphQL + RSocket

## 8. Custom Application Metrics

### 8.1 Exception Processing Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `exceptions.processed.total` | Counter | Total exceptions processed | Tags: `service=interface-exception-collector`<br>Value: `5423` |
| `exceptions.by.severity.total` | Counter | Exceptions by severity level | Tags: `service=interface-exception-collector`, `severity=CRITICAL`<br>Value: `145` |
| `exception.processing.duration` | Timer | Exception processing time | Tags: `service=interface-exception-collector`<br>p50=50ms, p95=200ms, p99=500ms |

**Business Value**: Exception volume tracking, severity distribution, processing performance

---

### 8.2 Retry Operation Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `retry.operations.total` | Counter | Total retry operations attempted | Tags: `service=interface-exception-collector`<br>Value: `1250` |
| `retry.success.total` | Counter | Successful retry operations | Tags: `service=interface-exception-collector`<br>Value: `1100` |
| `retry.failure.total` | Counter | Failed retry operations | Tags: `service=interface-exception-collector`<br>Value: `150` |
| `retry.operation.duration` | Timer | Retry operation duration | Tags: `service=interface-exception-collector`, `interfaceType=REST`, `success=true`<br>p95=1500ms |

**Business Value**: Retry effectiveness (88% success rate), identify problematic interfaces

---

### 8.3 Alert Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `alerts.critical.total` | Counter | Critical alerts generated | Tags: `service=interface-exception-collector`<br>Value: `23` |

**Business Value**: Critical issue tracking, alerting effectiveness

---

### 8.4 API Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `api.response.duration` | Timer | REST API endpoint response times | Tags: `service=interface-exception-collector`, `endpoint=/api/exceptions`, `method=GET`, `statusCode=200`<br>p50=45ms, p95=150ms, p99=350ms |

**Business Value**: API performance monitoring, SLA compliance

---

### 8.5 Database Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `database.operations.total` | Counter | Total database operations | Tags: `service=interface-exception-collector`, `operation=findAllExceptions`, `success=true`<br>Value: `8542` |
| `database.operation.duration` | Timer | Database operation execution time | Tags: `service=interface-exception-collector`, `operation=saveException`<br>p50=15ms, p95=75ms, p99=200ms |

**Business Value**: Database performance monitoring, slow query detection

---

### 8.6 Kafka Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `kafka.messages.consumed.total` | Counter | Total Kafka messages consumed | Tags: `service=interface-exception-collector`, `topic=exception-events`, `success=true`<br>Value: `12450` |
| `kafka.messages.produced.total` | Counter | Total Kafka messages produced | Tags: `service=interface-exception-collector`, `topic=exception-alerts`, `success=true`<br>Value: `12400` |

**Business Value**: Message flow tracking, error rate monitoring

---

### 8.7 External Service Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `external.service.call.duration` | Timer | External service call duration | Tags: `service=interface-exception-collector`, `serviceName=notification-service`, `success=true`<br>p50=100ms, p95=500ms, p99=1200ms |

**Business Value**: External dependency performance, timeout detection

---

## 9. GraphQL Metrics

### 9.1 Query Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_query_count_total` | Counter | Total GraphQL queries executed | Tags: `operation=getExceptionById`, `operationType=query`, `status=success`<br>Value: `3542` |
| `graphql_query_duration_seconds` | Timer | GraphQL query execution duration | Tags: `operation=listExceptions`, `operationType=query`, `status=success`<br>p50=0.085s, p95=0.250s, p99=0.650s |

**Business Value**: Query performance monitoring, usage analytics

---

### 9.2 Mutation Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_mutation_count_total` | Counter | Total GraphQL mutations executed | Tags: `operation=updateException`, `operationType=mutation`, `status=success`<br>Value: `845` |
| `graphql_mutation_duration_seconds` | Timer | GraphQL mutation execution duration | Tags: `operation=createException`, `operationType=mutation`<br>p50=0.120s, p95=0.450s, p99=1.200s |

**Business Value**: Mutation performance, write operation tracking

---

### 9.3 Subscription Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_subscription_count_total` | Counter | Total GraphQL subscriptions initiated | Tags: `operation=exceptionUpdates`, `operationType=subscription`<br>Value: `234` |
| `graphql_subscription_duration_seconds` | Timer | GraphQL subscription execution duration | Tags: `operation=exceptionUpdates`, `operationType=subscription`<br>p95=0.050s |
| `graphql_subscription_connections_active` | Gauge | Active GraphQL subscription connections | Value: `42` connections |

**Business Value**: Real-time connection monitoring, WebSocket health

---

### 9.4 Field Resolution Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_field_fetch_duration_seconds` | Timer | GraphQL field resolver execution time | Tags: `field=severity`, `parentType=Exception`, `status=success`<br>p99=0.015s |

**Business Value**: N+1 query detection, resolver performance optimization

---

### 9.5 GraphQL Error Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_error_count_total` | Counter | Total GraphQL errors | Tags: `errorType=ValidationError`<br>Value: `127` |

**Business Value**: Error rate tracking, error pattern analysis

---

### 9.6 GraphQL Cache Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_cache_access_total` | Counter | GraphQL cache access count | Tags: `cacheName=exceptionCache`, `hit=true`<br>Value: `2845` (hits)<br>Tags: `cacheName=exceptionCache`, `hit=false`<br>Value: `324` (misses) |

**Business Value**: Cache effectiveness (89.8% hit rate), performance optimization

---

### 9.7 GraphQL DataLoader Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_dataloader_batch_total` | Counter | Total DataLoader batch operations | Tags: `loaderName=exceptionLoader`<br>Value: `542` |
| `graphql_dataloader_batch_seconds` | Timer | DataLoader batch execution duration | Tags: `loaderName=exceptionLoader`<br>p95=0.125s |

**Business Value**: Batch loading efficiency, N+1 query prevention

---

### 9.8 GraphQL Business Metrics (Dynamic)

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_business_{metricName}_duration_seconds` | Timer | Custom business operation timing | Example: `graphql_business_exception_resolution_duration_seconds`<br>p95=2.5s |
| `graphql_business_{metricName}_total` | Counter | Custom business operation count | Example: `graphql_business_exception_escalations_total`<br>Value: `45` |

**Business Value**: Business-specific KPI tracking, custom workflow monitoring

---

## 10. GraphQL Subscription Detailed Metrics

### 10.1 Connection Lifecycle Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_subscription_connections_total` | Counter | Total subscription connections established | Tags: `subscriptionType=exceptionUpdates`<br>Value: `1245` |
| `graphql_subscription_disconnections_total` | Counter | Total subscription disconnections | Tags: `subscriptionType=exceptionUpdates`<br>Value: `1203` |
| `graphql_subscription_connection_duration_seconds` | Timer | Subscription connection lifetime | Tags: `subscriptionType=exceptionUpdates`<br>Average: `450s` (7.5 min) |

**Business Value**: Connection churn analysis, user engagement tracking

---

### 10.2 Subscription Message Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_subscription_messages_sent_total` | Counter | Total subscription messages sent | Tags: `operation=exceptionUpdates`<br>Value: `18542` |
| `graphql_subscription_messages_failed_total` | Counter | Failed subscription message deliveries | Tags: `operation=exceptionUpdates`, `errorType=CLIENT_DISCONNECTED`<br>Value: `127` |
| `graphql_subscription_message_delivery_seconds` | Timer | Message delivery latency | Tags: `operation=exceptionUpdates`<br>p95=0.025s |

**Business Value**: Message delivery reliability (99.3% success), real-time latency monitoring

---

### 10.3 Subscription Lifecycle Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_subscription_started_total` | Counter | Total subscriptions started | Tags: `operation=exceptionUpdates`, `subscriptionType=EXCEPTION_UPDATES`<br>Value: `1245` |
| `graphql_subscription_stopped_total` | Counter | Total subscriptions stopped | Tags: `operation=exceptionUpdates`, `subscriptionType=EXCEPTION_UPDATES`<br>Value: `1203` |
| `graphql_subscription_lifetime_seconds` | Timer | Subscription lifetime duration | Tags: `operation=exceptionUpdates`<br>p50=300s, p95=1200s |

**Business Value**: Subscription usage patterns, engagement duration

---

### 10.4 Subscription Event Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_subscription_event_processing_seconds` | Timer | Subscription event processing time | Tags: `eventType=EXCEPTION_UPDATED`<br>p95=0.045s |
| `graphql_subscription_events_filtered_total` | Counter | Subscription events filtered out | Tags: `eventType=EXCEPTION_UPDATED`, `reason=NO_SUBSCRIBERS`<br>Value: `3241` |
| `graphql_subscription_latency_seconds` | Timer | End-to-end event latency | Tags: `operation=exceptionUpdates`<br>p95=0.085s (event generation → client delivery) |

**Business Value**: Real-time performance, filter effectiveness

---

### 10.5 Subscription Capacity Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `graphql_subscription_buffer_utilization_percent` | Gauge | Subscription buffer utilization | Value: `4.2%` (42 active / 1000 max connections) |

**Business Value**: Capacity planning, scalability monitoring

---

## 11. RSocket Metrics

### 11.1 RSocket Call Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `rsocket.calls.total` | Counter | Total RSocket calls to mock server | Tags: `service=mock-rsocket-server`, `client=interface-exception-collector`<br>Value: `8542` |
| `rsocket.calls.success` | Counter | Successful RSocket calls | Tags: `service=mock-rsocket-server`, `operation=getExceptionData`<br>Value: `8450` |
| `rsocket.calls.failure` | Counter | Failed RSocket calls | Tags: `service=mock-rsocket-server`, `operation=getExceptionData`<br>Value: `92` |
| `rsocket.call.duration` | Timer | RSocket call duration | Tags: `service=mock-rsocket-server`, `operation=getExceptionData`<br>p50=25ms, p95=100ms, p99=250ms |

**Business Value**: RSocket performance monitoring, success rate tracking (98.9%)

---

### 11.2 RSocket Error Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `rsocket.errors.total` | Counter | RSocket errors by type | Tags: `service=mock-rsocket-server`, `errorType=CONNECTION_ERROR`, `operation=getExceptionData`<br>Value: `45` |
| `rsocket.timeouts.total` | Counter | RSocket call timeouts | Tags: `service=mock-rsocket-server`, `operation=getExceptionData`<br>Value: `23` |

**Business Value**: Error pattern analysis, timeout tuning

---

### 11.3 RSocket Resilience Metrics

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `rsocket.circuit_breaker.events` | Counter | Circuit breaker events for RSocket | Tags: `service=mock-rsocket-server`, `eventType=open`, `operation=getExceptionData`<br>Value: `3` |

**Business Value**: RSocket dependency health, automatic failure isolation

---

## 12. GraphQL Alerting Threshold Metrics

### 12.1 Threshold Configuration Gauges

| Metric Name | Type | Purpose | Example Value |
|-------------|------|---------|---------------|
| `graphql_alert_threshold_query_response_time_ms` | Gauge | Alert threshold for query response time | Value: `500ms` |
| `graphql_alert_threshold_mutation_response_time_ms` | Gauge | Alert threshold for mutation response time | Value: `3000ms` |
| `graphql_alert_threshold_field_fetch_time_ms` | Gauge | Alert threshold for field fetch time | Value: `100ms` |
| `graphql_alert_threshold_error_rate_percent` | Gauge | Alert threshold for error rate | Value: `5%` |
| `graphql_alert_threshold_cache_miss_rate_percent` | Gauge | Alert threshold for cache miss rate | Value: `20%` |
| `graphql_alert_threshold_max_concurrent_queries` | Gauge | Alert threshold for concurrent queries | Value: `100` |
| `graphql_alert_threshold_max_subscription_connections` | Gauge | Alert threshold for subscription connections | Value: `1000` |

**Business Value**: Dynamic alerting configuration, SLA threshold visibility

---

## 13. HikariCP Connection Pool Metrics

### 13.1 Connection Pool Metrics

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| `hikari.connections.active` | Gauge | Active database connections | Value: `8` |
| `hikari.connections.idle` | Gauge | Idle connections in pool | Value: `12` |
| `hikari.connections.pending` | Gauge | Pending connection requests | Value: `0` |
| `hikari.connections.max` | Gauge | Maximum pool size | Value: `50` |
| `hikari.connections.min` | Gauge | Minimum pool size | Value: `10` |
| `hikari.connections.usage` | Timer | Connection usage time | p95=250ms |
| `hikari.connections.timeout` | Counter | Connection timeout count | Value: `3` |
| `hikari.connections.creation` | Timer | Connection creation time | p95=45ms |

**Business Value**: Connection pool health, resource utilization, timeout detection

---

## 14. Hibernate/JPA Metrics

### 14.1 Hibernate Statistics

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| `hibernate.sessions.open` | Gauge | Open Hibernate sessions | Value: `12` |
| `hibernate.sessions.closed` | Gauge | Closed sessions | Value: `8542` |
| `hibernate.transactions` | Counter | Transaction count | Value: `8420` |
| `hibernate.query.executions` | Counter | Query execution count | Value: `42540` |
| `hibernate.cache.puts` | Counter | Second-level cache puts | Value: `2450` |
| `hibernate.cache.hits` | Counter | Second-level cache hits | Value: `18542` |
| `hibernate.cache.misses` | Counter | Second-level cache misses | Value: `3245` |
| `hibernate.entity.loads` | Counter | Entity load operations | Value: `21787` |
| `hibernate.entity.inserts` | Counter | Entity insert operations | Value: `1245` |
| `hibernate.entity.updates` | Counter | Entity update operations | Value: `3542` |
| `hibernate.entity.deletes` | Counter | Entity delete operations | Value: `234` |

**Business Value**: ORM performance, cache effectiveness (85.1% hit rate), query optimization

---

## 15. Interface Exception Collector - Kafka Metrics

### 15.1 Consumer Metrics (Auto-configured)

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| `kafka.consumer.fetch.manager.records.consumed.total` | Counter | Total records consumed | Value: `12450` |
| `kafka.consumer.fetch.manager.fetch.latency.avg` | Gauge | Average fetch latency | Value: `28ms` |
| `kafka.consumer.fetch.manager.fetch.latency.max` | Gauge | Maximum fetch latency | Value: `450ms` |
| `kafka.consumer.coordinator.commit.latency.avg` | Gauge | Average commit latency | Value: `15ms` |
| `kafka.consumer.coordinator.commit.latency.max` | Gauge | Maximum commit latency | Value: `120ms` |

---

### 15.2 Producer Metrics (Auto-configured)

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| `kafka.producer.record.send.total` | Counter | Total records sent | Value: `12400` |
| `kafka.producer.record.error.total` | Counter | Producer errors | Value: `18` |
| `kafka.producer.record.retry.total` | Counter | Producer retries | Value: `12` |
| `kafka.producer.request.latency.avg` | Gauge | Average request latency | Value: `22ms` |
| `kafka.producer.request.latency.max` | Gauge | Maximum request latency | Value: `350ms` |

**Business Value**: Message reliability, throughput monitoring, latency tracking

---

## 16. Interface Exception Collector - Resilience4j Metrics

### 16.1 Circuit Breaker (source-service, mock-rsocket-server)

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `resilience4j.circuitbreaker.state` | Gauge | Circuit breaker state | Value: `0` (CLOSED)<br>Tags: `name=source-service` |
| `resilience4j.circuitbreaker.calls` | Counter | Calls by state | Tags: `name=mock-rsocket-server`, `state=successful`<br>Value: `8450` |
| `resilience4j.circuitbreaker.failure.rate` | Gauge | Failure rate | Value: `0.011` (1.1%)<br>Tags: `name=source-service` |
| `resilience4j.circuitbreaker.slow.call.rate` | Gauge | Slow call rate | Value: `0.023` (2.3%)<br>Tags: `name=mock-rsocket-server` |

---

### 16.2 Retry (source-service, mock-rsocket-server)

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `resilience4j.retry.calls.successful.with.retry` | Counter | Successful after retry | Tags: `name=source-service`<br>Value: `45` |
| `resilience4j.retry.calls.successful.without.retry` | Counter | Successful without retry | Tags: `name=source-service`<br>Value: `8405` |
| `resilience4j.retry.calls.failed.with.retry` | Counter | Failed after retry | Tags: `name=source-service`<br>Value: `12` |

---

### 16.3 Time Limiter (source-service, mock-rsocket-server)

| Metric Name | Type | Purpose | Example/Tags |
|-------------|------|---------|--------------|
| `resilience4j.timelimiter.calls.successful` | Counter | Successful within timeout | Tags: `name=mock-rsocket-server`<br>Value: `8427` |
| `resilience4j.timelimiter.calls.timeout` | Counter | Timed out calls | Tags: `name=mock-rsocket-server`<br>Value: `23` |

**Business Value**: Dependency resilience, timeout tuning, automatic recovery tracking

---

## 17. Health Indicator Metrics

### 17.1 Custom GraphQL Health Metrics

| Metric Name | Type | Purpose | Example |
|-------------|------|---------|---------|
| `graphql_health_database_response_time_ms` | Gauge | Database health check response time | Value: `12ms` |
| `graphql_health_cache_response_time_ms` | Gauge | Cache health check response time | Value: `3ms` |

**Business Value**: Component health monitoring, dependency status

---

# Metrics Export & Access

## Event Governance Framework

### Prometheus Endpoints
- **Orders Service**: `http://localhost:8080/actuator/prometheus`
- **Collections Service**: `http://localhost:8081/actuator/prometheus`
- **Manufacturing Service**: `http://localhost:8082/actuator/prometheus`

### Prometheus Server
- **URL**: `http://localhost:9090`
- **Scrape Interval**: 15 seconds
- **Jobs**: biopro-orders, biopro-collections, biopro-manufacturing

### Grafana
- **URL**: `http://localhost:3000`
- **Pre-built Dashboard**: BioPro DLQ Metrics (`biopro-dlq-dashboard.json`)
- **Auth**: Anonymous (Admin role)

---

## Interface Exception Collector

### Prometheus Endpoint
- **URL**: `http://localhost:{port}/actuator/prometheus`
- **Scrape Interval**: 10 seconds (configurable)

### Additional Endpoints
- **Health**: `/actuator/health`
- **Metrics**: `/actuator/metrics`
- **GraphQL Health**: `/actuator/graphql-health`

### Metric Export Configuration
```yaml
management.metrics.export.prometheus:
  enabled: true
  step: 10s
  descriptions: true
```

---

# Recommended Dashboards & Alerts

## Event Governance Framework - Recommended Alerts

| Alert Name | Condition | Severity | Purpose |
|------------|-----------|----------|---------|
| High DLQ Rate | `rate(biopro_dlq_events_total[5m]) > 10` | CRITICAL | Detect event processing failures |
| Schema Validation Failures | `rate(biopro_schema_validation_total{result="failure"}[5m]) > 5` | HIGH | Breaking schema changes |
| Circuit Breaker Open | `biopro_circuit_breaker_state == 1` | CRITICAL | Dependency failure |
| High Consumer Lag | `kafka_consumer_records_lag > 1000` | HIGH | Consumer performance degradation |
| Event Processing Slow (p95) | `histogram_quantile(0.95, biopro_event_processing_duration_bucket) > 1` | MEDIUM | Performance SLA breach |
| Retry Exhaustion | `rate(biopro_retry_attempts{attemptNumber="3"}[5m]) > 5` | HIGH | Persistent failures |

---

## Interface Exception Collector - Recommended Alerts

| Alert Name | Condition | Severity | Purpose |
|------------|-----------|----------|---------|
| High GraphQL Error Rate | `(rate(graphql_error_count_total[5m]) / rate(graphql_query_count_total[5m])) > 0.05` | HIGH | GraphQL error threshold breach (5%) |
| Slow GraphQL Queries | `histogram_quantile(0.95, graphql_query_duration_seconds_bucket) > 0.5` | MEDIUM | Query performance SLA breach (500ms) |
| Slow GraphQL Mutations | `histogram_quantile(0.95, graphql_mutation_duration_seconds_bucket) > 3` | MEDIUM | Mutation performance SLA breach (3s) |
| High Active Subscriptions | `graphql_subscription_connections_active > 900` | MEDIUM | Approaching capacity (1000 max) |
| Subscription Message Failures | `rate(graphql_subscription_messages_failed_total[5m]) > 10` | HIGH | Subscription delivery issues |
| High Exception Processing Volume | `rate(exceptions.by.severity.total{severity="CRITICAL"}[5m]) > 5` | CRITICAL | Critical exception spike |
| Low Retry Success Rate | `(retry.success.total / (retry.success.total + retry.failure.total)) < 0.7` | HIGH | Retry effectiveness below 70% |
| Database Connection Pool Exhaustion | `hikari.connections.pending > 0` | CRITICAL | Connection pool saturation |
| RSocket Circuit Breaker Open | `rsocket_circuit_breaker_events{eventType="open"} > 0` | HIGH | RSocket dependency failure |
| High Cache Miss Rate | `(graphql_cache_access_total{hit="false"} / sum(graphql_cache_access_total)) > 0.2` | MEDIUM | Cache effectiveness below 80% |

---

## Recommended Dashboard Panels

### Event Governance Framework
1. **DLQ Overview**: Total DLQ events, reprocessing success rate, error distribution by module
2. **Schema Registry**: Validation success rate, schema versions in use, registry operations
3. **Event Processing**: Processing duration (p50/p95/p99), throughput by event type
4. **Kafka Health**: Consumer lag, producer throughput, error rates
5. **Resilience**: Circuit breaker states, retry attempts, failure rates
6. **JVM Health**: Memory usage, GC pause time, thread count

### Interface Exception Collector
1. **Exception Overview**: Total exceptions by severity, processing duration, retry success rate
2. **GraphQL Performance**: Query/mutation/subscription duration (p50/p95/p99), error rate
3. **GraphQL Subscriptions**: Active connections, message delivery latency, event processing time
4. **API Performance**: REST endpoint response times, request volume, error rates
5. **Database Health**: Connection pool utilization, query execution time, cache hit rate
6. **RSocket Health**: Call success rate, duration, circuit breaker state
7. **Kafka Integration**: Message consumption/production rates, error counts
8. **JVM & Resources**: Memory usage, GC activity, CPU usage, thread count

---

## Metric Tag Strategy

### Common Tags (Both Applications)
- `application`: Application name
- `environment`: dev/staging/production
- `version`: Application version (from build)

### Event Governance Tags
- `module`: orders/collections/manufacturing
- `eventType`: Specific event type (e.g., OrderCreatedEvent)
- `errorType`: Error classification (e.g., SCHEMA_VALIDATION)
- `result`: success/failure

### Interface Exception Collector Tags
- `service`: interface-exception-collector-service
- `operation`: Specific operation name
- `severity`: CRITICAL/HIGH/MEDIUM/LOW
- `interfaceType`: Type of interface (REST/RSOCKET/GRAPHQL)
- `statusCode`: HTTP status code
- `errorType`: Error classification

---

## Summary Statistics

### Event Governance Framework
- **Total Metric Categories**: 7 (Custom BioPro, Actuator, Kafka, Resilience4j, Schema Registry, Prometheus, Dynatrace)
- **Custom Metrics**: 11
- **Auto-configured Metrics**: 50+
- **Total Metrics**: 60+
- **Services Monitored**: 3 (Orders, Collections, Manufacturing)
- **Grafana Dashboards**: 1 pre-built

### Interface Exception Collector
- **Total Metric Categories**: 10 (Application, GraphQL, Subscriptions, RSocket, Actuator, HikariCP, Hibernate, Kafka, Resilience4j, Health)
- **Custom Metrics**: 60+
- **Auto-configured Metrics**: 40+
- **Total Metrics**: 100+
- **Services Monitored**: 1 (Interface Exception Collector)

---

## Key Performance Indicators (KPIs)

### Event Governance Framework
1. **DLQ Rate**: < 1% of total events
2. **Schema Validation Success Rate**: > 99%
3. **Event Processing p95**: < 500ms
4. **Consumer Lag**: < 100 messages
5. **Retry Success Rate**: > 80%
6. **Circuit Breaker Uptime**: > 99.9%

### Interface Exception Collector
1. **GraphQL Query p95**: < 500ms
2. **GraphQL Mutation p95**: < 3s
3. **GraphQL Error Rate**: < 5%
4. **Exception Retry Success Rate**: > 70%
5. **Cache Hit Rate**: > 80%
6. **Database Connection Pool Utilization**: < 80%
7. **Active Subscription Connections**: < 900
8. **RSocket Call Success Rate**: > 95%
