# BioPro Event Governance Framework - Changelog

## Version 1.1.0 - Architecture Simplification

### Changes Made

#### 1. Removed Redis Caching Layer
**Rationale**: Schema Registry has built-in caching. Redis added unnecessary complexity.

**Changes**:
- Removed `redis` service from `docker-compose.yml`
- Removed `spring-boot-starter-data-redis` dependency from `biopro-common-integration`
- Simplified `SchemaRegistryService` to use only in-memory Caffeine cache
- Updated documentation to reflect single-layer caching strategy

**Benefits**:
- Simpler infrastructure (one less service to manage)
- Faster startup time
- Lower resource footprint
- Easier development setup

#### 2. Switched from Prometheus to Dynatrace
**Rationale**: Enterprise monitoring with Dynatrace provides better observability and custom business metrics.

**Changes**:
- Replaced `micrometer-registry-prometheus` with `micrometer-registry-dynatrace`
- Added `DynatraceCustomMetricsService` for custom statistics
- Updated all `application.yml` configurations to use Dynatrace
- Removed Prometheus actuator endpoint exposure

**New Features**:
- Custom business events for DLQ operations
- Dynatrace-native metric dimensions (tags)
- Circuit breaker state monitoring
- Retry attempt tracking
- Reprocessing outcome metrics

**Configuration** (in `application.yml`):
```yaml
management:
  metrics:
    export:
      dynatrace:
        enabled: true
        uri: http://localhost:14499/metrics/ingest  # OneAgent endpoint
        api-token: ${DYNATRACE_API_TOKEN}  # Set via environment variable
        v2:
          metric-key-prefix: biopro
    tags:
      application: ${spring.application.name}
      environment: ${ENV}
      module: ${MODULE_NAME}
```

### Updated Architecture

**Before**:
```
Application → L1 Cache (Caffeine) → L2 Cache (Redis) → Schema Registry
Application → Metrics → Prometheus → Grafana
```

**After**:
```
Application → In-Memory Cache (Caffeine) → Schema Registry
Application → Metrics → Dynatrace
```

### Migration Guide

#### For Existing Deployments:

1. **Update Docker Compose**:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```
   Note: Redis service will no longer start

2. **Update Application Configuration**:
   - Remove any Redis configuration
   - Add Dynatrace configuration (see above)
   - Set `DYNATRACE_API_TOKEN` environment variable

3. **Update Dependencies**:
   ```bash
   mvn clean install
   ```

#### For New Deployments:

Simply follow the updated Quick Start guide - no additional configuration needed!

### Metrics Available in Dynatrace

All metrics now published to Dynatrace with `biopro.` prefix:

| Metric | Description | Dimensions |
|--------|-------------|------------|
| `biopro.dlq.events.total` | Total DLQ events | module, eventType, errorType |
| `biopro.dlq.business.event` | Business events | module, eventType, priority, errorCategory |
| `biopro.event.processing.duration` | Processing time | module, eventType |
| `biopro.schema.operations` | Schema operations | module, operation, result |
| `biopro.circuit.breaker.state` | Circuit breaker state | circuit, state |
| `biopro.retry.attempts` | Retry attempts | module, eventType, attemptNumber |
| `biopro.dlq.reprocessing` | Reprocessing outcomes | module, eventType, outcome |

### Breaking Changes

⚠️ **Breaking Changes**:
1. Redis dependency removed - applications using Redis for other purposes will need to add it back explicitly
2. Prometheus endpoint removed - monitoring tools expecting `/actuator/prometheus` need to switch to Dynatrace
3. Metric export configuration changed - update `application.yml` as shown above

### Benefits Summary

✅ **Simpler Architecture**: 2 fewer dependencies (Redis client, Prometheus registry)
✅ **Lower Infrastructure Cost**: One less service to run and maintain
✅ **Better Enterprise Monitoring**: Dynatrace provides richer analytics
✅ **Faster Startup**: Less initialization overhead
✅ **Easier Development**: Fewer moving parts for local development

---

## Version 1.0.0 - Initial Release

See [README.md](README.md) for full feature list.
