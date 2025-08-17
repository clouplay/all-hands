.PHONY: help build up down logs clean install dev test

help: ## Bu yardım mesajını göster
	@echo "Aieditor - AI Code Editor"
	@echo ""
	@echo "Kullanılabilir komutlar:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Docker image'larını oluştur
	docker-compose build

up: ## Uygulamayı başlat
	docker-compose up -d

dev: ## Development modunda başlat (logları göster)
	docker-compose up

down: ## Uygulamayı durdur
	docker-compose down

logs: ## Logları göster
	docker-compose logs -f

clean: ## Tüm container'ları ve volume'ları temizle
	docker-compose down -v --remove-orphans
	docker system prune -f

install: ## Bağımlılıkları yükle
	cd frontend && npm install
	cd backend && pip install -r requirements.txt

test-backend: ## Backend testlerini çalıştır
	cd backend && python -m pytest

test-frontend: ## Frontend testlerini çalıştır
	cd frontend && npm test

lint-backend: ## Backend kod kalitesi kontrolü
	cd backend && flake8 . --max-line-length=100

lint-frontend: ## Frontend kod kalitesi kontrolü
	cd frontend && npm run lint

format-backend: ## Backend kod formatla
	cd backend && black . && isort .

format-frontend: ## Frontend kod formatla
	cd frontend && npm run format

setup: ## İlk kurulum
	cp .env.example .env
	@echo "Lütfen .env dosyasını düzenleyip API key'lerinizi ekleyin"
	make build
	make up

health: ## Sistem sağlık kontrolü
	curl -f http://localhost:8000/health || exit 1
	curl -f http://localhost:3000 || exit 1