# 🤖 Install AI Dependencies Script
# Script pentru instalarea dependențelor AI necesare

Write-Host "🤖 Installing AI Dependencies for Nursing Training AI..." -ForegroundColor Green
Write-Host ""

# Verifică dacă Python este instalat
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python nu este instalat! Te rog instalează Python 3.11+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Navighează la directorul backend
$backendPath = ".\Nursing_Training_AI_App\backend"
if (Test-Path $backendPath) {
    Set-Location $backendPath
    Write-Host "📁 Changed to backend directory: $backendPath" -ForegroundColor Blue
} else {
    Write-Host "❌ Backend directory not found: $backendPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Creează virtual environment dacă nu există
if (-not (Test-Path "venv")) {
    Write-Host "🐍 Creating virtual environment..." -ForegroundColor Blue
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activează virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️ Upgrading pip..." -ForegroundColor Blue
python -m pip install --upgrade pip

# Instalează dependențele de bază
Write-Host "📦 Installing basic dependencies..." -ForegroundColor Blue
pip install -r requirements.txt

# Instalează dependențele AI suplimentare
Write-Host "🤖 Installing AI-specific dependencies..." -ForegroundColor Blue

# Instalează PyTorch (CPU version pentru compatibilitate Windows)
Write-Host "🔥 Installing PyTorch..." -ForegroundColor Blue
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Instalează FAISS
Write-Host "🔍 Installing FAISS..." -ForegroundColor Blue
pip install faiss-cpu

# Instalează Sentence Transformers
Write-Host "📝 Installing Sentence Transformers..." -ForegroundColor Blue
pip install sentence-transformers

# Instalează Transformers
Write-Host "🔄 Installing Transformers..." -ForegroundColor Blue
pip install transformers

# Instalează dependențe suplimentare
Write-Host "📚 Installing additional dependencies..." -ForegroundColor Blue
pip install numpy==1.24.3
pip install aiofiles==23.2.1
pip install scikit-learn
pip install nltk

# Verifică instalarea
Write-Host "✅ Verifying installation..." -ForegroundColor Blue
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import faiss; print('FAISS: OK')"
python -c "import sentence_transformers; print('Sentence Transformers: OK')"
python -c "import transformers; print('Transformers: OK')"

Write-Host ""
Write-Host "🎉 AI Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Set your OpenAI API key in .env file" -ForegroundColor White
Write-Host "2. Run the AI services test: python test_ai_services.py" -ForegroundColor White
Write-Host "3. Start the backend: python main.py" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
