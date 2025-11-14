# Kill processes using BioPro ports

Write-Host "Killing processes on BioPro ports..." -ForegroundColor Yellow

# Ports to check
$ports = @(2181, 9092, 8080, 8081, 8082, 9090, 3000, 8090)

foreach ($port in $ports) {
    Write-Host "`nChecking port $port..." -ForegroundColor Cyan

    # Find process using the port
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

    if ($connections) {
        foreach ($conn in $connections) {
            $processId = $conn.OwningProcess
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue

            if ($process) {
                Write-Host "  Found: $($process.ProcessName) (PID: $processId)" -ForegroundColor Red
                Write-Host "  Killing process..." -ForegroundColor Yellow

                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue

                if ($?) {
                    Write-Host "  ✅ Process killed successfully" -ForegroundColor Green
                } else {
                    Write-Host "  ❌ Failed to kill process (may need admin rights)" -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host "  ✅ Port $port is free" -ForegroundColor Green
    }
}

Write-Host "`n✅ Done! All ports checked." -ForegroundColor Green
Write-Host "`nNow run: docker-compose up -d --build" -ForegroundColor Cyan
