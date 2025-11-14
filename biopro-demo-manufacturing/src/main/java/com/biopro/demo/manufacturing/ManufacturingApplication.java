package com.biopro.demo.manufacturing;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * BioPro Manufacturing Service - Demo Application
 * Demonstrates plasma product manufacturing event processing with DLQ integration
 */
@SpringBootApplication(scanBasePackages = {
        "com.biopro.demo.manufacturing",
        "com.biopro.common"
})
public class ManufacturingApplication {

    public static void main(String[] args) {
        SpringApplication.run(ManufacturingApplication.class, args);
    }
}
