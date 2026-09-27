# CodeShift Backend Container for Render
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install Git and certificates (required for repository cloning and Twin worktrees)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (v20 LTS), npm, yarn, and pnpm for baseline and verification runs
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g yarn pnpm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python package dependencies
COPY backend/pyproject.toml /app/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e .

# Copy application code
COPY backend/ /app/

# Ensure runtime data persistence directory exists
RUN mkdir -p /app/data

EXPOSE 8000

# Render sets $PORT dynamically at runtime (defaulting to 8000)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
