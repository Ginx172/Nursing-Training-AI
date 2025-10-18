# 🏗️ Architecture Documentation - Nursing Training AI

## 📋 **OVERVIEW**

Aplicația Nursing Training AI este o platformă de training medical AI pentru personalul NHS, construită cu o arhitectură modulară și scalabilă.

## 🎯 **ARHITECTURA GENERALĂ**

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                            │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Web App       │   Mobile App    │   Desktop App           │
│   (React)       │   (React Native)│   (Electron)            │
└─────────────────┴─────────────────┴─────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY                             │
│                   (FastAPI)                                │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                           │
├─────────────────┬─────────────────┬─────────────────────────┤
│   RAG Service   │   MCP Service   │   AI Service            │
│   (Retrieval)   │   (Context)     │   (GPT-4)               │
└─────────────────┴─────────────────┴─────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                              │
├─────────────────┬─────────────────┬─────────────────────────┤
│   PostgreSQL    │   Redis         │   File Storage          │
│   (Main DB)     │   (Cache)       │   (Uploads)             │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## 🔧 **COMPONENTE PRINCIPALE**

### **1. Backend (FastAPI)**
- **API Gateway:** Endpoint-uri REST pentru toate serviciile
- **Authentication:** JWT-based authentication
- **Authorization:** Role-based access control
- **Rate Limiting:** Protecție împotriva abuzurilor
- **CORS:** Cross-origin resource sharing

### **2. Frontend (React + Next.js)**
- **Web Application:** Interfața web principală
- **Responsive Design:** Compatibil cu toate dispozitivele
- **State Management:** React Query pentru state management
- **UI Components:** Componente reutilizabile cu Tailwind CSS

### **3. Mobile (React Native + Expo)**
- **Cross-platform:** iOS și Android
- **Native Features:** Acces la funcționalități native
- **Offline Support:** Funcționalitate offline limitată
- **Push Notifications:** Notificări push pentru training

### **4. Database (PostgreSQL)**
- **Main Database:** Stocarea datelor principale
- **ACID Compliance:** Transacții sigure
- **Full-text Search:** Căutare în text
- **JSON Support:** Stocarea datelor structurate

### **5. Cache (Redis)**
- **Session Storage:** Stocarea sesiunilor
- **API Caching:** Cache pentru API-uri
- **Rate Limiting:** Limite de rate
- **Real-time Data:** Date în timp real

## 🚀 **SERVICII AI**

### **RAG System (Retrieval-Augmented Generation)**
```python
# Exemplu de implementare
class RAGService:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_store = FAISS()
    
    def retrieve(self, query: str, k: int = 5):
        # Căutare semantică
        query_embedding = self.embedder.encode(query)
        results = self.vector_store.search(query_embedding, k)
        return results
    
    def generate(self, query: str, context: str):
        # Generare răspuns cu context
        prompt = f"Context: {context}\nQuestion: {query}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

### **MCP System (Model Context Protocol)**
```python
# Exemplu de implementare
class MCPService:
    def __init__(self):
        self.context_manager = ContextManager()
        self.model_router = ModelRouter()
    
    def process(self, input_data: dict):
        # Gestionarea contextului
        context = self.context_manager.get_context(input_data)
        
        # Routing către modelul potrivit
        model = self.model_router.select_model(input_data)
        
        # Procesarea cu modelul selectat
        result = model.process(context, input_data)
        return result
```

## 📊 **FLUXUL DE DATE**

### **1. Autentificare**
```
Client → API Gateway → Auth Service → Database
                ↓
            JWT Token → Client
```

### **2. Training Session**
```
Client → API Gateway → Training Service → RAG Service
                ↓
            Questions → Client
                ↓
            Answers → AI Service → Feedback → Client
```

### **3. Demo System**
```
Client → API Gateway → Demo Service → Question Bank
                ↓
            Demo Questions → Client
                ↓
            Answers → AI Service → Recommendations → Client
```

## 🔒 **SECURITATE**

### **1. Authentication**
- JWT tokens cu expirare
- Refresh tokens pentru reînnoire
- Secure cookie storage

### **2. Authorization**
- Role-based access control
- Permission-based endpoints
- Resource-level permissions

### **3. Data Protection**
- Encryption at rest
- Encryption in transit (HTTPS)
- PII data anonymization

### **4. API Security**
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

## 📈 **SCALABILITATE**

### **1. Horizontal Scaling**
- Load balancers
- Multiple API instances
- Database read replicas
- CDN pentru assets statice

### **2. Caching Strategy**
- Redis pentru cache
- CDN pentru assets
- Database query caching
- API response caching

### **3. Database Optimization**
- Indexing strategy
- Query optimization
- Connection pooling
- Read/write splitting

## 🚀 **DEPLOYMENT**

### **1. Development**
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Mobile
cd mobile
npm install
npx expo start
```

### **2. Production**
```bash
# Docker Compose
docker-compose up -d

# Kubernetes (viitor)
kubectl apply -f k8s/
```

### **3. Monitoring**
- Application logs
- Performance metrics
- Error tracking
- User analytics

## 🔄 **CI/CD PIPELINE**

### **1. Development**
- Git hooks pentru pre-commit
- Automated testing
- Code quality checks

### **2. Staging**
- Automated deployment
- Integration testing
- Performance testing

### **3. Production**
- Blue-green deployment
- Rollback strategy
- Health checks

## 📱 **CROSS-PLATFORM SUPPORT**

### **1. Web (React + Next.js)**
- Responsive design
- PWA support
- Offline functionality

### **2. Mobile (React Native + Expo)**
- iOS și Android
- Native performance
- Push notifications

### **3. Desktop (Electron)**
- Windows, Mac, Linux
- Native integration
- Offline support

---

*Documentația arhitecturii - Ultima actualizare: 29 Septembrie 2024*
