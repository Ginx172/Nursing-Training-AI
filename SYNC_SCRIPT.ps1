# ===============================================
# 🔄 NURSING TRAINING AI - GitHub Sync Script
# ===============================================
# Acest script sincronizează automat proiectul cu GitHub
# Autor: Nursing Training AI Team
# Versiune: 1.0

param(
    [switch]$AutoCommit = $false,
    [string]$CommitMessage = ""
)

# Culori pentru console
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor $ColorInfo
Write-Host "║   🔄 NURSING TRAINING AI - GitHub Sync       ║" -ForegroundColor $ColorInfo
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor $ColorInfo
Write-Host ""

# Verifică dacă suntem într-un repository Git
if (-not (Test-Path .git)) {
    Write-Host "❌ EROARE: Nu ești într-un repository Git!" -ForegroundColor $ColorError
    Write-Host "   Rulează: git clone https://github.com/Ginx172/Nursing-Training-AI.git" -ForegroundColor $ColorWarning
    exit 1
}

# Step 1: Check Git status
Write-Host "📊 Verificare status Git..." -ForegroundColor $ColorInfo
git status

# Step 2: Pull latest changes
Write-Host ""
Write-Host "⬇️  Pull ultimele modificări din GitHub..." -ForegroundColor $ColorInfo
$pullResult = git pull origin main 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  WARNING: Pull a întâmpinat probleme" -ForegroundColor $ColorWarning
    Write-Host $pullResult -ForegroundColor $ColorWarning
} else {
    Write-Host "✅ Pull reușit!" -ForegroundColor $ColorSuccess
}

# Step 3: Check for local changes
$changes = git status --porcelain

if (-not $changes) {
    Write-Host ""
    Write-Host "✨ Nu există modificări locale de sincronizat" -ForegroundColor $ColorSuccess
    Write-Host "   Proiectul este up-to-date cu GitHub!" -ForegroundColor $ColorSuccess
    exit 0
}

# Step 4: Display changes
Write-Host ""
Write-Host "📝 Modificări detectate:" -ForegroundColor $ColorInfo
git status --short

# Step 5: Add changes
Write-Host ""
Write-Host "➕ Adăugare fișiere modificate..." -ForegroundColor $ColorInfo
git add .

# Step 6: Commit
Write-Host ""
if ($CommitMessage -ne "") {
    # Use provided commit message
    $message = $CommitMessage
} elseif ($AutoCommit) {
    # Auto-generate commit message
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $message = "Auto-sync: $timestamp"
} else {
    # Ask user for commit message
    Write-Host "💬 Introdu mesajul pentru commit:" -ForegroundColor $ColorInfo
    Write-Host "   (sau apasă Enter pentru mesaj automat)" -ForegroundColor $ColorWarning
    $userMessage = Read-Host "   Mesaj"
    
    if ($userMessage -eq "") {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $message = "Manual sync: $timestamp"
    } else {
        $message = $userMessage
    }
}

Write-Host "📦 Commit cu mesajul: '$message'" -ForegroundColor $ColorInfo
git commit -m $message

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ EROARE la commit!" -ForegroundColor $ColorError
    exit 1
}

# Step 7: Push to GitHub
Write-Host ""
Write-Host "⬆️  Push către GitHub..." -ForegroundColor $ColorInfo
$pushResult = git push origin main 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ EROARE la push!" -ForegroundColor $ColorError
    Write-Host $pushResult -ForegroundColor $ColorError
    Write-Host ""
    Write-Host "💡 Posibile soluții:" -ForegroundColor $ColorWarning
    Write-Host "   1. Verifică autentificarea: gh auth login" -ForegroundColor $ColorWarning
    Write-Host "   2. Verifică conexiunea la internet" -ForegroundColor $ColorWarning
    Write-Host "   3. Verifică permisiunile pe repository" -ForegroundColor $ColorWarning
    exit 1
}

# Success!
Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor $ColorSuccess
Write-Host "║   ✅ SINCRONIZARE COMPLETĂ CU SUCCES!        ║" -ForegroundColor $ColorSuccess
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor $ColorSuccess
Write-Host ""
Write-Host "🔗 Repository: https://github.com/Ginx172/Nursing-Training-AI" -ForegroundColor $ColorInfo
Write-Host ""

# Display summary
$commitCount = git rev-list --count HEAD
$lastCommit = git log -1 --format="%h - %s (%cr)"

Write-Host "📊 Statistici Repository:" -ForegroundColor $ColorInfo
Write-Host "   Total commits: $commitCount" -ForegroundColor $ColorInfo
Write-Host "   Ultimul commit: $lastCommit" -ForegroundColor $ColorInfo
Write-Host ""

exit 0

