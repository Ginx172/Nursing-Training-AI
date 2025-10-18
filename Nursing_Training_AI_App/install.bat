@echo off
echo 🏥 Installing Nursing Training AI Application...
echo.

REM Verifică dacă Python este instalat
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nu este instalat! Te rog instalează Python 3.11+ din https://python.org
    pause
    exit /b 1
)

REM Verifică dacă Node.js este instalat
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js nu este instalat! Te rog instalează Node.js 18+ din https://nodejs.org
    pause
    exit /b 1
)

REM Verifică dacă Docker este instalat
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Docker nu este instalat! Va fi necesar pentru baza de date și Redis
    echo    Poți instala Docker Desktop din https://docker.com
    echo.
)

echo ✅ Dependențele de bază sunt instalate
echo.

REM Creează fișierul .env
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ✅ .env file created
    echo ⚠️  Te rog editează .env cu configurațiile tale
    echo.
)

REM Instalează dependențele backend
echo 🐍 Installing Python dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Eroare la instalarea dependențelor Python
    pause
    exit /b 1
)
cd ..
echo ✅ Python dependencies installed

REM Instalează dependențele frontend
echo 📦 Installing Node.js dependencies...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo ❌ Eroare la instalarea dependențelor Node.js
    pause
    exit /b 1
)
cd ..
echo ✅ Node.js dependencies installed

REM Instalează dependențele mobile
echo 📱 Installing Mobile dependencies...
cd mobile
npm install
if %errorlevel% neq 0 (
    echo ❌ Eroare la instalarea dependențelor Mobile
    pause
    exit /b 1
)
cd ..
echo ✅ Mobile dependencies installed

echo.
echo 🎉 Installation completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your configuration
echo 2. Start database and Redis: docker-compose up -d postgres redis
echo 3. Start backend: cd backend && python main.py
echo 4. Start frontend: cd frontend && npm run dev
echo 5. Start mobile: cd mobile && npx expo start
echo.
echo 📚 Documentation: docs/ARCHITECTURE.md
echo.
pause
