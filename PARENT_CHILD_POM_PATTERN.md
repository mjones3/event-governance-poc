# Parent/Child POM Pattern with Spring Boot Starter

## ✅ Yes! This POC Uses the Exact Spring Boot Starter Pattern

The BioPro Event Governance Framework follows the **same multi-module pattern** as official Spring Boot starters (like `spring-boot-starter-web`, `spring-boot-starter-data-jpa`, etc.).

---

## Architecture

### Parent POM (Aggregator)

**File**: `pom.xml`
**Artifact**: `biopro-common-dlq-parent`
**Packaging**: `pom`

```xml
<groupId>com.biopro</groupId>
<artifactId>biopro-common-dlq-parent</artifactId>
<version>1.0.0-SNAPSHOT</version>
<packaging>pom</packaging>

<modules>
    <module>biopro-common-core</module>
    <module>biopro-common-config</module>
    <module>biopro-common-integration</module>
    <module>biopro-common-security</module>
    <module>biopro-common-monitoring</module>
    <module>biopro-dlq-spring-boot-starter</module>  <!-- AGGREGATING STARTER -->
    <module>biopro-demo-orders</module>
    <module>biopro-demo-collections</module>
    <module>biopro-demo-manufacturing</module>
</modules>
```

**Responsibilities**:
- ✅ Defines all dependency versions (Spring Boot, Kafka, Confluent, etc.)
- ✅ Manages common properties (Java 17, encoding, etc.)
- ✅ Provides `<dependencyManagement>` for all children
- ✅ Aggregates all modules for reactor build

---

## Child Modules (Components)

### 1. Core Modules (Business Logic)

#### `biopro-common-core`
```xml
<parent>
    <groupId>com.biopro</groupId>
    <artifactId>biopro-common-dlq-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</parent>

<artifactId>biopro-common-core</artifactId>
```

**Contains**:
- DLQ domain models (`DLQEvent`, `Priority`, `ErrorType`)
- DLQ processor logic
- Reprocessing service
- **No Spring dependencies** (pure domain logic)

#### `biopro-common-config`
**Contains**:
- Spring Boot auto-configuration classes
- `@Configuration` beans
- Circuit breaker configuration
- Retry configuration
- **This is where Spring Boot magic happens!**

#### `biopro-common-integration`
**Contains**:
- Kafka integration
- Schema Registry service
- Avro schema definitions (`.avsc` files)
- Generated Avro classes

#### `biopro-common-security`
**Contains**:
- Audit service
- Authorization framework
- JWT validation (future)

#### `biopro-common-monitoring`
**Contains**:
- Dynatrace metrics service
- Health indicators
- Custom business metrics

---

### 2. Aggregating Starter (The Magic)

#### `biopro-dlq-spring-boot-starter`

**This is the key module** - it's what users depend on!

```xml
<parent>
    <groupId>com.biopro</groupId>
    <artifactId>biopro-common-dlq-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</parent>

<artifactId>biopro-dlq-spring-boot-starter</artifactId>

<dependencies>
    <!-- Aggregates ALL BioPro modules -->
    <dependency>
        <groupId>com.biopro</groupId>
        <artifactId>biopro-common-core</artifactId>
    </dependency>
    <dependency>
        <groupId>com.biopro</groupId>
        <artifactId>biopro-common-config</artifactId>
    </dependency>
    <dependency>
        <groupId>com.biopro</groupId>
        <artifactId>biopro-common-integration</artifactId>
    </dependency>
    <dependency>
        <groupId>com.biopro</groupId>
        <artifactId>biopro-common-security</artifactId>
    </dependency>
    <dependency>
        <groupId>com.biopro</groupId>
        <artifactId>biopro-common-monitoring</artifactId>
    </dependency>

    <!-- Spring Boot essentials -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-autoconfigure</artifactId>
    </dependency>
</dependencies>
```

**Why This Pattern?**

Just like `spring-boot-starter-web`:
```xml
<!-- spring-boot-starter-web aggregates: -->
<!-- - spring-boot-starter -->
<!-- - spring-web -->
<!-- - spring-webmvc -->
<!-- - tomcat-embed -->
<!-- - jackson -->
```

Our `biopro-dlq-spring-boot-starter` aggregates:
```xml
<!-- biopro-dlq-spring-boot-starter aggregates: -->
<!-- - biopro-common-core -->
<!-- - biopro-common-config -->
<!-- - biopro-common-integration -->
<!-- - biopro-common-security -->
<!-- - biopro-common-monitoring -->
```

---

### 3. Demo Applications (Consumers)

#### `biopro-demo-orders`, `biopro-demo-collections`, `biopro-demo-manufacturing`

**How They Use the Starter**:

```xml
<parent>
    <groupId>com.biopro</groupId>
    <artifactId>biopro-common-dlq-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</parent>

<dependencies>
    <!-- ONE dependency gets EVERYTHING -->
    <dependency>
        <groupId>com.biopro</groupId>
        <artifactId>biopro-dlq-spring-boot-starter</artifactId>
        <version>${project.version}</version>
    </dependency>

    <!-- Just add Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
</dependencies>
```

**Configuration** (application.yml):
```yaml
biopro:
  dlq:
    enabled: true
    module-name: orders  # That's it! Auto-configuration does the rest
```

**Result**:
- ✅ DLQ processing automatically enabled
- ✅ Kafka producer/consumer configured
- ✅ Schema Registry client configured
- ✅ Circuit breaker and retry configured
- ✅ Metrics and health checks registered
- ✅ Audit logging enabled

---

