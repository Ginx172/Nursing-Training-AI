# Robust Startup Script for Nursing Training AI
# cleans up existing processes before starting

Write-Host "🏥 Nursing Training AI - Secure Launch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Cleanup Phase
Write-Host "🧹 performing cleanup..." -ForegroundColor Yellow

# Kill Python processes ( Backend)
try {
    $pythonProcs = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcs) {
        Write-Host "   - Killing $($pythonProcs.Count) lingering Python processes..." -ForegroundColor Gray
        Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    }
}
catch {
    Write-Host "   - No Python processes found." -ForegroundColor Gray
}

# Kill Node processes (Frontend)
try {
    $nodeProcs = Get-Process node -ErrorAction SilentlyContinue
    if ($nodeProcs) {
        Write-Host "   - Killing $($nodeProcs.Count) lingering Node.js processes..." -ForegroundColor Gray
        Stop-Process -Name node -Force -ErrorAction SilentlyContinue
    }
}
catch {
    Write-Host "   - No Node.js processes found." -ForegroundColor Gray
}

# Free up ports explicitly
try {
    $port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($port8000) {
        Write-Host "   - Force freeing Port 8000..." -ForegroundColor Red
        Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
catch {}

try {
    $port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
    if ($port3000) {
        Write-Host "   - Force freeing Port 3000..." -ForegroundColor Red
        Stop-Process -Id $port3000.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
catch {}

Start-Sleep -Seconds 2
Write-Host "✅ Cleanup Complete. System Ready." -ForegroundColor Green
Write-Host ""

# 2. Start Backend
Write-Host "🚀 Starting Backend (FastAPI)..." -ForegroundColor Yellow
$backendScript = "cd 'j:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend'; .\venv\Scripts\python main.py"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Normal

# 3. Start Frontend
Write-Host "🎨 Starting Frontend (Next.js)..." -ForegroundColor Yellow
$frontendScript = "cd 'j:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\frontend'; npm run dev"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal

# 4. Open Dashboard
Write-Host "🌐 Waiting for services..." -ForegroundColor Cyan
for ($i = 5; $i -gt 0; $i--) {
    Write-Host "   Launching in $i..." -NoNewline
    Start-Sleep -Seconds 1
    Write-Host "`r" -NoNewline
}
Write-Host ""
Start-Process "http://localhost:3000/dashboard"

Write-Host "✨ Application Launched Successfully!" -ForegroundColor Green
Write-Host "   - To restart: Run this script again."
Write-Host "   - If it freezes: Close all windows and run this script."
