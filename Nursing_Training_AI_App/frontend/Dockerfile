# 🐳 Dockerfile pentru Frontend Next.js
FROM node:18-alpine

# Setează directorul de lucru
WORKDIR /app

# Copiază package.json și package-lock.json
COPY package*.json ./

# Instalează dependențele
RUN npm ci --only=production

# Copiază codul sursă
COPY . .

# Construiește aplicația
RUN npm run build

# Expune portul
EXPOSE 3000

# Comanda de start
CMD ["npm", "start"]
