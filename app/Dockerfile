# BOLDR Self-Improving Customer Intelligence Engine
# Multi-stage Dockerfile for production deployment
#
# Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP (T17LL1937H)
# https://DigitalFutures.Asia
#
# Runs both FastAPI (port 8000) and Streamlit (port 8501) via supervisord.
# ChromaDB and n8n run in separate containers via docker-compose.yml.
#
# Build: docker build -t boldr-app:latest .
# Run:   docker compose up -d

# ============================================================
# Stage 1: Install Python dependencies
# ============================================================
FROM python:3.12-slim AS dependencies

WORKDIR /app

# Install system dependencies for building native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with CPU-only PyTorch to reduce image size
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 2: Runtime image
# ============================================================
FROM python:3.12-slim AS runtime

LABEL author="Steve Ng, Founder and CEO — Digital Futures Consultancy LLP"
LABEL description="BOLDR Self-Improving Customer Intelligence Engine"
LABEL project="ECHELON 2026 AI Workflow Competition — REVENUE ROCKET Track"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install runtime dependencies only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create data directory for SQLite databases
RUN mkdir -p /app/data

# Supervisord configuration for running both FastAPI and Streamlit
RUN mkdir -p /var/log/supervisor
COPY <<'EOF' /etc/supervisor/conf.d/boldr.conf
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:boldr_api]
command=uvicorn app.api:app --host 0.0.0.0 --port 8000 --workers 2
directory=/app
autostart=true
autorestart=true
startsecs=5
startretries=3
stdout_logfile=/var/log/supervisor/boldr_api.log
stderr_logfile=/var/log/supervisor/boldr_api_error.log

[program:boldr_dashboard]
command=streamlit run app/dashboard/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
directory=/app
autostart=true
autorestart=true
startsecs=10
startretries=3
stdout_logfile=/var/log/supervisor/boldr_dashboard.log
stderr_logfile=/var/log/supervisor/boldr_dashboard_error.log
EOF

# Health check — check FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=60s \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose ports
# 8000 = FastAPI (intelligence loop API)
# 8501 = Streamlit (dashboard)
EXPOSE 8000 8501

# Volume mounts for persistent data
VOLUME ["/app/data", "/app/chroma_data"]

# Start both services via supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/boldr.conf"]