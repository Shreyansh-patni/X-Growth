# X Growth Automation - Startup Script

Write-Host "Starting X Growth Automation System..." -ForegroundColor Green

# Start Backend in background
Write-Host "Starting Backend (Port 8001)..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --port 8001" -WorkingDirectory "backend" -WindowStyle Minimized

# Start Frontend
Write-Host "Starting Frontend (Port 3000)..." -ForegroundColor Cyan
Write-Host "Frontend will open in a new terminal window."
Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "frontend"

Write-Host "Services started!" -ForegroundColor Green
Write-Host "Backend API: http://localhost:8001"
Write-Host "Frontend UI: http://localhost:3000"
Write-Host "Press any key to exit this launcher (services will keep running)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
