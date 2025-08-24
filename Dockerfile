# Multi-stage build for MemoryAid application
FROM python:3.9-slim as backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY api/ ./api/

# Create data directories
RUN mkdir -p /app/data/images

# Build stage for frontend
FROM node:18-alpine as frontend

WORKDIR /app/web

# Copy frontend package files
COPY web/package*.json ./
RUN npm ci --only=production

# Copy frontend source
COPY web/ ./

# Build frontend
RUN npm run build

# Final stage
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from backend stage
COPY --from=backend /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin

# Copy backend code
COPY --from=backend /app/api ./api

# Copy built frontend from frontend stage
COPY --from=frontend /app/web/.next ./web/.next
COPY --from=frontend /app/web/public ./web/public
COPY --from=frontend /app/web/package.json ./web/

# Copy other necessary files
COPY --from=frontend /app/web/next.config.js ./web/
COPY --from=frontend /app/web/tailwind.config.js ./web/
COPY --from=frontend /app/web/postcss.config.js ./web/

# Create data directories
RUN mkdir -p /app/data/images

# Create startup script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose ports
EXPOSE 8000 3000

# Set environment variables
ENV PYTHONPATH=/app
ENV DEMO_MODE=true
ENV CAPTURE_INTERVAL_SECONDS=30
ENV STORAGE_PATH=/app/data/images
ENV FAISS_INDEX_PATH=/app/data/faiss.index
ENV METADATA_DB_PATH=/app/data/metadata.db
ENV MEMORY_API_KEY=demo_key_12345

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
