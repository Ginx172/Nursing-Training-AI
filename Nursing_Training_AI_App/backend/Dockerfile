# 🐳 Dockerfile pentru Backend FastAPI
FROM python:3.11-slim

# Setează directorul de lucru
WORKDIR /app

# Instalează dependențele sistem
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiază requirements.txt
COPY requirements.txt .

# Instalează dependențele Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiază codul sursă
COPY . .

# Creează directorul pentru uploads
RUN mkdir -p uploads

# Expune portul
EXPOSE 8000

# Comanda de start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
