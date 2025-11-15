package com.biopro.demo.orders.controller;

import com.biopro.demo.orders.service.OrderEventPublisher;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST controller for order operations.
 * Demonstrates event publishing with DLQ handling.
 */
@Slf4j
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderEventPublisher eventPublisher;

    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(@RequestBody OrderRequest request) {
        log.info("Received order creation request: {}", request);

        try {
            OrderEventPublisher.OrderCreatedRequest eventRequest =
                    OrderEventPublisher.OrderCreatedRequest.builder()
                            .orderId(request.getOrderId())
                            .bloodType(request.getBloodType())
                            .quantity(request.getQuantity())
                            .priority(request.getPriority())
                            .facilityId(request.getFacilityId())
                            .requestedBy(request.getRequestedBy())
                            .orderStatus(request.getOrderStatus())
                            .build();

            eventPublisher.publishOrderCreated(eventRequest);

            return ResponseEntity.ok(OrderResponse.builder()
                    .success(true)
                    .message("Order event published successfully")
                    .orderId(request.getOrderId())
                    .build());

        } catch (Exception e) {
            log.error("Error creating order", e);
            return ResponseEntity.internalServerError()
                    .body(OrderResponse.builder()
                            .success(false)
                            .message("Error: " + e.getMessage())
                            .build());
        }
    }

    @lombok.Data
    public static class OrderRequest {
        private String orderId;
        private String bloodType;
        private Integer quantity;
        private String priority;
        private String facilityId;
        private String requestedBy;
        private String orderStatus;
    }

    @lombok.Data
    @lombok.Builder
    public static class OrderResponse {
        private boolean success;
        private String message;
        private String orderId;
    }
}
