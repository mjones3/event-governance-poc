package com.biopro.common.core.dlq.reprocessing;

import com.biopro.common.core.dlq.model.DLQEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.time.Instant;

/**
 * Service for reprocessing events from the Dead Letter Queue.
 * Supports manual and automatic reprocessing strategies.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DLQReprocessingService {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    /**
     * Reprocesses a DLQ event by publishing it back to the original topic
     */
    public ReprocessingResult reprocess(DLQEvent dlqEvent, String reprocessedBy) {
        log.info("Reprocessing DLQ event: {} from module: {}",
                dlqEvent.getDlqEventId(), dlqEvent.getModule());

        try {
            // Update status
            dlqEvent.setStatus(DLQEvent.ReprocessingStatus.IN_PROGRESS);
            dlqEvent.setLastReprocessingAttempt(Instant.now());
            dlqEvent.setReprocessingCount(dlqEvent.getReprocessingCount() + 1);
            dlqEvent.setReprocessedBy(reprocessedBy);

            // Republish to original topic
            kafkaTemplate.send(
                    dlqEvent.getOriginalTopic(),
                    dlqEvent.getOriginalEventId(),
                    dlqEvent.getOriginalPayload()
            ).whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("Failed to reprocess DLQ event: {}", dlqEvent.getDlqEventId(), ex);
                    dlqEvent.setStatus(DLQEvent.ReprocessingStatus.REPROCESSED_FAILED);
                } else {
                    log.info("Successfully reprocessed DLQ event: {}", dlqEvent.getDlqEventId());
                    dlqEvent.setStatus(DLQEvent.ReprocessingStatus.REPROCESSED_SUCCESS);
                }
            });

            return ReprocessingResult.builder()
                    .success(true)
                    .dlqEventId(dlqEvent.getDlqEventId())
                    .reprocessedAt(Instant.now())
                    .message("Event reprocessed successfully")
                    .build();

        } catch (Exception e) {
            log.error("Error reprocessing DLQ event: {}", dlqEvent.getDlqEventId(), e);
            dlqEvent.setStatus(DLQEvent.ReprocessingStatus.REPROCESSED_FAILED);

            return ReprocessingResult.builder()
                    .success(false)
                    .dlqEventId(dlqEvent.getDlqEventId())
                    .reprocessedAt(Instant.now())
                    .message("Failed to reprocess: " + e.getMessage())
                    .build();
        }
    }

    /**
     * Bulk reprocessing for multiple DLQ events
     */
    public BulkReprocessingResult bulkReprocess(
            java.util.List<DLQEvent> dlqEvents,
            String reprocessedBy) {

        int successCount = 0;
        int failureCount = 0;

        for (DLQEvent event : dlqEvents) {
            ReprocessingResult result = reprocess(event, reprocessedBy);
            if (result.isSuccess()) {
                successCount++;
            } else {
                failureCount++;
            }
        }

        return BulkReprocessingResult.builder()
                .totalEvents(dlqEvents.size())
                .successCount(successCount)
                .failureCount(failureCount)
                .build();
    }

    @lombok.Data
    @lombok.Builder
    public static class ReprocessingResult {
        private boolean success;
        private String dlqEventId;
        private Instant reprocessedAt;
        private String message;
    }

    @lombok.Data
    @lombok.Builder
    public static class BulkReprocessingResult {
        private int totalEvents;
        private int successCount;
        private int failureCount;

        public double getSuccessRate() {
            return totalEvents > 0 ? (double) successCount / totalEvents * 100 : 0;
        }
    }
}
