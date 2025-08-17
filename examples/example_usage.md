# Aieditor Kullanım Örnekleri

## Kod Yazma

### Python Fonksiyonu Oluşturma
```
Kullanıcı: "Fibonacci sayılarını hesaplayan bir Python fonksiyonu yaz"

AI Yanıtı:
```python
def fibonacci(n):
    """
    Fibonacci dizisinin n. elemanını hesaplar
    
    Args:
        n (int): Hesaplanacak Fibonacci sayısının sırası
    
    Returns:
        int: n. Fibonacci sayısı
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Örnek kullanım
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### React Komponenti
```
Kullanıcı: "Bir todo listesi React komponenti oluştur"

AI Yanıtı: [React komponenti kodu]
```

## Terminal Komutları

### Dosya İşlemleri
```
Kullanıcı: "Mevcut dizindeki Python dosyalarını listele"
AI: `ls *.py` komutunu çalıştırır

Kullanıcı: "requirements.txt dosyasını oluştur"
AI: Gerekli paketleri analiz eder ve dosyayı oluşturur
```

### Git İşlemleri
```
Kullanıcı: "Git repository'sini başlat ve ilk commit'i yap"
AI: 
1. `git init`
2. `git add .`
3. `git commit -m "Initial commit"`
```

## Dosya Yönetimi

### Dosya Okuma
```
Kullanıcı: "config.json dosyasını oku"
AI: Dosya içeriğini gösterir ve açıklar
```

### Kod Analizi
```
Kullanıcı: "Bu Python kodunu analiz et ve iyileştirme önerileri ver"
AI: Kod kalitesi, performance ve best practices açısından analiz yapar
```

## Proje Geliştirme Senaryoları

### Web API Oluşturma
```
1. "FastAPI ile basit bir REST API oluştur"
2. "Veritabanı modelleri ekle"
3. "Authentication sistemi ekle"
4. "API testlerini yaz"
```

### Frontend Geliştirme
```
1. "React uygulaması oluştur"
2. "Material-UI ile responsive tasarım yap"
3. "API entegrasyonu ekle"
4. "State management ekle"
```

## Debugging ve Sorun Giderme

### Hata Analizi
```
Kullanıcı: "Bu hata mesajını açıkla: ModuleNotFoundError: No module named 'requests'"
AI: Hatanın nedenini açıklar ve çözüm önerir
```

### Performance Optimizasyonu
```
Kullanıcı: "Bu kod neden yavaş çalışıyor?"
AI: Kodu analiz eder ve optimizasyon önerileri sunar
```

## Öğrenme ve Eğitim

### Kavram Açıklaması
```
Kullanıcı: "Async/await nedir ve nasıl kullanılır?"
AI: Detaylı açıklama ve örneklerle anlatır
```

### Best Practices
```
Kullanıcı: "Python'da clean code yazmanın kuralları neler?"
AI: Best practices'i örneklerle açıklar
```

## İleri Seviye Kullanım

### Mikroservis Mimarisi
```
1. "Docker ile mikroservis oluştur"
2. "API Gateway ekle"
3. "Service discovery implementasyonu"
4. "Monitoring ve logging"
```

### DevOps İşlemleri
```
1. "CI/CD pipeline oluştur"
2. "Kubernetes deployment"
3. "Infrastructure as Code"
4. "Monitoring setup"
```