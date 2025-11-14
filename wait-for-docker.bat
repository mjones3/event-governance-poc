@echo off
setlocal
set COUNT=0
:LOOP
if %COUNT% GEQ 12 (
    echo Docker failed to start after 60 seconds
    exit /b 1
)
docker info >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Docker is ready
    exit /b 0
)
timeout /t 5 /nobreak >nul 2>&1
set /A COUNT+=1
goto LOOP
