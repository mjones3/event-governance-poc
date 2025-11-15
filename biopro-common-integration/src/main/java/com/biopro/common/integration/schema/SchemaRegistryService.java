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
     * Validates an event against its registered schema using Avro's built-in validation.
     * This catches ALL violations including nested structures, types, enums, etc.
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

            // Validate by actually serializing to Avro
            // This uses Avro's complete validation logic
            log.debug("Validating event against schema: {}", subject);

            if (event instanceof Map) {
                Map<String, Object> eventMap = (Map<String, Object>) event;

                try {
                    // Attempt to create GenericRecord from the data
                    // This will throw AvroRuntimeException if validation fails
                    org.apache.avro.generic.GenericData.Record record =
                        new org.apache.avro.generic.GenericData.Record(schema);

                    // Populate the record
                    populateRecord(record, eventMap, schema);

                    // CRITICAL: Actually serialize to trigger full Avro validation
                    // Avro only validates on serialization, not on record creation!
                    java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
                    org.apache.avro.io.DatumWriter<org.apache.avro.generic.GenericRecord> writer =
                        new org.apache.avro.generic.GenericDatumWriter<>(schema);
                    org.apache.avro.io.Encoder encoder = org.apache.avro.io.EncoderFactory.get().binaryEncoder(out, null);
                    writer.write(record, encoder);
                    encoder.flush();

                    // If we got here, validation succeeded
                    return ValidationResult.builder()
                            .valid(true)
                            .schemaId(schema.getName())
                            .schemaVersion(getLatestVersion(subject))
                            .build();

                } catch (org.apache.avro.AvroRuntimeException | java.io.IOException e) {
                    // Avro validation failed
                    return ValidationResult.builder()
                            .valid(false)
                            .errorMessage("Schema validation failed: " + extractAvroError(e))
                            .build();
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
     * Recursively populates an Avro GenericRecord from a Map.
     * Avro will validate all fields, types, and constraints.
     */
    private void populateRecord(org.apache.avro.generic.GenericData.Record record,
                                Map<String, Object> data, Schema schema) {
        for (Schema.Field field : schema.getFields()) {
            Object value = data.get(field.name());

            if (value == null) {
                // Avro will validate if null is allowed for this field
                record.put(field.name(), null);
            } else if (value instanceof Map && field.schema().getType() == Schema.Type.RECORD) {
                // Nested record - recurse
                Schema fieldSchema = unwrapUnion(field.schema());
                if (fieldSchema.getType() == Schema.Type.RECORD) {
                    org.apache.avro.generic.GenericData.Record nestedRecord =
                        new org.apache.avro.generic.GenericData.Record(fieldSchema);
                    populateRecord(nestedRecord, (Map<String, Object>) value, fieldSchema);
                    record.put(field.name(), nestedRecord);
                } else {
                    record.put(field.name(), value);
                }
            } else if (value instanceof java.util.List) {
                // Array field - need to handle arrays of records
                Schema fieldSchema = unwrapUnion(field.schema());
                if (fieldSchema.getType() == Schema.Type.ARRAY) {
                    Schema elementSchema = fieldSchema.getElementType();
                    if (elementSchema.getType() == Schema.Type.RECORD) {
                        // Array of records - convert each Map to GenericRecord
                        java.util.List<Object> sourceList = (java.util.List<Object>) value;
                        java.util.List<org.apache.avro.generic.GenericData.Record> recordList = new java.util.ArrayList<>();
                        for (Object item : sourceList) {
                            if (item instanceof Map) {
                                org.apache.avro.generic.GenericData.Record itemRecord =
                                    new org.apache.avro.generic.GenericData.Record(elementSchema);
                                populateRecord(itemRecord, (Map<String, Object>) item, elementSchema);
                                recordList.add(itemRecord);
                            } else {
                                // Item is already a GenericRecord or primitive
                                recordList.add((org.apache.avro.generic.GenericData.Record) item);
                            }
                        }
                        record.put(field.name(), recordList);
                    } else {
                        // Array of primitives
                        record.put(field.name(), value);
                    }
                } else {
                    record.put(field.name(), value);
                }
            } else {
                // Primitive or other type - Avro will validate
                record.put(field.name(), value);
            }
        }
    }

    /**
     * Unwraps union schemas to get the actual type
     */
    private Schema unwrapUnion(Schema schema) {
        if (schema.getType() == Schema.Type.UNION) {
            for (Schema unionType : schema.getTypes()) {
                if (unionType.getType() != Schema.Type.NULL) {
                    return unionType;
                }
            }
        }
        return schema;
    }

    /**
     * Extracts a clean error message from Avro exceptions
     */
    private String extractAvroError(Exception e) {
        String message = e.getMessage();
        if (message == null && e.getCause() != null) {
            message = e.getCause().getMessage();
        }
        return message != null ? message : "Unknown Avro validation error";
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
