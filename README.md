# MemoryAid - AI-Powered Memory Assistant

MemoryAid is a full-stack web application that uses AI to capture, store, and retrieve visual memories. It simulates continuous photo capture, processes images with OpenAI, and provides intelligent search and chat capabilities.

## Features

- 🤖 **AI-Powered Memory Processing**: Uses OpenAI GPT for image summarization and embeddings
- 📸 **Simulated Photo Capture**: Automatic background capture simulation with configurable intervals
- 🔍 **Intelligent Search**: Find memories by timestamp or natural language queries
- 💬 **Chat Interface**: Ask questions about your memories in natural language
- 🗄️ **Vector Storage**: FAISS-based vector database for fast similarity search
- 🖼️ **Image Compression**: Automatic image optimization and storage
- 🐳 **Docker Ready**: Single command deployment with Docker
- ☁️ **Vercel Ready**: Deployable to Vercel with serverless functions

## Quick Start with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API Key

### 1. Clone the Repository
```bash
git clone <your-repo>
cd memory_aid
```

### 2. Set Your OpenAI API Key
```bash
# Copy the environment template
cp docker.env .env

# Edit .env file and add your OpenAI API key
nano .env
```

**Only change this line:**
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Run with Single Command
```bash
# Make the run script executable
chmod +x run.sh

# Start the application
./run.sh
```

**Or use Docker Compose directly:**
```bash
docker-compose up --build
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Manual Setup (Alternative)

### Prerequisites
- Python 3.8+
- Node.js 18+
- OpenAI API Key

### 1. Environment Configuration
```bash
cp docker.env .env
# Edit .env and add your OpenAI API key
```

### 2. Install Dependencies

#### Backend
```bash
cd api
pip install -r requirements.txt
```

#### Frontend
```bash
cd web
npm install
```

### 3. Run Locally

#### Backend (Terminal 1)
```bash
cd api
uvicorn main:app --reload --port 8000
```

#### Frontend (Terminal 2)
```bash
cd web
npm run dev
```

## Environment Variables

The application only requires **one environment variable**:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ **Yes** | - |

**Optional variables (all have sensible defaults):**
- `DEMO_MODE` - Enable demo mode (default: `true`)
- `CAPTURE_INTERVAL_SECONDS` - Capture interval (default: `30`)
- `MEMORY_API_KEY` - Backend auth token (default: `demo_key_12345`)

## API Endpoints

### Core Endpoints

- `POST /simulate/capture` - Trigger a simulated photo capture
- `GET /memory/search?timestamp=YYYY-MM-DDTHH:MM:SS` - Search memories by timestamp
- `GET /memory/{id}` - Get memory details by ID
- `POST /chat` - Chat with the memory assistant
- `GET /health` - Health check and statistics

### Example API Usage

#### Trigger Capture
```bash
curl -X POST "http://localhost:8000/simulate/capture" \
  -H "Authorization: Bearer demo_key_12345"
```

#### Search Memories
```bash
curl "http://localhost:8000/memory/search?timestamp=2024-01-15T14:30:00" \
  -H "Authorization: Bearer demo_key_12345"
```

#### Chat Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer demo_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"message": "Where did I put my keys?"}'
```

## Docker Commands

### Build and Run
```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop
docker-compose down

# View logs
docker-compose logs -f
```

### Manual Docker Commands
```bash
# Build image
docker build -t memoryaid .

# Run container
docker run -p 3000:3000 -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  memoryaid
```

## Demo Mode

The application includes a demo mode that:
- Creates simulated captures every 30 seconds (configurable)
- Generates sample images with timestamps
- Provides immediate testing without real hardware

Demo mode is **enabled by default** and can be controlled via the `DEMO_MODE` environment variable.

## Testing

### Run Tests
```bash
cd api
pytest tests/
```

### Demo Script
```bash
python demo_run.py
```

## Vercel Deployment

### Option 1: Monorepo Deployment (Recommended)

1. **Connect Repository to Vercel**
   - Import your GitHub repository
   - Set root directory to `/web`
   - Framework preset: Next.js

2. **Configure Build Settings**
   ```
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

3. **Add Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add `OPENAI_API_KEY` with your actual key
   - Set `DEMO_MODE=true` for Vercel demo

4. **Configure Python Backend**
   - Create `/api` directory in Vercel
   - Add `vercel.json` configuration

### Vercel Configuration

The `vercel.json` file is already configured for monorepo deployment.

## Project Structure

```
memory_aid/
├── api/                 # FastAPI backend
│   ├── main.py         # Main application
│   ├── routers/        # API route handlers
│   ├── services/       # Business logic
│   ├── models/         # Data models
│   └── requirements.txt
├── web/                # Next.js frontend
│   ├── app/           # App router pages
│   ├── components/    # React components
│   ├── lib/           # Utilities
│   └── package.json
├── data/               # Data storage (created automatically)
├── tests/              # Test files
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Multi-stage Docker build
├── docker-entrypoint.sh # Docker startup script
├── run.sh              # Simple run script
├── demo_run.py         # Demo script
└── README.md
```

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Verify `OPENAI_API_KEY` is set correctly in `.env`
   - Check API key permissions and quota

2. **Docker Issues**
   - Ensure Docker and Docker Compose are installed
   - Check if ports 3000 and 8000 are available
   - Run `docker-compose logs` to view error logs

3. **Permission Issues**
   - Make run script executable: `chmod +x run.sh`
   - Check Docker permissions

4. **Port Conflicts**
   - Change ports in `docker-compose.yml` if needed
   - Stop other services using ports 3000/8000

### Performance Tips

- Use `DEMO_MODE=true` for faster testing
- Adjust `CAPTURE_INTERVAL_SECONDS` for development
- Monitor container resource usage with `docker stats`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs` when running
- Open an issue on GitHub

---

**Note**: This is a demo application. For production use, implement proper security measures, data encryption, and consider privacy implications of storing personal images and memories.
