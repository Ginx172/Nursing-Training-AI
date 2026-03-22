# Startup Script for Nursing Training AI
# This script launches both Backend and Frontend components

Write-Host "🏥 Starting Nursing Training AI System..." -ForegroundColor Cyan

# 1. Start Backend
Write-Host "🚀 Starting Backend (FastAPI)..." -ForegroundColor Yellow
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd 'j:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend'; .\venv\Scripts\python main.py" -WindowStyle Normal

# 2. Start Frontend
Write-Host "🎨 Starting Frontend (Next.js)..." -ForegroundColor Yellow
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd 'j:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\frontend'; npm run dev" -WindowStyle Normal

# 3. Open Browser
Write-Host "🌐 Opening Dashboard..." -ForegroundColor Green
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000/dashboard"

Write-Host "✅ System startup initiated!" -ForegroundColor Green
Write-Host "   - Backend: http://localhost:8000/docs"
Write-Host "   - Frontend: http://localhost:3000"
Write-Host "   - API Status: http://localhost:8000/api/health"
