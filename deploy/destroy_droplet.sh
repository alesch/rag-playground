#!/bin/bash
# destroy_droplet.sh
# Safely tears down the runner droplet, ensuring volumes are detached first.

# Load config
source "$(dirname "$0")/config.env"

# Get running droplet ID
if [ ! -f "$(dirname "$0")/.droplet_id" ]; then
    echo "ERROR: No droplet information found. Run create_droplet.sh first."
    exit 1
fi
DROPLET_ID=$(cat "$(dirname "$0")/.droplet_id")

echo "Destroying droplet $DROPLET_ID..."

# 1. Detach Volume (Important!)
echo "Detaching volume $VOLUME_ID..."
doctl compute volume-action detach "$VOLUME_ID" "$DROPLET_ID" --wait

if [ $? -eq 0 ]; then
    echo "Volume detached."
else
    echo "ERROR: Volume detach failed. You may need to investigate manually."
    # We still try to delete the droplet which might force cleanup
fi

# 2. Delete Droplet
echo "Deleting droplet..."
doctl compute droplet delete "$DROPLET_ID" --force

if [ $? -eq 0 ]; then
    echo "Droplet deleted."
else
    echo "ERROR: Droplet deletion failed."
    exit 1
fi

# 3. Cleanup local state
rm -f "$(dirname "$0")/.droplet_id"
rm -f "$(dirname "$0")/.droplet_ip"

echo "✅ Environment teardown complete."
