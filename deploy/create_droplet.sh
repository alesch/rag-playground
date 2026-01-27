#!/bin/bash
# create_droplet.sh
# Creates a droplet, attaches the volume, and prepares it for running tests.

# Load config
source "$(dirname "$0")/config.env"

echo "Running in region: $DO_REGION"
echo "Using Volume ID: $VOLUME_ID"

# 1. Create Droplet
echo "Creating droplet '$DROPLET_NAME'..."
DROPLET_ID=$(doctl compute droplet create "$DROPLET_NAME" \
  --region "$DO_REGION" \
  --image "$DO_IMAGE" \
  --size "$DO_SIZE" \
  --ssh-keys "$SSH_KEY_FINGERPRINT" \
  --volumes "$VOLUME_ID" \
  --tag-name "$TAGS" \
  --format ID --no-header \
  --wait)

if [ -z "$DROPLET_ID" ]; then
    echo "ERROR: Failed to create droplet."
    exit 1
fi

echo "Droplet created with ID: $DROPLET_ID"

# 2. Get Public IP
DROPLET_IP=$(doctl compute droplet get "$DROPLET_ID" --format PublicIPv4 --no-header)
echo "Droplet IP: $DROPLET_IP"

# 3. Wait for SSH to be ready
echo "Waiting for SSH to become available..."
MAX_RETRIES=30
for ((i=1; i<=MAX_RETRIES; i++)); do
    ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY_PATH" root@"$DROPLET_IP" "echo ready" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "SSH is ready!"
        break
    else
        echo -n "."
        sleep 2
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo "Timed out waiting for SSH."
        exit 1
    fi
done

# 4. Configure Droplet (Install Docker, Mount Volume)
echo "Configuring droplet..."
ssh -o StrictHostKeyChecking=no -i "$SSH_PRIVATE_KEY_PATH" root@"$DROPLET_IP" bash -s <<EOF
    # Set non-interactive
    export DEBIAN_FRONTEND=noninteractive

    # Update and install Docker
    echo "Installing Docker..."
    apt-get update -qq
    apt-get install -y docker.io snapd -qq
    
    # Install doctl for registry auth
    echo "Installing doctl..."
    snap install doctl
    snap connect doctl:dot-config-personal-files
    snap connect doctl:ssh-keys

    # Mount Volume
    echo "Mounting volume..."
    # DigitalOcean persistent volumes appear in specific paths
    mkdir -p /mnt/complaila-storage
    mount -o discard,defaults /dev/disk/by-id/scsi-0DO_Volume_complaila-storage /mnt/complaila-storage
    
    # Verify mount
    if mountpoint -q /mnt/complaila-storage; then
        echo "Volume mounted successfully."
    else
        echo "ERROR: Volume mount failed."
        exit 1
    fi
EOF

# 5. Save Droplet Info for downstream scripts
echo "$DROPLET_ID" > "$(dirname "$0")/.droplet_id"
echo "$DROPLET_IP" > "$(dirname "$0")/.droplet_ip"

echo "✅ Setup complete. Droplet $DROPLET_ID is ready at $DROPLET_IP"
