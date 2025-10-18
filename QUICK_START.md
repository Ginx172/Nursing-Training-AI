# 🚀 QUICK START - Nursing Training AI

## Descărcare Rapidă și Setup în 5 Minute

### **📥 Step 1: Descarcă Proiectul**

```powershell
# Clone repository-ul
git clone https://github.com/Ginx172/Nursing-Training-AI.git

# Intră în folder
cd Nursing-Training-AI
```

---

### **⚙️ Step 2: Setup Backend**

```powershell
# Navighează la backend
cd Nursing_Training_AI_App/backend

# Creează virtual environment
python -m venv venv

# Activează (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalează dependencies
pip install -r requirements.txt
```

**Creează fișier `.env`:**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/nursing_ai
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
```

**Start backend:**
```powershell
uvicorn main:app --reload
```

✅ Backend: http://localhost:8000
✅ API Docs: http://localhost:8000/docs

---

### **📱 Step 3: Setup Mobile App**

```powershell
# Navighează la mobile (terminal nou)
cd Nursing_Training_AI_App/mobile

# Instalează dependencies
npm install

# Start Expo
npx expo start
```

✅ Scanează QR code cu **Expo Go** app (iOS/Android)

---

### **🔄 Step 4: Sincronizare cu GitHub**

#### **Metoda 1: Manual**
```powershell
# Pull ultimele modificări
git pull origin main

# Add modificările tale
git add .

# Commit
git commit -m "Modificările mele"

# Push
git push origin main
```

#### **Metoda 2: Script Automat (RECOMANDAT)** ⭐
```powershell
# Rulează script-ul de sincronizare
.\SYNC_SCRIPT.ps1

# Sau cu mesaj custom
.\SYNC_SCRIPT.ps1 -CommitMessage "Am adăugat feature X"

# Sau complet automat
.\SYNC_SCRIPT.ps1 -AutoCommit
```

---

## 📁 **Structura Proiectului**

```
Nursing-Training-AI/
│
├── 📁 Healthcare_Knowledge_Base/      # Baza de cunoștințe medicale
├── 📁 Nursing_Interviews_AI_model/    # Modele AI (RAG, MCP)
│
├── 📁 Nursing_Training_AI_App/
│   ├── 📁 backend/                    # FastAPI Backend
│   │   ├── api/                       # API Endpoints
│   │   ├── services/                  # Business Logic
│   │   │   └── tts_service.py         # 🎤 Premium Voices
│   │   ├── core/                      # Core functionality
│   │   ├── data/question_banks/       # 15,000+ întrebări
│   │   └── requirements.txt
│   │
│   ├── 📁 mobile/                     # React Native + Expo
│   │   ├── screens/                   # UI Screens
│   │   ├── services/
│   │   │   └── AudioService.ts        # 🎤 Premium TTS
│   │   └── package.json
│   │
│   ├── 📁 k8s/                        # Kubernetes configs
│   └── 📁 sdk/                        # Python & JS SDKs
│
├── 📄 README.md
├── 📄 DOWNLOAD_SETUP_GUIDE.md         # Ghid detaliat
├── 📄 QUICK_START.md                  # 👈 Acest fișier
├── 📄 SYNC_SCRIPT.ps1                 # Script sincronizare
└── 📄 .gitignore
```

---

## 🎯 **Features Principale**

### **✅ Implementat Complet**

- ✅ **15,000+ Întrebări** pentru toate sectoarele UK Healthcare
- ✅ **Premium Voices** 🎤 (ElevenLabs, Azure, Google TTS)
- ✅ **Mobile App** (React Native + Expo)
- ✅ **Backend API** (FastAPI + PostgreSQL + Redis)
- ✅ **Stripe Payments** (4 planuri: Demo, Basic, Professional, Enterprise)
- ✅ **SSO & MFA** (Azure AD, Okta, SAML)
- ✅ **Multi-Tenancy** (Schema-per-tenant)
- ✅ **GraphQL API** + REST API
- ✅ **Kubernetes Ready** + Helm Charts
- ✅ **CI/CD Pipeline** (GitHub Actions)
- ✅ **Monitoring** (Prometheus + Grafana + Sentry)
- ✅ **Analytics Dashboard**
- ✅ **Admin Panel**
- ✅ **GDPR Compliance**
- ✅ **Offline Mode**
- ✅ **Push Notifications**
- ✅ **Dark Mode**

---

## 🎤 **Premium Voices - Cum Funcționează**

### **3 Provideri TTS:**

1. **ElevenLabs** ⭐⭐⭐⭐⭐
   - Cel mai natural, imposibil de distins de om real
   - 8 voci britanice (Sarah, Dorothy, Arnold, Adam, etc.)
   - £0.30 per 1,000 caractere

2. **Azure Neural TTS** ⭐⭐⭐⭐
   - Excelent, foarte clar
   - 7 voci britanice (Sonia, Ryan, Libby, etc.)
   - £4 per 1M caractere

3. **Google WaveNet** ⭐⭐⭐⭐
   - Foarte bună calitate
   - 5 voci britanice
   - £12 per 1M caractere

### **Mobile Integration:**
```typescript
import AudioService from './services/AudioService';

