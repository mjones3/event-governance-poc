package com.biopro.common.integration.schema;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClient;
import io.confluent.kafka.schemaregistry.client.rest.exceptions.RestClientException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.avro.Schema;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Enterprise Schema Registry Service with in-memory caching.
 * Provides schema validation, retrieval, and registration.
 * Schema Registry has built-in caching; this adds an application-level cache for performance.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SchemaRegistryService {

    private final SchemaRegistryClient schemaRegistryClient;

    // In-memory Caffeine cache for frequently accessed schemas
    private final Cache<String, Schema> schemaCache = Caffeine.newBuilder()
            .expireAfterWrite(30, TimeUnit.MINUTES)
            .maximumSize(1000)
            .recordStats()
            .build();

    /**
     * Validates an event against its registered schema
     */
    public ValidationResult validateEvent(String subject, Object event) {
        try {
            Schema schema = getSchema(subject);

            if (schema == null) {
                return ValidationResult.builder()
                        .valid(false)
                        .errorMessage("Schema not found for subject: " + subject)
                        .build();
            }

            // Validate event structure against schema
            log.debug("Validating event against schema: {}", subject);

            // For Map-based events, check required fields
            if (event instanceof Map) {
                Map<String, Object> eventMap = (Map<String, Object>) event;

                // Check all required fields from schema
                for (Schema.Field field : schema.getFields()) {
                    // Field is required if it has no default value
                    if (field.defaultVal() == null) {
                        // Check if field exists and is not null
                        if (!eventMap.containsKey(field.name()) || eventMap.get(field.name()) == null) {
                            return ValidationResult.builder()
                                    .valid(false)
                                    .errorMessage("Missing required field: " + field.name())
                                    .build();
                        }
                    }
                }
            }

            return ValidationResult.builder()
                    .valid(true)
                    .schemaId(schema.getName())
                    .schemaVersion(getLatestVersion(subject))
                    .build();

        } catch (Exception e) {
            log.error("Error validating event against schema: {}", subject, e);
            return ValidationResult.builder()
                    .valid(false)
                    .errorMessage("Validation error: " + e.getMessage())
                    .build();
        }
    }

    /**
     * Retrieves schema from cache or Schema Registry.
     * Uses in-memory cache to reduce Schema Registry calls.
     */
    public Schema getSchema(String subject) {
        // Try cache first
        Schema cachedSchema = schemaCache.getIfPresent(subject);
        if (cachedSchema != null) {
            log.debug("Schema found in cache: {}", subject);
            return cachedSchema;
        }

        // Fetch from Schema Registry (which has its own internal caching)
        try {
            log.debug("Fetching schema from Schema Registry: {}", subject);
            String schemaString = schemaRegistryClient.getLatestSchemaMetadata(subject).getSchema();
            Schema schema = new Schema.Parser().parse(schemaString);

            // Update application cache
            schemaCache.put(subject, schema);

            return schema;

        } catch (IOException | RestClientException e) {
            log.error("Failed to fetch schema from registry: {}", subject, e);
            return null;
        }
    }

    /**
     * Gets the latest version number for a subject
     */
    private int getLatestVersion(String subject) {
        try {
            return schemaRegistryClient.getLatestSchemaMetadata(subject).getVersion();
        } catch (IOException | RestClientException e) {
            log.warn("Failed to get latest version for subject: {}", subject);
            return -1;
        }
    }

    /**
     * Registers a new schema with the Schema Registry
     */
    public SchemaRegistrationResult registerSchema(String subject, String schemaString) {
        try {
            Schema schema = new Schema.Parser().parse(schemaString);

            int schemaId = schemaRegistryClient.register(subject, schema);

            // Update cache
            schemaCache.put(subject, schema);

            log.info("Successfully registered schema: {} with ID: {}", subject, schemaId);

            return SchemaRegistrationResult.builder()
                    .success(true)
                    .schemaId(schemaId)
                    .subject(subject)
                    .message("Schema registered successfully")
                    .build();

        } catch (IOException | RestClientException e) {
            log.error("Failed to register schema: {}", subject, e);
            return SchemaRegistrationResult.builder()
                    .success(false)
                    .subject(subject)
                    .message("Failed to register schema: " + e.getMessage())
                    .build();
        }
    }

    /**
     * Checks compatibility of a new schema version
     */
    public CompatibilityResult checkCompatibility(String subject, String newSchemaString) {
        try {
            Schema newSchema = new Schema.Parser().parse(newSchemaString);

            boolean compatible = schemaRegistryClient.testCompatibility(subject, newSchema);

            return CompatibilityResult.builder()
                    .compatible(compatible)
                    .subject(subject)
                    .message(compatible ? "Schema is compatible" : "Schema is not compatible")
                    .build();

        } catch (IOException | RestClientException e) {
            log.error("Failed to check compatibility for subject: {}", subject, e);
            return CompatibilityResult.builder()
                    .compatible(false)
                    .subject(subject)
                    .message("Compatibility check failed: " + e.getMessage())
                    .build();
        }
    }

    @lombok.Data
    @lombok.Builder
    public static class ValidationResult {
        private boolean valid;
        private String schemaId;
        private int schemaVersion;
        private String errorMessage;
    }

    @lombok.Data
    @lombok.Builder
    public static class SchemaRegistrationResult {
        private boolean success;
        private int schemaId;
        private String subject;
        private String message;
    }

    @lombok.Data
    @lombok.Builder
    public static class CompatibilityResult {
        private boolean compatible;
        private String subject;
        private String message;
    }
}
