# MemoryAid - Docker Quick Start

## 🚀 Single Command Setup

MemoryAid is now fully Dockerized! You can run the entire application (frontend + backend) with just one command.

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API Key

### Quick Start (3 Steps)

1. **Clone and Setup**
   ```bash
   git clone <your-repo>
   cd memory_aid
   ```

2. **Set OpenAI API Key**
   ```bash
   # Copy environment template
   cp docker.env .env
   
   # Edit .env and add your API key
   nano .env
   ```
   
   **Only change this line:**
   ```env
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

3. **Run with Single Command**
   ```bash
   # Option 1: Use the run script
   ./run.sh
   
   # Option 2: Use Docker Compose directly
   docker-compose up --build
   
   # Option 3: Use Make
   make run
   ```

### 🎯 Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Docs**: http://localhost:8000/docs

## 🐳 Docker Commands

```bash
# Start application
docker-compose up --build

# Start in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Clean everything
docker-compose down --rmi all --volumes
```

## 🔧 Make Commands

```bash
# Show all commands
make help

# Quick start (setup + run)
make start

# Build only
make build

# Run tests
make test

# Run demo
make demo
```

## 📋 What's Included

✅ **Frontend**: Next.js 14 with React 18 and Tailwind CSS  
✅ **Backend**: FastAPI with OpenAI integration  
✅ **Database**: SQLite + FAISS vector storage  
✅ **AI Features**: Image analysis, embeddings, chat assistant  
✅ **Demo Mode**: Automatic simulated captures every 30 seconds  
✅ **Single Container**: Both services in one Docker image  

## 🌟 Features

- **AI-Powered Memory Processing**: OpenAI GPT for image analysis
- **Automatic Captures**: Simulated photo capture every 30 seconds
- **Intelligent Search**: Find memories by timestamp or natural language
- **Chat Interface**: Ask questions about your memories
- **Vector Storage**: FAISS-based similarity search
- **Image Compression**: Automatic optimization and storage

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the ports
   lsof -i :3000
   lsof -i :8000
   
   # Stop conflicting services or change ports in docker-compose.yml
   ```

2. **Permission Denied**
   ```bash
   chmod +x run.sh
   ```

3. **Docker Not Running**
   ```bash
   # Start Docker service
   sudo systemctl start docker
   ```

4. **View Logs for Debugging**
   ```bash
   docker-compose logs -f
   ```

### Reset Everything

```bash
# Stop and remove everything
docker-compose down --rmi all --volumes

# Remove data
sudo rm -rf data/

# Start fresh
docker-compose up --build
```

## 🔐 Environment Variables

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional (all have defaults):**
- `DEMO_MODE` - Enable demo mode (default: true)
- `CAPTURE_INTERVAL_SECONDS` - Capture interval (default: 30)
- `MEMORY_API_KEY` - Backend auth token (default: demo_key_12345)

## 📱 Demo Mode

The application runs in demo mode by default:
- Creates simulated captures every 30 seconds
- Generates sample images with timestamps
- Processes images with AI analysis
- Stores everything in vector database

Perfect for testing and demonstrations!

## 🚀 Production Notes

For production deployment:
- Change `MEMORY_API_KEY` to a secure value
- Set `DEMO_MODE=false`
- Configure proper storage paths
- Use environment-specific settings

---

**That's it!** MemoryAid is now running with just one command. 🎉
