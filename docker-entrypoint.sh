#!/bin/bash

# MemoryAid Docker Entrypoint Script
# Starts both backend and frontend services

set -e

echo "🚀 MemoryAid starting up..."

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY environment variable is required!"
    echo "Please set it when running the container:"
    echo "docker run -e OPENAI_API_KEY=your_key_here ..."
    exit 1
fi

echo "✅ OpenAI API key configured"

# Set default environment variables if not provided
export DEMO_MODE=${DEMO_MODE:-true}
export CAPTURE_INTERVAL_SECONDS=${CAPTURE_INTERVAL_SECONDS:-30}
export STORAGE_PATH=${STORAGE_PATH:-/app/data/images}
export FAISS_INDEX_PATH=${FAISS_INDEX_PATH:-/app/data/faiss.index}
export METADATA_DB_PATH=${METADATA_DB_PATH:-/app/data/metadata.db}
export MEMORY_API_KEY=${MEMORY_API_KEY:-demo_key_12345}

echo "📋 Configuration:"
echo "   Demo Mode: $DEMO_MODE"
echo "   Capture Interval: $CAPTURE_INTERVAL_SECONDS seconds"
echo "   Storage Path: $STORAGE_PATH"
echo "   API Key: $MEMORY_API_KEY"

# Create necessary directories
mkdir -p "$STORAGE_PATH"
mkdir -p "$(dirname "$FAISS_INDEX_PATH")"
mkdir -p "$(dirname "$METADATA_DB_PATH")"

echo "📁 Directories created"

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down MemoryAid..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start backend service
echo "🔧 Starting FastAPI backend..."
cd /app
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start within 30 seconds"
        exit 1
    fi
    echo "   Attempt $i/30..."
    sleep 1
done

# Start frontend service
echo "🌐 Starting Next.js frontend..."
cd /app/web
npm start &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start within 30 seconds"
        exit 1
    fi
    echo "   Attempt $i/30..."
    sleep 1
done

echo ""
echo "🎉 MemoryAid is now running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the application"

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID
