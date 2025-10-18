# 📥 Ghid Complet - Descărcare și Setup Proiect

## Cum să Descarci Întregul Proiect pe PC

### **Metoda 1: Clone din GitHub (RECOMANDAT)** ✅

#### **Pasul 1: Deschide Terminal/PowerShell**
```powershell
# Navighează la locația dorită (exemplu: Desktop)
cd C:\Users\[username]\Desktop

# Sau pe drive-ul tău curent
cd J:\
```

#### **Pasul 2: Clone Repository-ul**
```powershell
git clone https://github.com/Ginx172/Nursing-Training-AI.git

# Intră în folder
cd Nursing-Training-AI
```

#### **Pasul 3: Verifică că ai tot**
```powershell
# Verifică branch-ul
git status

# Vezi toate fișierele
dir
```

---

## 📦 **Ce ai descărcat (Structura Completă)**

```
Nursing-Training-AI/
│
├── 📁 Healthcare_Knowledge_Base/          # Baza de cunoștințe medicale
│   ├── Clinical_Protocols/
│   │   ├── NICE_Guidelines/
│   │   ├── AMU_MAU/
│   │   ├── Emergency_AE/
│   │   ├── ICU_Critical_Care/
│   │   ├── Maternity/
│   │   ├── Mental_Health/
│   │   └── Pediatrics/
│   └── faiss_indexes/
│
├── 📁 Nursing_Interviews_AI_model/        # Modele AI și RAG
│   ├── rag_engine/
│   ├── mcp_server/
│   └── data/processed_text/
│
├── 📁 Nursing_Training_AI_App/            # Aplicația Principală
│   │
│   ├── 📁 backend/                        # Backend API (FastAPI)
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── questions.py
│   │   │   ├── analytics.py
│   │   │   ├── admin.py
│   │   │   ├── payments.py
│   │   │   ├── sso.py
│   │   │   └── tts.py                     # 🎤 Premium Voices API
│   │   │
│   │   ├── services/
│   │   │   ├── tts_service.py             # ⭐ ElevenLabs, Azure, Google TTS
│   │   │   ├── sso_service.py
│   │   │   ├── mfa_service.py
│   │   │   ├── stripe_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── gdpr_service.py
│   │   │   ├── webhook_service.py
│   │   │   ├── bi_integration_service.py
│   │   │   └── organization_service.py
│   │   │
│   │   ├── core/
│   │   │   ├── encryption.py
│   │   │   ├── rbac.py
│   │   │   ├── database.py
│   │   │   ├── cache.py
│   │   │   └── multi_tenancy.py
│   │   │
│   │   ├── data/
│   │   │   ├── question_banks/            # 📝 Peste 15,000 întrebări
│   │   │   │   ├── nhs/
│   │   │   │   ├── private_healthcare/
│   │   │   │   ├── care_homes/
│   │   │   │   ├── community_healthcare/
│   │   │   │   └── primary_care/
│   │   │   │
│   │   │   ├── uk_healthcare_sectors.json
│   │   │   └── nhs_band_expectations.json
│   │   │
│   │   ├── scripts/
│   │   │   └── generate_all_uk_healthcare_questions.py
│   │   │
│   │   ├── requirements.txt               # 📦 Toate dependențele Python
│   │   └── main.py
│   │
│   ├── 📁 mobile/                         # Mobile App (React Native + Expo)
│   │   ├── screens/
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── RegisterScreen.tsx
│   │   │   ├── DashboardScreen.tsx
│   │   │   ├── SpecialtiesScreen.tsx
│   │   │   ├── QuestionsScreen.tsx
│   │   │   ├── ResultsScreen.tsx
│   │   │   ├── ProfileScreen.tsx
│   │   │   ├── SubscriptionScreen.tsx
│   │   │   └── VoiceSettingsScreen.tsx    # 🎤 Voice Settings
│   │   │
│   │   ├── services/
│   │   │   ├── AudioService.ts            # ⭐ Premium TTS Integration
│   │   │   ├── OfflineService.ts
│   │   │   └── NotificationService.ts
│   │   │
│   │   ├── context/
│   │   │   ├── AppContext.tsx
│   │   │   └── ThemeContext.tsx
│   │   │
│   │   ├── package.json
│   │   ├── App.tsx
│   │   └── README.md
│   │
│   ├── 📁 k8s/                            # Kubernetes Deployment
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── helm/
│   │   ├── monitoring/
│   │   └── backup/
│   │
│   ├── 📁 sdk/                            # SDKs pentru integrare
│   │   ├── python/
│   │   └── javascript/
│   │
│   ├── 📁 infrastructure/
│   │   └── cloudflare-config.tf
│   │
│   └── docker-compose.yml
│
├── 📁 .github/
│   └── workflows/
│       └── ci-cd.yml                      # CI/CD Pipeline
│
├── 📄 README.md                           # Documentație principală
├── 📄 ENTERPRISE_ROADMAP.md               # Plan Enterprise
├── 📄 ENTERPRISE_FEATURES_COMPLETE.md     # Features implementate
├── 📄 DEPLOYMENT.md                       # Ghid deployment
├── 📄 DOWNLOAD_SETUP_GUIDE.md            # 📥 Acest fișier
├── 📄 .gitignore
└── 📄 proiecare faze de dezvoltare.txt   # Planul pe faze
```

---

## 🚀 **Setup Local - Pas cu Pas**

