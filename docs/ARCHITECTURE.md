# Mimari Dokümantasyonu

## Genel Bakış

Aieditor, OpenHands'den ilham alınarak geliştirilmiş modern bir AI kod editörüdür. Mikroservis mimarisi kullanarak ölçeklenebilir ve modüler bir yapı sunar.

## Sistem Mimarisi

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   LLM APIs     │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│ OpenAI/Claude   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │                       │                       
         ▼                       ▼                       
┌─────────────────┐    ┌─────────────────┐              
│   WebSocket     │    │     Redis       │              
│   Connection    │    │    (Cache)      │              
└─────────────────┘    └─────────────────┘              
                                │                        
                                ▼                        
                    ┌─────────────────┐                 
                    │ Docker Sandbox  │                 
                    │  (Execution)    │                 
                    └─────────────────┘                 
```

## Bileşenler

### Frontend (React/TypeScript)
- **Teknolojiler:** React 18, TypeScript, Material-UI, Monaco Editor
- **Özellikler:**
  - Real-time chat interface
  - Code syntax highlighting
  - File explorer
  - WebSocket connection management
  - Responsive design

### Backend (Python/FastAPI)
- **Teknolojiler:** FastAPI, WebSockets, Redis, Docker
- **Bileşenler:**
  - **Agent Manager:** AI agent'ları yönetir
  - **Session Manager:** Kullanıcı oturumlarını yönetir
  - **LLM Provider:** Çeşitli LLM API'larını yönetir
  - **WebSocket Handler:** Real-time iletişimi sağlar

### AI Agents
- **CodeAgent:** Kod yazma ve analiz
- **TerminalAgent:** Terminal komutları çalıştırma
- **FileAgent:** Dosya işlemleri

### LLM Providers
- **OpenAI:** GPT-4, GPT-3.5-turbo
- **Anthropic:** Claude-3 Sonnet, Haiku

## Veri Akışı

1. **Kullanıcı Etkileşimi:**
   - Kullanıcı frontend'de mesaj yazar
   - WebSocket üzerinden backend'e gönderilir

2. **Mesaj İşleme:**
   - Session Manager oturumu günceller
   - Agent Manager uygun agent'ı seçer
   - Agent, LLM Provider ile iletişime geçer

3. **Yanıt Üretimi:**
   - LLM'den yanıt alınır
   - Gerekirse kod çalıştırılır (sandbox)
   - Sonuç WebSocket ile frontend'e gönderilir

## Güvenlik

### Sandbox Ortamı
- Docker container'da izole çalıştırma
- Sınırlı dosya sistemi erişimi
- Network izolasyonu
- Resource limitleri

### API Güvenliği
- CORS koruması
- Rate limiting
- Input validation
- Error handling

## Ölçeklenebilirlik

### Horizontal Scaling
- Stateless backend design
- Redis ile session paylaşımı
- Load balancer desteği

### Performance
- Async/await pattern
- Connection pooling
- Caching strategies
- Lazy loading

## Geliştirme Prensipleri

### Clean Architecture
- Separation of concerns
- Dependency injection
- Interface segregation

### Code Quality
- Type hints (Python)
- TypeScript (Frontend)
- Unit testing
- Code formatting (Black, Prettier)

### Error Handling
- Graceful degradation
- Comprehensive logging
- User-friendly error messages
- Retry mechanisms