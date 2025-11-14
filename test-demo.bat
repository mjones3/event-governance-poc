@echo off
REM BioPro Event Governance Framework - Demo Test Script (Windows)
REM This script demonstrates the POC functionality

echo ========================================
echo BioPro Event Governance Framework Demo
echo ========================================
echo.

set ORDERS_SERVICE_URL=http://localhost:8080
set KAFKA_UI_URL=http://localhost:8090
set SCHEMA_REGISTRY_URL=http://localhost:8081

REM Step 1: Check infrastructure
echo Step 1: Checking infrastructure...
echo -----------------------------------
curl -s -f %SCHEMA_REGISTRY_URL% >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Schema Registry is ready
) else (
    echo [ERROR] Schema Registry is not responding
)

curl -s -f %KAFKA_UI_URL% >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Kafka UI is ready
) else (
    echo [ERROR] Kafka UI is not responding
)
echo.

REM Step 2: Check Orders service
echo Step 2: Checking Orders service...
echo -----------------------------------
curl -s -f %ORDERS_SERVICE_URL%/actuator/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Orders Service is ready
) else (
    echo [WARNING] Orders service not running
    echo Start it with: cd biopro-demo-orders ^&^& mvn spring-boot:run
)
echo.

REM Step 3: Publish valid order event
echo Step 3: Publishing VALID order event...
echo -----------------------------------
curl -X POST %ORDERS_SERVICE_URL%/api/orders ^
  -H "Content-Type: application/json" ^
  -d "{\"orderId\":\"ORD-VALID-001\",\"bloodType\":\"O_POSITIVE\",\"quantity\":2,\"priority\":\"URGENT\",\"facilityId\":\"FAC-001\",\"requestedBy\":\"DR-SMITH\"}"
echo.
echo.

REM Step 4: Publish emergency order
echo Step 4: Publishing EMERGENCY order event...
echo -----------------------------------
curl -X POST %ORDERS_SERVICE_URL%/api/orders ^
  -H "Content-Type: application/json" ^
  -d "{\"orderId\":\"ORD-EMERGENCY-002\",\"bloodType\":\"AB_NEGATIVE\",\"quantity\":5,\"priority\":\"LIFE_THREATENING\",\"facilityId\":\"FAC-002\",\"requestedBy\":\"DR-JONES\"}"
echo.
echo.

REM Summary
echo ========================================
echo Demo Test Summary
echo ========================================
echo.
echo Next steps:
echo 1. View events in Kafka UI: %KAFKA_UI_URL%
echo 2. Check main events topic: biopro.orders.events
echo 3. Check DLQ topic: biopro.orders.dlq
echo 4. View metrics: %ORDERS_SERVICE_URL%/actuator/metrics
echo 5. View Prometheus metrics: %ORDERS_SERVICE_URL%/actuator/prometheus
echo.
echo Demo completed!
echo.
pause
