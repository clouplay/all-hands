#!/bin/bash

echo "🤖 Aieditor - AI Code Editor"
echo "=============================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY=your_key_here"
    echo "   - ANTHROPIC_API_KEY=your_key_here"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

echo "🏗️  Building Docker images..."
docker-compose build

echo "🚀 Starting Aieditor..."
docker-compose up -d

echo ""
echo "✅ Aieditor is starting up!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   make logs    - View logs"
echo "   make down    - Stop services"
echo "   make clean   - Clean up"
echo ""

# Wait a bit and check if services are running
sleep 5

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy!"
else
    echo "⚠️  Backend might still be starting up..."
fi

echo ""
echo "🎉 Happy coding with AI!"