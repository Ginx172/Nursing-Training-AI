# 🏥 Nursing Training AI - Installation Script (PowerShell)

Write-Host "🏥 Installing Nursing Training AI Application..." -ForegroundColor Green
Write-Host ""

# Verifică dacă Python este instalat
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python nu este instalat! Te rog instalează Python 3.11+ din https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Verifică dacă Node.js este instalat
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js nu este instalat! Te rog instalează Node.js 18+ din https://nodejs.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Verifică dacă Docker este instalat
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Docker nu este instalat! Va fi necesar pentru baza de date și Redis" -ForegroundColor Yellow
    Write-Host "   Poți instala Docker Desktop din https://docker.com" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "✅ Dependențele de bază sunt instalate" -ForegroundColor Green
Write-Host ""

# Creează fișierul .env
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Blue
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host "⚠️  Te rog editează .env cu configurațiile tale" -ForegroundColor Yellow
    Write-Host ""
}

# Instalează dependențele backend
Write-Host "🐍 Installing Python dependencies..." -ForegroundColor Blue
Set-Location "backend"
try {
    pip install -r requirements.txt
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Eroare la instalarea dependențelor Python" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ".."

# Instalează dependențele frontend
Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Blue
Set-Location "frontend"
try {
    npm install
    Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Eroare la instalarea dependențelor Node.js" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ".."

# Instalează dependențele mobile
Write-Host "📱 Installing Mobile dependencies..." -ForegroundColor Blue
Set-Location "mobile"
try {
    npm install
    Write-Host "✅ Mobile dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Eroare la instalarea dependențelor Mobile" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ".."

Write-Host ""
Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Start database and Redis: docker-compose up -d postgres redis" -ForegroundColor White
Write-Host "3. Start backend: cd backend && python main.py" -ForegroundColor White
Write-Host "4. Start frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "5. Start mobile: cd mobile && npx expo start" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation: docs/ARCHITECTURE.md" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
