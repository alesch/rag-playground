#!/bin/bash

# Start Ollama in the background
echo "Starting Ollama server..."
ollama serve &

# Wait for Ollama server to be ready
echo "Waiting for Ollama to be ready..."
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 1
done
echo "Ollama is ready!"

# Execute the passed command (the CMD from Dockerfile or docker run)
exec "$@"
