@echo off
REM Kill processes using BioPro ports

echo Killing processes on BioPro ports...
echo.

REM Kill process on port 2181 (Zookeeper)
echo Checking port 2181 (Zookeeper)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :2181 ^| findstr LISTENING') do (
    echo Found process %%a on port 2181
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   Failed to kill PID %%a - may need admin rights
    ) else (
        echo   Killed PID %%a
    )
)

REM Kill process on port 9092 (Kafka)
echo Checking port 9092 (Kafka)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9092 ^| findstr LISTENING') do (
    echo Found process %%a on port 9092
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   Failed to kill PID %%a - may need admin rights
    ) else (
        echo   Killed PID %%a
    )
)

REM Kill process on port 8080 (Orders)
echo Checking port 8080 (Orders)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo Found process %%a on port 8080
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   Failed to kill PID %%a - may need admin rights
    ) else (
        echo   Killed PID %%a
    )
)

REM Kill process on port 8081 (Schema Registry / Collections)
echo Checking port 8081 (Schema Registry / Collections)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8081 ^| findstr LISTENING') do (
    echo Found process %%a on port 8081
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   Failed to kill PID %%a - may need admin rights
    ) else (
        echo   Killed PID %%a
    )
)

REM Kill process on port 8082 (Manufacturing)
echo Checking port 8082 (Manufacturing)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8082 ^| findstr LISTENING') do (
    echo Found process %%a on port 8082
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   Failed to kill PID %%a - may need admin rights
    ) else (
        echo   Killed PID %%a
    )
)

echo.
echo Done! All ports checked.
echo.
echo Now run: docker-compose up -d --build
pause
