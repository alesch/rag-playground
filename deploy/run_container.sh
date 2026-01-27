#!/bin/bash
# run_container.sh
# Connects to the droplet and runs the Docker container with an interactive shell.

# Load config
source "$(dirname "$0")/config.env"

# Get running droplet IP
if [ ! -f "$(dirname "$0")/.droplet_ip" ]; then
    echo "ERROR: No droplet information found. Run create_droplet.sh first."
    exit 1
fi
DROPLET_IP=$(cat "$(dirname "$0")/.droplet_ip")

echo "Connecting to droplet $DROPLET_IP..."

# Authenticate Docker to Registry
echo "Authenticating Docker..."
# Extract token from local doctl config
DO_TOKEN=$(grep 'access-token' ~/.config/doctl/config.yaml | head -1 | awk '{print $2}')
ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY_PATH" root@"$DROPLET_IP" bash -s <<EOF
    echo "$DO_TOKEN" | docker login registry.digitalocean.com -u unused --password-stdin
EOF

# Run Container with Volume Mounts
echo "Starting interactive container..."
ssh -t -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY_PATH" root@"$DROPLET_IP" \
    "docker run --rm -it \
      -v /mnt/complaila-storage:/storage \
      -v /mnt/complaila-storage/bin/ollama:/usr/local/bin/ollama \
      -e OLLAMA_MODELS=/storage/models \
      -e SQLITE_DB_PATH=/storage/data/complaila.db \
      $DOCKER_IMAGE \
      /bin/bash"

echo "✅ Evaluation complete."
