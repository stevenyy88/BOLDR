# BOLDR Setup and Installation Guide

> Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP (T17LL1937H) · https://DigitalFutures.Asia

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB free space
- **Python**: 3.12+ (tested with 3.14)
- **Docker**: Docker Desktop or Docker Engine 20.10+
- **Docker Compose**: v2.0+
- **Ollama**: Running locally with `glm-5.1:cloud` model pulled

### Quick Prereq Check
```bash
python3 --version      # Python 3.12+
docker --version       # Docker 20.10+
docker compose version # Docker Compose v2
ollama list            # Should show glm-5.1:cloud
```

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/stevenyy88/BOLDR.git
cd BOLDR

# 2. Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r app/requirements.txt

# 4. Copy and configure environment variables
cp .env.example .env
# The .env is pre-configured for local Ollama — edit API keys for cloud LLM

# 5. Start Docker services (ChromaDB + n8n only)
docker compose up -d chromadb n8n

# 6. Wait for services to be healthy
sleep 10

# 7. Seed the knowledge base
python scripts/index_kb.py --data-dir "../dataset" --chroma-host localhost --chroma-port 8100

# 8. Run tests
python -m pytest app/tests/test_e2e.py -v

# 9. Start the FastAPI server
uvicorn app.api:app --host 0.0.0.0 --port 8000

# 10. (In a new terminal) Start the Streamlit dashboard
streamlit run app/dashboard/app.py --server.port 8501 --server.headless true
```

## Accessing the Services

| Service | URL | Description |
|---------|-----|-------------|
| FastAPI | http://localhost:8000 | Intelligence Engine API |
| FastAPI Docs | http://localhost:8000/docs | Swagger UI |
| Streamlit | http://localhost:8501 | CS Dashboard |
| n8n | http://localhost:5678 | Workflow Editor |
| ChromaDB | http://localhost:8100 | Vector DB |
| Ollama | http://localhost:11434 | LLM Server |

## Configuration

All configuration is via the `.env` file:

| Variable | Description | Default |
|---|---|---|
| `GLM_API_KEY` | Primary LLM API key | `ollama` (local) |
| `GLM_BASE_URL` | LLM API base URL | `http://localhost:11434/v1` |
| `GLM_MODEL` | LLM model name | `glm-5.1:cloud` |
| `OPENAI_API_KEY` | Fallback LLM API key | `ollama` (local) |
| `N8N_HOST` | n8n bind address | `0.0.0.0` |
| `N8N_PORT` | n8n port | `5678` |
| `CHROMA_HOST` | ChromaDB host | `localhost` |
| `CHROMA_PORT` | ChromaDB port | `8100` |
| `STREAMLIT_PORT` | Streamlit port | `8501` |
| `CONFIDENCE_THRESHOLD` | KB confidence threshold | `0.5` |

### Cloud LLM (Production)
For production deployment with cloud LLM APIs:
```env
GLM_API_KEY=your_glm_api_key
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
GLM_MODEL=glm-5.1
```

### Gmail Integration (for email channel)
- **Gmail Client ID** — Google OAuth credentials
- **Gmail Client Secret** — Google OAuth credentials
- **Gmail Refresh Token** — Obtained via OAuth flow

## Running the Test Suite

```bash
# Activate virtual environment
source .venv/bin/activate

# Set environment for tests
export CHROMA_HOST=localhost CHROMA_PORT=8100 KB_DATA_DIR=../dataset

# Run all tests
python -m pytest app/tests/test_e2e.py -v

# Run the full 70-ticket pipeline test
python scripts/test_all_tickets.py --data-dir "../dataset"

# Index the knowledge base
python scripts/index_kb.py --data-dir "../dataset" --chroma-host localhost --chroma-port 8100

# Generate knowledge gap log
python scripts/generate_gap_log.py
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Full Intake Pipeline
```bash
curl -X POST http://localhost:8000/api/v1/intake \
  -H "Content-Type: application/json" \
  -d '{"message": "Is the Expedition strap BPA-free?", "channel": "instagram_dm", "subject": "Strap inquiry"}'
```

### Intent Classification
```bash
curl -X POST http://localhost:8000/api/v1/intent \
  -H "Content-Type: application/json" \
  -d '{"subject": "Strap inquiry", "message": "Is the Expedition strap BPA-free?"}'
```

### KB Search
```bash
curl -X POST http://localhost:8000/api/v1/kb/search \
  -H "Content-Type: application/json" \
  -d '{"query": "BPA-free straps", "n_results": 3}'
```

## Common Operations

### View Logs
```bash
docker compose logs -f n8n        # n8n workflow logs
docker compose logs -f chromadb    # ChromaDB logs
```

### Restart Services
```bash
docker compose restart n8n         # Restart n8n
docker compose restart chromadb    # Restart ChromaDB
```

### Stop
```bash
docker compose down                 # Stop all Docker services
```

## Troubleshooting

### ChromaDB won't start
```bash
docker compose logs chromadb       # Check logs
docker compose restart chromadb   # Restart
```

### n8n can't connect to FastAPI
```bash
# Verify FastAPI is running
curl http://localhost:8000/api/v1/health
# Check both services are running
docker compose ps
```

### Ollama not responding
```bash
ollama list                        # Check model is available
ollama pull glm-5.1:cloud         # Pull model if needed
curl http://localhost:11434/v1/models  # Verify API
```

### Python app can't connect to ChromaDB
```bash
curl http://localhost:8100/api/v2/heartbeat  # Verify ChromaDB
```