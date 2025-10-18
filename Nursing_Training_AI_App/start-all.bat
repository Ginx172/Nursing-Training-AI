@echo off
echo 🚀 Starting Nursing Training AI Application...
echo.

REM Verifică dacă Docker este instalat
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker nu este instalat! Te rog instalează Docker Desktop
    pause
    exit /b 1
)

REM Pornește baza de date și Redis
echo 🗄️ Starting Database and Redis...
docker-compose up -d postgres redis
if %errorlevel% neq 0 (
    echo ❌ Eroare la pornirea bazei de date
    pause
    exit /b 1
)

REM Așteaptă ca serviciile să pornească
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Pornește backend-ul
echo 🐍 Starting Backend API...
start "Backend API" cmd /k "cd backend && python main.py"

REM Așteaptă ca backend-ul să pornească
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Pornește frontend-ul
echo 🌐 Starting Frontend Web App...
start "Frontend Web" cmd /k "cd frontend && npm run dev"

REM Pornește mobile-ul
echo 📱 Starting Mobile App...
start "Mobile App" cmd /k "cd mobile && npx expo start"

echo.
echo ✅ All services started!
echo.
echo 📱 Services running on:
echo   - Backend API: http://localhost:8000
echo   - Frontend Web: http://localhost:3000
echo   - Mobile App: Expo DevTools
echo   - Database: localhost:5432
echo   - Redis: localhost:6379
echo.
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo Press any key to stop all services...
pause >nul

REM Oprește toate serviciile
echo 🛑 Stopping all services...
docker-compose down
taskkill /f /im "python.exe" >nul 2>&1
taskkill /f /im "node.exe" >nul 2>&1
echo ✅ All services stopped
