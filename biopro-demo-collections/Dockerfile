# Multi-stage Docker build for BioPro Collections Demo Service
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /build

# Import corporate CA certificate into Java truststore
COPY ca.arc-one.crt /tmp/ca.arc-one.crt
RUN keytool -import -trustcacerts -noprompt -alias corporate-ca \
    -file /tmp/ca.arc-one.crt \
    -keystore /opt/java/openjdk/lib/security/cacerts \
    -storepass changeit

# Copy Maven settings
COPY maven-settings.xml /root/.m2/settings.xml

# Copy parent POM and ALL module POMs first (for layer caching)
COPY pom.xml ./
COPY biopro-common-core/pom.xml ./biopro-common-core/
COPY biopro-common-config/pom.xml ./biopro-common-config/
COPY biopro-common-integration/pom.xml ./biopro-common-integration/
COPY biopro-common-security/pom.xml ./biopro-common-security/
COPY biopro-common-monitoring/pom.xml ./biopro-common-monitoring/
COPY biopro-dlq-spring-boot-starter/pom.xml ./biopro-dlq-spring-boot-starter/
COPY biopro-demo-orders/pom.xml ./biopro-demo-orders/
COPY biopro-demo-collections/pom.xml ./biopro-demo-collections/
COPY biopro-demo-manufacturing/pom.xml ./biopro-demo-manufacturing/

# Download dependencies (cached layer) - only for this module and dependencies
RUN mvn dependency:go-offline -B -pl biopro-demo-collections -am

# Copy ALL source code (Maven needs all modules to validate reactor)
COPY biopro-common-core/src ./biopro-common-core/src
COPY biopro-common-config/src ./biopro-common-config/src
COPY biopro-common-integration/src ./biopro-common-integration/src
COPY biopro-common-security/src ./biopro-common-security/src
COPY biopro-common-monitoring/src ./biopro-common-monitoring/src
COPY biopro-dlq-spring-boot-starter/src ./biopro-dlq-spring-boot-starter/src
COPY biopro-demo-orders/src ./biopro-demo-orders/src
COPY biopro-demo-collections/src ./biopro-demo-collections/src
COPY biopro-demo-manufacturing/src ./biopro-demo-manufacturing/src

# Build the application
RUN mvn clean package -DskipTests -pl biopro-demo-collections -am

# Runtime stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Install glibc compatibility for Snappy compression
RUN apk add --no-cache libc6-compat

# Add non-root user
RUN addgroup -g 1001 biopro && adduser -D -u 1001 -G biopro biopro

# Copy JAR from build stage
COPY --from=build /build/biopro-demo-collections/target/*.jar app.jar

# Change ownership
RUN chown -R biopro:biopro /app

USER biopro

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
