# 🚀 Quick Start Guide - Nursing Training AI

## 📋 **INSTALARE RAPIDĂ**

### **1. Instalare Automată (Windows)**
```bash
# Rulează scriptul de instalare
.\install.bat

# Sau pentru PowerShell
.\install.ps1
```

### **2. Instalare Manuală**
```bash
# 1. Clonează repository-ul
git clone <repository-url>
cd Nursing_Training_AI_App

# 2. Creează fișierul .env
copy .env.example .env

# 3. Instalează dependențele backend
cd backend
pip install -r requirements.txt

# 4. Instalează dependențele frontend
cd ../frontend
npm install

# 5. Instalează dependențele mobile
cd ../mobile
npm install
```

## 🚀 **PORNIREA APLICAȚIEI**

### **Opțiunea 1: Pornire Automată (Recomandată)**
```bash
# Pornește toate serviciile
.\start-all.bat

# Sau pentru PowerShell
.\start-all.ps1
```

### **Opțiunea 2: Pornire Manuală**
```bash
# 1. Pornește baza de date și Redis
docker-compose up -d postgres redis

# 2. Pornește backend-ul
cd backend
python main.py

# 3. Pornește frontend-ul (în alt terminal)
cd frontend
npm run dev

# 4. Pornește mobile-ul (în alt terminal)
cd mobile
npx expo start
```

## 🌐 **ACCESAREA APLICAȚIEI**

### **Web Application**
- **URL:** http://localhost:3000
- **Platform:** Windows, Mac, Linux
- **Browser:** Chrome, Firefox, Safari, Edge

### **Mobile Application**
- **Platform:** iOS, Android
- **Method:** Expo Go app sau build nativ
- **Development:** Expo DevTools

### **API Documentation**
- **URL:** http://localhost:8000/docs
- **Type:** Swagger UI
- **Authentication:** JWT tokens

## 🔧 **CONFIGURARE**

### **1. Fișierul .env**
Editează fișierul `.env` cu configurațiile tale:
```env
# Baza de date
DATABASE_URL=postgresql://nursing_user:nursing_password@localhost:5432/nursing_training_ai

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your-openai-api-key-here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **2. Baza de Date**
```bash
# Creează baza de date
docker-compose up -d postgres

# Aplică migrările
cd backend
alembic upgrade head
```

## 📱 **FUNCȚIONALITĂȚI DISPONIBILE**

### **Demo System**
- 2-3 întrebări gratuite pe lună
- Feedback personalizat
- Recomandări de studiu

### **Training Personalizat**
- Conținut adaptat pe band NHS
- Teste de calcul
- Progres tracking

### **Sisteme AI**
- RAG (Retrieval-Augmented Generation)
- MCP (Model Context Protocol)
- Feedback AI cu GPT-4

## 🛠️ **DEZVOLTARE**

### **Backend Development**
```bash
cd backend
python main.py
# API disponibil la http://localhost:8000
```

### **Frontend Development**
```bash
cd frontend
npm run dev
# Web app disponibil la http://localhost:3000
```

### **Mobile Development**
```bash
cd mobile
npx expo start
# Mobile app disponibil prin Expo
```

## 🐛 **TROUBLESHOOTING**

### **Probleme Comune**

#### **1. Port deja folosit**
```bash
# Verifică ce proces folosește portul
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Oprește procesul
taskkill /PID <process_id> /F
```

#### **2. Docker nu pornește**
```bash
# Verifică dacă Docker Desktop rulează
docker --version

# Restart Docker Desktop
# Apoi încearcă din nou
docker-compose up -d
```

#### **3. Dependențe Python**
```bash
# Creează virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### **4. Dependențe Node.js**
```bash
# Șterge node_modules și reinstalează
rm -rf node_modules package-lock.json
npm install
```

## 📚 **DOCUMENTAȚIE**

### **Arhitectură**
- **Fișier:** `docs/ARCHITECTURE.md`
- **Conținut:** Arhitectura completă a aplicației

### **API Documentation**
- **URL:** http://localhost:8000/docs
- **Conținut:** Endpoint-uri și exemple

### **Database Schema**
- **Fișier:** `database/schemas/init.sql`
- **Conținut:** Schema bazei de date

## 🆘 **SUPORT**

### **Logs și Debugging**
```bash
# Backend logs
cd backend
python main.py --log-level debug

# Frontend logs
cd frontend
npm run dev --verbose

# Docker logs
docker-compose logs -f
```

### **Reset Complet**
```bash
# Oprește toate serviciile
docker-compose down

# Șterge volume-urile
docker-compose down -v

# Reinstalează dependențele
.\install.bat
```

---

*Quick Start Guide - Ultima actualizare: 29 Septembrie 2024*