## Maven Reactor Build

When you run `mvn clean install` from parent:

```
[INFO] Reactor Build Order:
[INFO]
[INFO] BioPro Common DLQ Parent          [pom]   ← Parent coordinates everything
[INFO] BioPro Common Core                [jar]   ← Builds first (no dependencies)
[INFO] BioPro Common Config              [jar]   ← Depends on Core
[INFO] BioPro Common Integration         [jar]   ← Depends on Core
[INFO] BioPro Common Security            [jar]   ← Depends on Core
[INFO] BioPro Common Monitoring          [jar]   ← Depends on Core
[INFO] BioPro DLQ Spring Boot Starter    [jar]   ← Aggregates all above
[INFO] BioPro Demo - Orders              [jar]   ← Depends on Starter
[INFO] BioPro Demo - Collections         [jar]   ← Depends on Starter
[INFO] BioPro Demo - Manufacturing       [jar]   ← Depends on Starter
```

Maven automatically:
1. Resolves dependency order
2. Builds modules in correct sequence
3. Installs each to local `.m2` repo
4. Makes them available to dependent modules

---

## Benefits of This Pattern

### 1. **Zero Configuration for Consumers**

Users only need:
```xml
<dependency>
    <groupId>com.biopro</groupId>
    <artifactId>biopro-dlq-spring-boot-starter</artifactId>
</dependency>
```

### 2. **Centralized Version Management**

Parent POM controls all versions:
```xml
<properties>
    <spring-boot.version>3.2.1</spring-boot.version>
    <kafka.version>3.6.1</kafka.version>
    <confluent.version>7.5.3</confluent.version>
</properties>
```

Children inherit automatically - no version conflicts!

### 3. **Modular Development**

Each module has single responsibility:
- **Core**: Domain logic (no Spring)
- **Config**: Spring auto-configuration
- **Integration**: External systems
- **Security**: Cross-cutting concerns
- **Monitoring**: Observability

### 4. **Easy Testing**

Test modules independently:
```bash
cd biopro-common-core
mvn test  # Tests just core logic
```

### 5. **Consistent Builds**

One command builds everything:
```bash
mvn clean install
```

---

## Spring Boot Auto-Configuration

The magic happens in `biopro-common-config`:

**File**: `biopro-common-config/src/main/resources/META-INF/spring.factories`
```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.biopro.common.config.DLQAutoConfiguration
```

**Auto-Configuration Class**:
```java
@Configuration
@ConditionalOnProperty(prefix = "biopro.dlq", name = "enabled", havingValue = "true")
@EnableConfigurationProperties(DLQConfigurationProperties.class)
public class DLQAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public DLQProcessor dlqProcessor() {
        return new DLQProcessor();
    }

    @Bean
    public SchemaRegistryService schemaRegistryService() {
        return new SchemaRegistryService();
    }

    // Circuit breaker, retry, metrics, etc.
}
```

**Result**: When user adds the starter and sets `biopro.dlq.enabled=true`, Spring Boot automatically:
1. Scans for `@Configuration` classes
2. Finds `DLQAutoConfiguration`
3. Checks conditions (`@ConditionalOnProperty`)
4. Registers all beans
5. Injects dependencies

---

## Comparison to Official Spring Boot Starters

### `spring-boot-starter-web`
```
spring-boot-starter-web/
├── spring-boot-starter
├── spring-web
├── spring-webmvc
└── tomcat-embed
```

### `biopro-dlq-spring-boot-starter`
```
biopro-dlq-spring-boot-starter/
├── biopro-common-core
├── biopro-common-config
├── biopro-common-integration
├── biopro-common-security
└── biopro-common-monitoring
```

**Exact same pattern!**

---

## SSL Build Issue Workaround

### Problem
Maven can't download from Maven Central due to corporate SSL certs.

### Solutions

#### ✅ Option 1: Use Docker Builds (RECOMMENDED for POC)

**Tilt automatically uses Docker**, which works fine:
```bash
tilt up
# Docker builds all services successfully
```

**Or manually**:
```bash
docker build -t local/biopro-orders:latest -f biopro-demo-orders/Dockerfile .
```

Docker builds work because:
- Uses its own JDK inside container
- No corporate proxy/SSL issues
- Clean dependency downloads

#### ⚠️ Option 2: Configure Corporate Proxy (If Needed Later)

Create `~/.m2/settings.xml`:
```xml
<settings>
    <proxies>
        <proxy>
            <id>corporate</id>
            <active>true</active>
            <protocol>https</protocol>
            <host>proxy.company.com</host>
            <port>8080</port>
        </proxy>
    </proxies>
</settings>
```

#### ⚠️ Option 3: Import Corporate CA Cert (Production)

```bash
keytool -import -trustcacerts -alias corporate \
  -file corporate-ca.crt \
  -keystore $JAVA_HOME/lib/security/cacerts
```

---

## Conclusion

✅ **Yes, this POC uses the exact parent/child POM pattern with Spring Boot starter!**

**Structure**:
- Parent POM aggregates 9 modules
- 5 common modules (core, config, integration, security, monitoring)
- 1 aggregating starter (pulls everything together)
- 3 demo applications (show usage)

**Build**:
- Use Docker/Tilt (works perfectly)
- Local Maven has SSL issues (corporate proxy)
- POC is fully functional via Docker

**Pattern**:
- Matches official Spring Boot starters
- Zero-configuration for users
- Auto-configuration via Spring Boot
- Modular and testable

---

**Ready to deploy with Tilt!** 🚀

```bash
tilt up  # Everything just works!
```
