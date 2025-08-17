FROM node:18-alpine

WORKDIR /app

# Package.json'ı kopyala ve bağımlılıkları yükle
COPY package*.json ./
RUN npm install

# Uygulama kodunu kopyala
COPY . .

# Port'u aç
EXPOSE 3000

# Development server'ı başlat
CMD ["npm", "start"]