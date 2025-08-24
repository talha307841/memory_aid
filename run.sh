#!/bin/bash

# MemoryAid Run Script
# Simple script to run the application with Docker

set -e

echo "🚀 MemoryAid Docker Runner"
echo "=========================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp docker.env .env
    echo "⚠️  Please edit .env file and add your OpenAI API key!"
    echo "   Then run this script again."
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env && ! grep -q "OPENAI_API_KEY=" .env; then
    echo "❌ OPENAI_API_KEY not found in .env file!"
    echo "Please edit .env file and add your OpenAI API key."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if API key is actually set
if [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ Please set your actual OpenAI API key in .env file!"
    exit 1
fi

echo "✅ Environment configured"
echo "🔑 OpenAI API Key: ${OPENAI_API_KEY:0:10}..."

# Build and run with Docker Compose
echo "🐳 Building and starting MemoryAid..."
docker-compose up --build

echo "🎉 MemoryAid stopped!"
