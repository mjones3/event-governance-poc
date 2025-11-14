package com.biopro.demo.collections;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * BioPro Collections Service - Demo Application
 * Demonstrates blood collection event processing with DLQ integration
 */
@SpringBootApplication(scanBasePackages = {
        "com.biopro.demo.collections",
        "com.biopro.common"
})
public class CollectionsApplication {

    public static void main(String[] args) {
        SpringApplication.run(CollectionsApplication.class, args);
    }
}
