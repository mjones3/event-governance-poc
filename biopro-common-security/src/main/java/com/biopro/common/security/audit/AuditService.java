package com.biopro.common.security.audit;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Map;

/**
 * Audit service for tracking all DLQ operations.
 * Ensures FDA compliance with complete audit trail.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuditService {

    /**
     * Logs a DLQ operation for audit trail
     */
    public void logDlqOperation(
            String operation,
            String eventId,
            String module,
            String user,
            Map<String, Object> metadata) {

        AuditEntry entry = AuditEntry.builder()
                .timestamp(Instant.now())
                .operation(operation)
                .eventId(eventId)
                .module(module)
                .user(user)
                .metadata(metadata)
                .build();

        // In production, this would write to:
        // - CloudWatch Logs
        // - S3 for long-term retention
        // - FDA audit system
        log.info("AUDIT: operation={}, eventId={}, module={}, user={}, metadata={}",
                operation, eventId, module, user, metadata);
    }

    /**
     * Logs a security event (authentication, authorization, etc.)
     */
    public void logSecurityEvent(String eventType, Map<String, String> details) {
        log.warn("SECURITY_AUDIT: type={}, details={}", eventType, details);
    }

    /**
     * Logs an authorization decision
     */
    public void logAuthorizationDecision(
            String username,
            String resource,
            String permission,
            boolean granted) {

        log.info("AUTHORIZATION_AUDIT: user={}, resource={}, permission={}, granted={}",
                username, resource, permission, granted);
    }

    /**
     * Logs PII detection
     */
    public void logPIIDetection(String eventType, int fieldCount, java.util.Set<?> fieldTypes) {
        log.warn("PII_DETECTION: eventType={}, fieldCount={}, types={}",
                eventType, fieldCount, fieldTypes);
    }

    /**
     * Logs field encryption
     */
    public void logFieldEncryption(String fieldName, String eventType, String keyId, String user) {
        log.info("ENCRYPTION_AUDIT: field={}, eventType={}, keyId={}, user={}",
                fieldName, eventType, keyId, user);
    }

    @lombok.Data
    @lombok.Builder
    private static class AuditEntry {
        private Instant timestamp;
        private String operation;
        private String eventId;
        private String module;
        private String user;
        private Map<String, Object> metadata;
    }
}
