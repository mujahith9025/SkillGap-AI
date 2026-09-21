# Multi-Stage Production Dockerfile for SkillGap AI
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python package dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code, datasets, and configurations
COPY . .

# Expose default port
EXPOSE 8000

# Launch command using shell format to support dynamic $PORT from cloud providers (Render, Railway, HuggingFace, Cloud Run)
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
