# BOLDR Self-Improving Customer Intelligence Engine
# Dockerfile for Python application (FastAPI + Streamlit)

FROM python:3.12-slim

LABEL author="Steve Ng, Founder and CEO - Digital Futures Consultancy LLP"
LABEL description="BOLDR Self-Improving Customer Intelligence Engine"
LABEL project="ECHELON 2026 AI Workflow Competition - REVENUE ROCKET Track"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
# 8000 = FastAPI (intelligence loop API)
# 8501 = Streamlit (dashboard)
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default: run FastAPI server
# Streamlit dashboard can be run separately: streamlit run app/dashboard/app.py
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]