# 🏥 Nursing Training AI - Aplicație de Training Medical

## 📋 **DESCRIEREA PROIECTULUI**

Aplicație de training medical AI pentru personalul NHS (Band 2-8) cu funcționalități RAG și MCP, accesibilă pe Windows, Mac, iOS, Android și Linux.

## 🏗️ **ARHITECTURA PROIECTULUI**

```
Nursing_Training_AI_App/
├── backend/                 # Backend FastAPI
│   ├── api/                # API endpoints
│   ├── core/               # Logica de bază
│   ├── services/           # Servicii (RAG, MCP, AI)
│   ├── models/             # Modele de date
│   ├── utils/              # Utilitare
│   └── config/             # Configurări
├── frontend/               # Frontend React
│   ├── src/                # Cod sursă
│   ├── components/         # Componente React
│   ├── pages/              # Pagini
│   ├── hooks/              # Custom hooks
│   ├── services/           # Servicii API
│   ├── utils/              # Utilitare
│   └── assets/             # Resurse statice
├── mobile/                 # Aplicație mobilă React Native
│   ├── src/                # Cod sursă
│   ├── components/         # Componente mobile
│   ├── screens/            # Ecrane
│   ├── services/           # Servicii API
│   ├── utils/              # Utilitare
│   └── assets/             # Resurse mobile
├── database/               # Baza de date
│   ├── migrations/         # Migrări
│   ├── seeds/              # Date inițiale
│   └── schemas/            # Scheme de date
├── docs/                   # Documentație
├── tests/                  # Teste
└── README.md              # Acest fișier
```

## 🎯 **FUNCȚIONALITĂȚI PRINCIPALE**

### **1. Sistem Demo (2-3 întrebări)**
- Scenarii clinice de bază
- Situații de management/leadership
- Cazuri complexe specifice specializării
- Feedback personalizat și recomandări

### **2. Training Personalizat pe Band**
- **Band 6:** Senior Staff Nurse
- **Band 7:** Clinical Nurse Specialist  
- **Band 8A:** Advanced Nurse Practitioner
- Conținut adaptat cerințelor specifice

### **3. Teste de Calcule**
- Calculul dozelor de medicamente
- Calculul fluidelor
- Calculul nutrițional
- Conversii între unități

### **4. Sisteme AI**
- **RAG (Retrieval-Augmented Generation):** Căutare și generare de conținut
- **MCP (Model Context Protocol):** Protocol pentru contextul modelelor

## 🛠️ **TECHNOLOGII FOLOSITE**

### **Backend:**
- **FastAPI** - Framework web Python
- **PostgreSQL** - Baza de date principală
- **Redis** - Cache și sesiuni
- **Celery** - Task-uri asincrone
- **Docker** - Containerizare

### **Frontend:**
- **React** - Framework UI
- **Next.js** - Framework React
- **Tailwind CSS** - Styling
- **TypeScript** - Tipizare statică

### **Mobile:**
- **React Native** - Aplicații mobile cross-platform
- **Expo** - Platforma de dezvoltare

### **AI/ML:**
- **FAISS** - Căutare semantică
- **Sentence Transformers** - Embeddings
- **OpenAI GPT-4** - Feedback AI
- **Whisper** - Speech-to-text

## 🚀 **INSTALARE ȘI RULARE**

### **Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### **Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### **Mobile:**
```bash
cd mobile
npm install
npx expo start
```

## 📱 **PLATFORME SUPPORTATE**

- ✅ **Windows** (Desktop + Web)
- ✅ **Mac** (Desktop + Web)
- ✅ **iOS** (Mobile)
- ✅ **Android** (Mobile)
- ✅ **Linux** (Desktop + Web)

## 💰 **MODEL COMERCIAL**

### **Demo (Gratuit):**
- 2-3 întrebări pe lună
- Feedback de bază
- Acces limitat la conținut

### **Tier 1 (Basic):**
- Acces complet la conținut text
- Teste nelimitate
- Feedback detaliat

### **Tier 2 (Professional):**
- Toate funcționalitățile Tier 1
- Conținut personalizat pe specializare
- Rapoarte de progres

### **Tier 3 (Enterprise):**
- Toate funcționalitățile
- Managementul echipei
- Analytics avansate

## 🔧 **DEZVOLTARE**

### **Faza 1: Schelet (CURRENT)**
- [x] Structura proiectului
- [ ] Configurarea backend-ului
- [ ] Configurarea frontend-ului
- [ ] Schema bazei de date

### **Faza 2: Module de Bază**
- [ ] Sistemul RAG
- [ ] Sistemul MCP
- [ ] Modulul demo
- [ ] Modulele specifice pe band

### **Faza 3: Integrare**
- [ ] Interacțiunea între module
- [ ] Sistemul de plăți
- [ ] Deployment

## 📞 **CONTACT**

Pentru întrebări sau suport, contactați echipa de dezvoltare.

---

*Ultima actualizare: 29 Septembrie 2024*
