# 🤖 Aieditor - AI-Powered Code Editor

Aieditor, OpenHands'den ilham alınarak geliştirilmiş modern bir AI kod editörüdür. Geliştiricilerin AI asistanları ile birlikte çalışarak daha verimli kod yazmasını sağlar.

## ✨ Özellikler

- 🧠 **AI Agent Sistemi**: Çeşitli LLM'lerle entegre çalışan akıllı kod asistanı
- 💻 **Terminal Entegrasyonu**: Komutları doğrudan çalıştırma ve sonuçları görme
- 📁 **Dosya Yönetimi**: Proje dosyalarını görüntüleme ve düzenleme
- 🌐 **Web Browsing**: AI'ın web'de araştırma yapabilmesi
- 🔧 **API Çağrıları**: Harici servislere bağlanma yeteneği
- 💬 **Real-time Chat**: AI ile doğal dil ile iletişim
- 🐳 **Docker Sandbox**: Güvenli kod çalıştırma ortamı

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Docker ve Docker Compose
- Node.js 18+ (frontend geliştirme için)
- Python 3.9+ (backend geliştirme için)

### Kurulum

```bash
# Projeyi klonlayın
git clone <repo-url>
cd aieditor

# Hızlı başlatma
./start.sh

# Veya manuel kurulum
make setup

# Tarayıcıda açın
open http://localhost:3000
```

### API Key Yapılandırması

1. `.env` dosyasını oluşturun:
```bash
cp .env.example .env
```

2. API key'inizi ekleyin:
```bash
# OpenAI için
OPENAI_API_KEY=your_openai_api_key_here

# Veya Anthropic için
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 🏗️ Mimari

```
aieditor/
├── frontend/          # React/TypeScript UI
├── backend/           # Python API ve Agent sistemi
├── docker/           # Docker konfigürasyonları
├── docs/             # Dokümantasyon
└── examples/         # Örnek kullanımlar
```

## 🤝 Katkıda Bulunma

Bu proje açık kaynak kodludur ve katkılarınızı bekliyoruz!

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.