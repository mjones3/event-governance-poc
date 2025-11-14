package com.biopro.demo.collections.controller;

import com.biopro.demo.collections.service.CollectionEventPublisher;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST controller for Collections service
 */
@Slf4j
@RestController
@RequestMapping("/api/collections")
@RequiredArgsConstructor
public class CollectionController {

    private final CollectionEventPublisher eventPublisher;

    @PostMapping
    public ResponseEntity<String> createCollection(
            @RequestBody CollectionEventPublisher.CollectionReceivedRequest request) {

        log.info("Received collection request: {}", request.getUnitNumber());
        eventPublisher.publishCollectionReceived(request);

        return ResponseEntity.ok("Collection event published");
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Collections service is healthy");
    }
}
