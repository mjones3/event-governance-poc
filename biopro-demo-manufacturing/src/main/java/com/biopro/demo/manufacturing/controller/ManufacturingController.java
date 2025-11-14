package com.biopro.demo.manufacturing.controller;

import com.biopro.demo.manufacturing.service.ManufacturingEventPublisher;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST controller for Manufacturing service
 */
@Slf4j
@RestController
@RequestMapping("/api/manufacturing")
@RequiredArgsConstructor
public class ManufacturingController {

    private final ManufacturingEventPublisher eventPublisher;

    @PostMapping("/products")
    public ResponseEntity<String> createProduct(
            @RequestBody ManufacturingEventPublisher.ProductCreatedRequest request) {

        log.info("Received product creation request: {}", request.getProductId());
        eventPublisher.publishProductCreated(request);

        return ResponseEntity.ok("Product event published");
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Manufacturing service is healthy");
    }
}
