# Kurulum Rehberi

## Gereksinimler

- Docker ve Docker Compose
- Git
- Node.js 18+ (geliştirme için)
- Python 3.9+ (geliştirme için)

## Hızlı Kurulum

1. **Projeyi klonlayın:**
```bash
git clone <repo-url>
cd aieditor
```

2. **Environment dosyasını oluşturun:**
```bash
cp .env.example .env
```

3. **API key'lerinizi ekleyin:**
`.env` dosyasını düzenleyip OpenAI veya Anthropic API key'inizi ekleyin:
```
OPENAI_API_KEY=your_api_key_here
# veya
ANTHROPIC_API_KEY=your_api_key_here
```

4. **Uygulamayı başlatın:**
```bash
make setup
```

5. **Tarayıcıda açın:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Manuel Kurulum

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Redis

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

## Geliştirme Ortamı

```bash
# Development modunda başlat
make dev

# Logları izle
make logs

# Testleri çalıştır
make test-backend
make test-frontend

# Kod kalitesi kontrolü
make lint-backend
make lint-frontend
```

## Sorun Giderme

### Port Çakışması
Eğer 3000 veya 8000 portları kullanılıyorsa, docker-compose.yml dosyasında port ayarlarını değiştirin.

### API Key Hatası
`.env` dosyasında API key'inizin doğru olduğundan emin olun.

### Docker Sorunları
```bash
# Container'ları temizle
make clean

# Yeniden oluştur
make build
make up
```