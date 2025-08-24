.PHONY: help build run stop logs clean test demo

# Default target
help:
	@echo "MemoryAid - Available Commands:"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  build    - Build the Docker image"
	@echo "  run      - Start the application (builds if needed)"
	@echo "  stop     - Stop the application"
	@echo "  logs     - View application logs"
	@echo "  clean    - Remove containers and images"
	@echo ""
	@echo "🔧 Development Commands:"
	@echo "  test     - Run backend tests"
	@echo "  demo     - Run demo script"
	@echo "  install  - Install dependencies locally"
	@echo ""
	@echo "📋 Setup Commands:"
	@echo "  setup    - Initial setup (copy env file)"
	@echo "  help     - Show this help message"

# Docker commands
build:
	@echo "🔨 Building MemoryAid Docker image..."
	docker-compose build

run: build
	@echo "🚀 Starting MemoryAid..."
	docker-compose up

run-detached: build
	@echo "🚀 Starting MemoryAid in background..."
	docker-compose up -d

stop:
	@echo "🛑 Stopping MemoryAid..."
	docker-compose down

logs:
	@echo "📋 Viewing logs..."
	docker-compose logs -f

clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

# Development commands
test:
	@echo "🧪 Running backend tests..."
	cd api && python -m pytest tests/ -v

demo:
	@echo "🎮 Running demo script..."
	python demo_run.py

install:
	@echo "📦 Installing dependencies locally..."
	@echo "Installing backend dependencies..."
	cd api && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd web && npm install

# Setup commands
setup:
	@echo "⚙️  Setting up MemoryAid..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp docker.env .env; \
		echo "⚠️  Please edit .env file and add your OpenAI API key!"; \
		echo "   Then run 'make run' to start the application."; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Quick start
start: setup run
