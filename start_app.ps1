# Nursing Training AI - Start Application Script
# PowerShell script to start the complete application

Write-Host "🏥 Starting Nursing Training AI Application..." -ForegroundColor Green

# Change to backend directory
Set-Location -Path "J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend"

Write-Host "📁 Changed to backend directory" -ForegroundColor Yellow

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python first." -ForegroundColor Red
    exit 1
}

# Install required packages if needed
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
python -c "import fastapi, uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    pip install fastapi uvicorn python-multipart
}

# Start the server
Write-Host "🚀 Starting FastAPI server on port 8002..." -ForegroundColor Green
Write-Host "📱 Frontend will open automatically in your browser" -ForegroundColor Cyan
Write-Host "🔗 API Documentation: http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Red

# Start server in background
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main_working:app", "--host", "0.0.0.0", "--port", "8002", "--reload" -WindowStyle Minimized

# Wait a moment for server to start
Start-Sleep -Seconds 3

# Open frontend
Write-Host "🌐 Opening frontend..." -ForegroundColor Green
Start-Process "J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\frontend\index.html"

Write-Host "✅ Application started successfully!" -ForegroundColor Green
Write-Host "🎯 You can now test the application in your browser" -ForegroundColor Cyan