const audioService = AudioService.getInstance();

// Play cu voce premium
await audioService.speakQuestion(
  "A patient presents with chest pain...",
  {
    provider: 'elevenlabs',
    gender: 'female',
    accent: 'rp',
    age: 'young'
  }
);
```

---

## 📊 **Database Setup (Optional)**

### **PostgreSQL cu Docker:**
```powershell
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=nursing_ai \
  -p 5432:5432 \
  postgres:15
```

### **Redis cu Docker:**
```powershell
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7
```

---

## 🔐 **Environment Variables**

Creează `.env` în `backend/`:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/nursing_ai

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key-here-min-32-chars

# Stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Premium TTS (Optional)
ELEVENLABS_API_KEY=your_key
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=uksouth
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Sentry
SENTRY_DSN=your-sentry-dsn
```

---

## 🆘 **Troubleshooting**

### **Git Clone lent?**
```powershell
git clone --depth 1 https://github.com/Ginx172/Nursing-Training-AI.git
```

### **Permission denied?**
```powershell
gh auth login
```

### **Port deja ocupat?**
```powershell
# Backend pe alt port
uvicorn main:app --reload --port 8001
```

---

## 📚 **Documentație Completă**

- **Setup Detaliat**: [DOWNLOAD_SETUP_GUIDE.md](DOWNLOAD_SETUP_GUIDE.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Enterprise Features**: [ENTERPRISE_FEATURES_COMPLETE.md](ENTERPRISE_FEATURES_COMPLETE.md)
- **API Docs**: http://localhost:8000/docs (după start backend)

---

## 🔗 **Links Utile**

- **GitHub Repository**: https://github.com/Ginx172/Nursing-Training-AI
- **Issues**: https://github.com/Ginx172/Nursing-Training-AI/issues
- **ElevenLabs**: https://elevenlabs.io
- **Expo Go**: https://expo.dev/client

---

## ✅ **Checklist Setup**

- [ ] Git clone complet
- [ ] Backend dependencies instalate (`pip install -r requirements.txt`)
- [ ] Mobile dependencies instalate (`npm install`)
- [ ] `.env` creat cu configurații
- [ ] PostgreSQL running (optional)
- [ ] Redis running (optional)
- [ ] Backend started (`uvicorn main:app --reload`)
- [ ] Mobile app started (`npx expo start`)
- [ ] Expo Go app instalat pe telefon
- [ ] QR code scanat și app rulează pe telefon

---

**🎉 Gata! Proiectul rulează local pe PC-ul tău!**

Pentru sincronizare cu GitHub, folosește:
```powershell
.\SYNC_SCRIPT.ps1
```

