# AI Desktop Pet

An AI-driven desktop companion application with two-tier memory system, proactive engagement, and multi-user support. Built with PyQt6 for the GUI and FastAPI for the backend API.

## Features

### Core Features
- 🤖 **Multi-AI Provider Support**: OpenAI, Claude (Anthropic), and Gemini
- 💬 **Intelligent Chat Interface**: Beautiful floating window with chat bubbles
- 🧠 **Two-Tier Memory System**: 
  - Short-term: Last 20 conversation messages
  - Long-term: ChromaDB vector store with semantic search
- 👤 **User Profile Management**: Automatic extraction and updates of user information
- ⚡ **Proactive Conversations**: AI initiates conversations after periods of inactivity
- 🎨 **Customizable Personality**: Define AI character traits, backstory, and response style
- 💾 **Persistent Storage**: Conversation history and user profiles saved locally

### Architecture
- **Frontend-Backend Separation**: Client-server architecture for scalability
- **Multi-User Support**: Each user has isolated data and conversation history
- **Docker & Kubernetes Ready**: Containerized deployment with K8s manifests
- **Load Testing Support**: Mock AI provider for testing without API costs

## Quick Start

### Prerequisites
- Python 3.10 or higher
- PyQt6 (for GUI)
- FastAPI (for backend API)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-Desktop-Pet
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or use a virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Running the Application

#### Option 1: GUI Mode (Desktop Application)
```bash
python run.py
```

This starts the desktop application with a floating chat window.

#### Option 2: API Mode (Backend Server)
```bash
# Set environment variables
export API_MODE=true
export USE_MOCK_AI=true  # Use mock AI for testing (no API tokens consumed)

# Start the server
python run.py --api
# Or
python run.py --api
```

The API server will be available at `http://localhost:8080`
- API Documentation: http://localhost:8080/docs
- Health Check: http://localhost:8080/health

#### Option 3: Frontend-Backend Separation

**Terminal 1 - Start Backend:**
```bash
export API_MODE=true
export USE_MOCK_AI=true
python run.py --api
```

**Terminal 2 - Start Client:**
```bash
export API_BASE_URL=http://localhost:8080
python run.py
```

## Configuration

### Setting Up AI Provider

1. **OpenAI**
   ```bash
   export OPENAI_API_KEY=sk-your-key-here
   export AI_PROVIDER=openai
   export OPENAI_MODEL=gpt-3.5-turbo
   ```

2. **Claude (Anthropic)**
   ```bash
   export CLAUDE_API_KEY=your-key-here
   export AI_PROVIDER=claude
   export CLAUDE_MODEL=claude-3-sonnet-20240229
   ```

3. **Gemini**
   ```bash
   export GEMINI_API_KEY=your-key-here
   export AI_PROVIDER=gemini
   export GEMINI_MODEL=gemini-pro
   ```

### Configuration Files

Configuration is stored in `data/config.json`:
```json
{
  "ai_provider": "openai",
  "openai": {
    "api_key": "sk-...",
    "model": "gpt-3.5-turbo",
    "max_tokens": 150
  },
  "window": {
    "x": 100,
    "y": 100
  },
  "opacity": 92
}
```

## Project Structure

```
AI-Desktop-Pet/
├── src/                      # Core application code
│   ├── domain/              # Domain layer (business logic)
│   │   ├── ai/              # AI providers and profile extraction
│   │   └── profile/         # User profile management
│   ├── infrastructure/      # Infrastructure layer
│   │   ├── memory/          # Vector store (ChromaDB)
│   │   └── api_clients/    # External API clients
│   ├── application/         # Application layer
│   ├── presentation/        # UI components (standalone mode)
│   └── api/                # FastAPI server
├── client/                  # Client-side code
│   └── src/
│       ├── presentation/    # UI components
│       └── infrastructure/  # Client infrastructure
├── backend/                 # Backend API code
│   └── app/                # FastAPI application
├── data/                   # Data directory (auto-created)
│   ├── config.json         # Application configuration
│   ├── personality.json    # Personality settings
│   ├── conversation_history.json
│   └── users/              # Per-user data (multi-user mode)
├── k8s/                    # Kubernetes deployment files
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
├── run.py                 # Main entry point
└── README.md
```

## Architecture

The project follows a clean architecture pattern with clear separation of concerns:

- **Domain Layer**: Core business logic (AI providers, profile management)
- **Infrastructure Layer**: External services (vector store, API clients)
- **Application Layer**: Use cases and orchestration
- **Presentation Layer**: UI components
- **API Layer**: RESTful API endpoints

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)

## Deployment

### Docker

Build the Docker image:
```bash
docker build -t desktop-pet:latest .
```

Run the container:
```bash
docker run -p 8080:8080 \
  -e API_MODE=true \
  -e USE_MOCK_AI=true \
  -v $(pwd)/data:/app/data \
  desktop-pet:latest
```

Or use Docker Compose:
```bash
docker-compose up -d
```

### AWS EC2 (Free Tier) 🆓

Deploy to AWS EC2 using GitHub Actions - **completely free**!