### **1. Setup Backend (Python FastAPI)**

#### **Instalare Python Dependencies:**
```powershell
# Navighează la backend
cd Nursing_Training_AI_App/backend

# Creează virtual environment
python -m venv venv

# Activează venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalează toate dependențele
pip install -r requirements.txt
```

#### **Configurare Environment Variables:**
Creează fișier `.env` în `backend/`:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/nursing_ai

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key-here

# Stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Premium TTS (Optional - pentru voci premium)
ELEVENLABS_API_KEY=your_elevenlabs_key
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=uksouth
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Sentry (Monitoring)
SENTRY_DSN=your-sentry-dsn
```

#### **Start Backend:**
```powershell
# Run cu uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend va rula la: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

---

### **2. Setup Mobile App (React Native + Expo)**

#### **Instalare Node.js Dependencies:**
```powershell
# Navighează la mobile
cd Nursing_Training_AI_App/mobile

# Instalează dependențele
npm install
```

#### **Start Expo Dev Server:**
```powershell
# Start development server
npx expo start

# Sau pentru clear cache
npx expo start -c
```

#### **Rulează pe Device/Emulator:**
- **iOS**: Apasă `i` în terminal (necesită macOS + Xcode)
- **Android**: Apasă `a` în terminal (necesită Android Studio)
- **Physical Device**: Scanează QR code cu Expo Go app

---

### **3. Setup Database (PostgreSQL)**

#### **Instalare PostgreSQL:**
```powershell
# Download de pe: https://www.postgresql.org/download/windows/
# Sau folosește Docker:
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=nursing_ai \
  -p 5432:5432 \
  postgres:15
```

#### **Create Tables:**
```sql
-- Conectează-te la database și rulează schema.sql
psql -U postgres -d nursing_ai -f backend/database/schema.sql
```

---

### **4. Setup Redis (Caching)**

```powershell
# Docker (cel mai simplu)
docker run -d --name redis -p 6379:6379 redis:7

# Sau instalează local de pe: https://redis.io/download
```

---

## 🔄 **Sincronizare continuă cu GitHub**

### **Pull ultimele modificări:**
```powershell
# Asigură-te că ești în main branch
git checkout main

# Pull changes
git pull origin main
```

### **Push modificările tale:**
```powershell
# Verifică ce ai modificat
git status

# Add files
git add .

# Commit
git commit -m "Descriere modificări"

# Push
git push origin main
```

### **Sincronizare automată (Optional):**
Creează script PowerShell `sync.ps1`:
```powershell
# sync.ps1
Write-Host "🔄 Sincronizare cu GitHub..." -ForegroundColor Cyan

# Pull latest
git pull origin main

# Add all changes
git add .

# Check if there are changes
$changes = git status --porcelain
if ($changes) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Auto-sync: $timestamp"
    git push origin main
    Write-Host "✅ Sincronizare completă!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Nu există modificări de sincronizat" -ForegroundColor Yellow
}
```

Rulează:
```powershell
.\sync.ps1
```

---

## 📦 **Backup Complet (Optional)**

### **Creare Archive ZIP:**
```powershell
# Compress întregul proiect
Compress-Archive -Path "Nursing-Training-AI" -DestinationPath "Nursing-Training-AI-Backup-$(Get-Date -Format 'yyyy-MM-dd').zip"
```

### **Backup pe Drive Extern:**
```powershell
# Copy folder complet
Copy-Item -Path "Nursing-Training-AI" -Destination "D:\Backups\" -Recurse
```

---

## 🆘 **Troubleshooting**

### **Problem: Git Clone slow/fails**
```powershell
# Clone fără history (mai rapid)
git clone --depth 1 https://github.com/Ginx172/Nursing-Training-AI.git
```

### **Problem: Large files not downloading**
Git LFS pentru fișiere mari:
```powershell
git lfs install
git lfs pull
```

### **Problem: Permission denied**
```powershell
# Re-authenticate GitHub
gh auth login
```

---

## 📊 **Verificare Setup**

### **Checklist Setup Complet:**
```powershell
# ✅ Git repository cloned
git status

# ✅ Backend dependencies installed
cd Nursing_Training_AI_App/backend
pip list

# ✅ Mobile dependencies installed
cd ../mobile
npm list

# ✅ Database running
psql -U postgres -c "SELECT version();"

# ✅ Redis running
redis-cli ping
# Response: PONG

# ✅ Backend running
curl http://localhost:8000/health

# ✅ Mobile app running
# Check Expo DevTools: http://localhost:19002
```

---

## 🎯 **Quick Start (TL;DR)**

```powershell
# 1. Clone
git clone https://github.com/Ginx172/Nursing-Training-AI.git
cd Nursing-Training-AI

# 2. Backend
cd Nursing_Training_AI_App/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create .env file
uvicorn main:app --reload

# 3. Mobile (new terminal)
cd Nursing_Training_AI_App/mobile
npm install
npx expo start

# 4. Open browser
# Backend API: http://localhost:8000/docs
# Mobile: Scan QR code with Expo Go app
```

---

## 📞 **Contact & Support**

- **GitHub Issues**: https://github.com/Ginx172/Nursing-Training-AI/issues
- **Documentation**: https://github.com/Ginx172/Nursing-Training-AI#readme

---

**✅ Acum ai tot proiectul pe PC-ul tău!** 🎉

