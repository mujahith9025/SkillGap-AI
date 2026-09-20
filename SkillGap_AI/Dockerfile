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

# Expose FastAPI Web App (8000)
EXPOSE 8000

# Healthcheck for container stability
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# Default command launches the FastAPI web application and REST API
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
