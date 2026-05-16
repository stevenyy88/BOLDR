# BOLDR Setup and Installation Guide

> Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB free space
- **Docker**: Docker Desktop or Docker Engine 20.10+
- **Docker Compose**: v2.0+

### API Keys Required
- **GLM API Key** — Primary LLM for classification and drafting (get from platform)
- **OpenAI API Key** — Fallback LLM (optional, for low-confidence edge cases)
- **Anthropic API Key** — Claude fallback (optional, for edge cases)

### Gmail Integration (for email channel)
- **Gmail Client ID** — Google OAuth credentials
- **Gmail Client Secret** — Google OAuth credentials
- **Gmail Refresh Token** — Obtained via OAuth flow

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/stevenyy88/BOLDR.git
cd BOLDR

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Start all services
docker compose up -d

# 4. Verify services are running
docker compose ps

# 5. Access the services:
#    n8n workflow editor:  http://localhost:5678
#    Streamlit dashboard:   http://localhost:8501
#    ChromaDB:              http://localhost:8000
```

## Configuration

All configuration is via the `.env` file:

| Variable | Description | Default |
|---|---|---|
| `GLM_API_KEY` | Primary LLM API key | (required) |
| `OPENAI_API_KEY` | Fallback LLM API key | (optional) |
| `ANTHROPIC_API_KEY` | Claude fallback API key | (optional) |
| `N8N_HOST` | n8n bind address | `0.0.0.0` |
| `N8N_PORT` | n8n port | `5678` |
| `GENERIC_TIMEZONE` | Timezone | `Asia/Singapore` |
| `CHROMA_HOST` | ChromaDB host | `chromadb` |
| `CHROMA_PORT` | ChromaDB port | `8000` |
| `STREAMLIT_PORT` | Streamlit port | `8501` |
| `CONFIDENCE_THRESHOLD` | KB confidence threshold | `0.5` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Accessing the Services

### n8n Workflow Editor
- URL: http://localhost:5678
- Import workflow: Settings → Import from File → `n8n/workflows/boldr_intelligence_loop.json`

### Streamlit Dashboard
- URL: http://localhost:8501
- Features: Approval queue, theme analysis, KB management, gap log, marketing brief

### ChromaDB
- URL: http://localhost:8000
- Health check: http://localhost:8000/api/v1/heartbeat

## Running the Test Suite

```bash
# Run all tests
cd app
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_e2e.py -v        # End-to-end tests
python -m pytest tests/test_classifier.py -v   # Intent + persona classification

# Run the full 70-ticket pipeline test
python scripts/test_all_tickets.py

# Index the knowledge base
python scripts/index_kb.py

# Generate knowledge gap log
python scripts/generate_gap_log.py
```

## Common Operations

### View Logs
```bash
docker compose logs -f app        # Streamlit app logs
docker compose logs -f n8n        # n8n workflow logs
docker compose logs -f chromadb   # ChromaDB logs
```

### Restart Services
```bash
docker compose restart app         # Restart Python app
docker compose restart n8n         # Restart n8n
docker compose restart             # Restart all
```

### Update
```bash
docker compose pull                 # Pull latest images
docker compose up -d               # Restart with new images
```

### Stop
```bash
docker compose down                 # Stop all services
docker compose down -v              # Stop and remove volumes (resets data)
```

## Troubleshooting

### ChromaDB won't start
```bash
docker compose logs chromadb       # Check logs
docker compose restart chromadb    # Restart
```

### n8n can't connect to Python app
```bash
# Verify both services are running
docker compose ps
# Check network
docker network inspect boldr_default
```

### Python app can't connect to ChromaDB
```bash
# Verify ChromaDB is healthy
curl http://localhost:8000/api/v1/heartbeat
```