**Quick Start**: See [AWS Quick Start Guide](docs/AWS_QUICK_START.md)

**Features**:
- ✅ Automatic deployment on GitHub push
- ✅ Uses AWS Free Tier (EC2 t2.micro + ECR)
- ✅ Zero cost for 12 months
- ✅ Production-ready CI/CD

**Setup Steps**:
1. Create EC2 instance (t2.micro)
2. Create ECR repository
3. Configure GitHub Secrets
4. Push code → Auto deploy! 🚀

See [AWS Deployment Guide](docs/AWS_DEPLOYMENT.md) for detailed instructions.

### Kubernetes

Deploy to Kubernetes:
```bash
# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Apply Secrets (create secret.yaml from secret.yaml.example)
kubectl apply -f k8s/secret.yaml

# Apply PVC
kubectl apply -f k8s/pvc.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Optional: Apply HPA for auto-scaling
kubectl apply -f k8s/hpa.yaml
```

### CI/CD

- **Jenkins**: See [CI/CD Documentation](docs/CI_CD.md)
- **GitHub Actions**: Automatic deployment to AWS (see `.github/workflows/deploy-aws.yml`)

## Development

### Running Tests

```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Load tests (requires Locust)
locust -f tests/load/locustfile.py
```

### Code Structure

- **Domain Layer**: Pure business logic, no dependencies on infrastructure
- **Infrastructure Layer**: External service integrations
- **Application Layer**: Orchestrates domain and infrastructure
- **Presentation Layer**: UI components using PyQt6
- **API Layer**: FastAPI REST endpoints

## Environment Variables

### Backend Environment Variables
```bash
API_MODE=true                    # Enable API mode
PORT=8080                        # Server port
HOST=0.0.0.0                     # Listen address
USE_MOCK_AI=true                 # Use Mock AI (for testing)
AI_PROVIDER=openai               # AI Provider name
OPENAI_API_KEY=sk-...            # OpenAI API Key
CLAUDE_API_KEY=...               # Claude API Key
GEMINI_API_KEY=...               # Gemini API Key
MOCK_RESPONSE_DELAY=1.0          # Mock response delay (seconds)
MOCK_CPU_INTENSIVE=true          # Enable CPU-intensive mock processing
```

### Client Environment Variables
```bash
API_BASE_URL=http://localhost:8080  # Backend API address
USER_ID=your-user-id                # User ID (optional, auto-generated)
```

## Features in Detail

### Two-Tier Memory System

1. **Short-term Memory**: Last 20 conversation messages kept in memory for context
2. **Long-term Memory**: ChromaDB vector store with semantic search
   - Uses free local SentenceTransformer model (all-MiniLM-L6-v2)
   - No API keys required for embeddings
   - Conversations stored with metadata for retrieval

### User Profile Management

The system automatically extracts and maintains user profiles:
- **Name**: User's name (if mentioned)
- **Personality Traits**: Observable traits from conversations
- **Preferences**: Likes, dislikes, interests
- **Goals**: Aspirations and objectives
- **Important Dates**: Birthdays, deadlines, anniversaries
- **Facts**: Other notable information

Profile updates are triggered intelligently:
- First 20 conversations: Every 5 conversations
- 20-50 conversations: Every 10 conversations
- After 50: Every 15 conversations

### Proactive Conversations

The AI can initiate conversations after periods of inactivity:
- Default interval: 10 minutes
- Configurable via `proactive_interval_minutes`
- Only triggers if user hasn't sent a message recently

## Troubleshooting

### Client Cannot Connect to Backend

**Error**: `Cannot connect to backend API`

**Solutions**:
1. Verify backend is running: `python run.py --api`
2. Check `API_BASE_URL` environment variable
3. Check firewall settings
4. Verify backend health: `curl http://localhost:8080/health`

### Import Errors

**Error**: `ModuleNotFoundError`

**Solutions**:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (requires 3.10+)
3. Verify virtual environment is activated

### Backend Startup Failed

**Error**: Backend cannot start

**Solutions**:
1. Check port availability: `netstat -an | grep 8080`
2. Verify dependencies: `pip install -r backend/requirements.txt`
3. Check error logs for detailed messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See [LICENSE](LICENSE) file for details.

## Roadmap

### Completed ✅
- [x] Desktop floating window
- [x] Chat interface UI
- [x] Personality setup interface
- [x] Two-tier memory system
- [x] User profile extraction
- [x] Proactive conversations
- [x] Multi-AI provider support
- [x] Frontend-backend separation
- [x] Docker containerization
- [x] Kubernetes deployment

### In Progress / Planned
- [ ] Load testing and performance optimization
- [ ] Additional AI providers
- [ ] Enhanced UI themes
- [ ] Plugin system for extensions
- [ ] Mobile companion app

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI
- Uses [FastAPI](https://fastapi.tiangolo.com/) for the backend API
- Vector storage powered by [ChromaDB](https://www.trychroma.com/)
- Embeddings provided by [Sentence Transformers](https://www.sbert.net/)
