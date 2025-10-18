# 🚀 Nursing Training AI - Start All Services Script

Write-Host "🚀 Starting Nursing Training AI Application..." -ForegroundColor Green
Write-Host ""

# Verifică dacă Docker este instalat
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker nu este instalat! Te rog instalează Docker Desktop" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Pornește baza de date și Redis
Write-Host "🗄️ Starting Database and Redis..." -ForegroundColor Blue
try {
    docker-compose up -d postgres redis
    Write-Host "✅ Database and Redis started" -ForegroundColor Green
} catch {
    Write-Host "❌ Eroare la pornirea bazei de date" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Așteaptă ca serviciile să pornească
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Pornește backend-ul
Write-Host "🐍 Starting Backend API..." -ForegroundColor Blue
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd backend && python main.py" -WindowStyle Normal

# Așteaptă ca backend-ul să pornească
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Pornește frontend-ul
Write-Host "🌐 Starting Frontend Web App..." -ForegroundColor Blue
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd frontend && npm run dev" -WindowStyle Normal

# Pornește mobile-ul
Write-Host "📱 Starting Mobile App..." -ForegroundColor Blue
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd mobile && npx expo start" -WindowStyle Normal

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Services running on:" -ForegroundColor Cyan
Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  - Frontend Web: http://localhost:3000" -ForegroundColor White
Write-Host "  - Mobile App: Expo DevTools" -ForegroundColor White
Write-Host "  - Database: localhost:5432" -ForegroundColor White
Write-Host "  - Redis: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to stop all services..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Oprește toate serviciile
Write-Host "🛑 Stopping all services..." -ForegroundColor Red
try {
    docker-compose down
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "✅ All services stopped" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some services may still be running" -ForegroundColor Yellow
}

Read-Host "Press Enter to exit"
