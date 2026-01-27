# --- Stage 1: Download Ollama binary ---
FROM debian:bookworm-slim AS ollama-downloader
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -L https://ollama.com/download/ollama-linux-amd64 -o /bin/ollama \
    && chmod +x /bin/ollama

# --- Stage 2: Final Image ---
FROM python:3.11-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal runtime dependencies in ONE layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Ollama binary from Stage 1
COPY --from=ollama-downloader /bin/ollama /usr/local/bin/ollama

# Set working directory
WORKDIR /app

# Ensure storage directory exists
RUN mkdir -p /storage && chmod 777 /storage

# Copy requirements and install (Aggressive slimming)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    OLLAMA_HOST=0.0.0.0 \
    OLLAMA_MODELS=/storage/models \
    SQLITE_DB_PATH=/storage/complaila.db

# Expose Ollama port
EXPOSE 11434

# Use the entrypoint script
RUN chmod +x /app/scripts/entrypoint.sh
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]
