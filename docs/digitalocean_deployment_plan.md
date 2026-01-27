# DigitalOcean Deployment Plan

## Overview

Deploy the Complaila RAG system to DigitalOcean using a cost-efficient architecture with Docker containers and persistent storage for Ollama models.

## Architecture

- **Droplet**: Basic 8GB RAM, 4 vCPUs (shared) - $56/month, $0.026 per 20-minute run
- **Volume**: 10GB block storage for Ollama models and database - ~$1/month
- **Docker**: Application containerization for portability
- **Cost**: ~$1.26 for 10 test runs per month

## Strategy

### One-Time Setup

1. Create DigitalOcean account and get API token
2. Install `doctl` CLI tool
3. Create Volume and initial Droplet
4. Download Ollama models to Volume (gemma, deepseek, llama3.2)
5. Build and push Docker image
6. Take snapshot (optional backup)
7. Destroy initial Droplet

### Per-Test Workflow

1. Create Basic 8GB Droplet (~60 seconds)
2. Attach existing Volume with models
3. Pull Docker image
4. Run container with Volume mounted
5. Execute questionnaire tests (~20 minutes)
6. Retrieve results
7. Destroy Droplet
8. **Pay only for active time**: ~$0.026 per run

## Implementation Steps

### Phase 1: Account Setup

#### 1.1 Create DigitalOcean Account

- Sign up at <https://digitalocean.com>
- Look for $200 free credit for new users (valid for 60 days)
- Add payment method
- Generate API token: Account → API → Generate New Token (read/write access)

#### 1.2 Install doctl CLI

```bash
# Ubuntu/Debian
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
tar xf doctl-1.104.0-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin
doctl version

# Authenticate
doctl auth init
# Paste your API token when prompted
```

### Phase 2: Docker Setup

#### 2.1 Create Dockerfile

Create `Dockerfile` in project root with:

- Ubuntu 24.04 base
- Python 3.11+
- Ollama installation
- Project dependencies
- Application code

#### 2.2 Create .dockerignore

Exclude unnecessary files:

- `venv/`
- `*.pyc`
- `.git/`
- `data/` (will be synced separately)
- `notebooks/`

#### 2.3 Build and Test Locally

```bash
docker build -t complaila:latest .
docker run --rm complaila:latest python --version
```

#### 2.4 Push to DigitalOcean Container Registry (DOCR)

```bash
# Create the registry (one-time)
# Replace 'alesch-registry' with your preferred name
doctl registry create alesch-registry

# Authenticate Docker with your registry
doctl registry login

# Tag and push
# The format is registry.digitalocean.com/REGISTRY_NAME/IMAGE_NAME:TAG
docker tag complaila:latest registry.digitalocean.com/alesch-registry/complaila:latest
docker push registry.digitalocean.com/alesch-registry/complaila:latest
```

### Phase 3: DigitalOcean Infrastructure

#### 3.1 Create Volume for Ollama Models

```bash
# Create 10GB volume in your preferred region (Use nyc3 for better latency from Argentina)
doctl compute volume create complaila-storage \
  --region nyc3 \
  --size 10GiB \
  --desc "Persistent storage for Complaila models and database"

# Get volume ID
doctl compute volume list
```

#### 3.2 Create Initial Setup Droplet

```bash
# Create Basic 8GB Droplet
doctl compute droplet create complaila-setup \
  --region nyc3 \
  --image ubuntu-24-04-x64 \
  --size s-4vcpu-8gb \
  --ssh-keys YOUR_SSH_KEY_ID \
  --wait

# Attach volume
doctl compute volume-action attach VOLUME_ID DROPLET_ID --wait

# Get Droplet IP
doctl compute droplet list
```

#### 3.3 Configure Setup Droplet

SSH into the droplet and run:

```bash
# Install Docker
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Mount volume
sudo mkdir -p /mnt/complaila-storage
sudo mount -o discard,defaults /dev/disk/by-id/scsi-0DO_Volume_complaila-storage /mnt/complaila-storage
echo '/dev/disk/by-id/scsi-0DO_Volume_complaila-storage /mnt/complaila-storage ext4 defaults,nofail,discard 0 0' | sudo tee -a /etc/fstab

# Configure Volume structure
sudo mkdir -p /mnt/complaila-storage/models
sudo mkdir -p /mnt/complaila-storage/bin
sudo mkdir -p /mnt/complaila-storage/data
sudo chown -R $(whoami):$(whoami) /mnt/complaila-storage

# Download Ollama binary to the Volume (One-time)
# This keeps the Docker image small (<500MB)
curl -L https://ollama.com/download/ollama-linux-amd64 -o /mnt/complaila-storage/bin/ollama
chmod +x /mnt/complaila-storage/bin/ollama

# Download models using the binary on the volume
export OLLAMA_MODELS=/mnt/complaila-storage/models
/mnt/complaila-storage/bin/ollama serve &
sleep 5
/mnt/complaila-storage/bin/ollama pull mxbai-embed-large
/mnt/complaila-storage/bin/ollama pull llama3.2

# Verify storage
du -sh /mnt/complaila-storage
```

#### 3.4 Test Docker Container

```bash
# Authenticate Docker on the Droplet
# Note: In automation, we will use a secret or doctl
doctl registry login

# Pull from DOCR
docker pull registry.digitalocean.com/alesch-registry/complaila:latest

# Test with volume mounted (Models + Binary + Database)
docker run --rm \
  -v /mnt/complaila-storage:/storage \
  -v /mnt/complaila-storage/bin/ollama:/usr/local/bin/ollama \
  registry.digitalocean.com/alesch-registry/complaila:latest \
  ollama list
```

### Phase 4: Automation Scripts

#### 4.1 Create `deploy/config.env`

```bash
# DigitalOcean settings
DO_REGION="nyc3"
DO_SIZE="s-4vcpu-8gb"
DO_IMAGE="ubuntu-24-04-x64"
VOLUME_ID="your-volume-id"
DOCKER_IMAGE="registry.digitalocean.com/alesch-registry/complaila:latest"
SSH_KEY_ID="your-ssh-key-id"
```

#### 4.2 Create `deploy/create_droplet.sh`

Script to:

- Create new Droplet
- Attach Volume
- Install Docker
- Mount Volume
- Pull Docker image
- Return Droplet IP

#### 4.3 Create `deploy/run_tests.sh`

Script to:

- SSH into Droplet
- Run Docker container with tests
- Download results
- Display summary

#### 4.4 Create `deploy/destroy_droplet.sh`

Script to:

- Detach Volume (important!)
- Destroy Droplet
- Confirm cleanup

#### 4.5 Create `deploy/full_workflow.sh`

Master script that chains:

1. Create Droplet
2. Run tests
3. Download results
4. Destroy Droplet

### Phase 5: Project Integration

#### 5.1 Update Project Structure

```
complaila/
├── deploy/
│   ├── config.env
│   ├── create_droplet.sh
│   ├── run_tests.sh
│   ├── destroy_droplet.sh
│   └── full_workflow.sh
├── Dockerfile
├── .dockerignore
└── docs/
    └── digitalocean_deployment_plan.md
```

#### 5.2 Update `.gitignore`

Add:

```
deploy/config.env
deploy/*.log
deploy/droplet_info.json
```

#### 5.3 Create Example Config

`deploy/config.env.example` with placeholder values

### Phase 6: Testing & Validation

#### 6.1 Test Full Workflow

```bash
cd deploy
./full_workflow.sh
```

#### 6.2 Validate Results

- Check test completion time (~20 minutes)
- Verify results accuracy
- Confirm cost (~$0.026 per run)
- Check Volume persistence

#### 6.3 Document Usage

Create `deploy/README.md` with:

- Prerequisites
- Setup instructions
- Usage examples
- Troubleshooting

## Cost Breakdown

### Monthly Costs (10 test runs)

- **Volume storage**: $1.00/month (10GB)
- **Droplet usage**: $0.026 × 10 = $0.26
- **Data transfer**: Free (within limits)
- **Total**: ~$1.26/month

### Comparison to Alternatives

- **Persistent Droplet**: $56/month
- **Snapshot approach**: ~$10/month (10 runs)
- **Docker + Volume**: ~$1.26/month ✅ **Best value**

## Next Steps

1. ✅ Choose deployment strategy (Docker + Volume)
2. ⬜ Create DigitalOcean account
3. ✅ Install doctl CLI
4. ✅ Create Dockerfile (Python-slim)
5. ⬜ Setup Volume and download models
6. ⬜ Create automation scripts
7. ⬜ Test full workflow
8. ⬜ Document and commit

## Benefits

- **Cost-efficient**: Pay only for compute time used
- **Portable**: Same Docker image works anywhere
- **Secure**: Hosted in private DigitalOcean Container Registry (DOCR)
- **Persistent**: Models stay on Volume, no re-downloading
- **Flexible**: Easy to test different models
- **Scalable**: Can run multiple tests in parallel if needed

## Considerations

- Initial setup takes ~30-60 minutes (one-time)
- Model downloads ~10-20GB (one-time)
- Requires DigitalOcean API token management
- Need to manage Docker image updates
- Volume is region-specific (can't easily move)

## Troubleshooting

### Common Issues

1. **Volume not mounting**: Check volume ID and region match
2. **Docker image too large**: Use `.dockerignore` effectively
3. **Ollama models not found**: Verify OLLAMA_MODELS env var
4. **Droplet creation fails**: Check SSH key ID and region availability
5. **Tests timeout**: Increase timeout or check model size

### Debug Commands

```bash
# Check volume status
doctl compute volume list

# Check droplet status
doctl compute droplet list

# SSH into droplet
doctl compute ssh DROPLET_ID

# View Docker logs
docker logs CONTAINER_ID

# Check volume mount
df -h | grep complaila-storage
```

## References

- [DigitalOcean Droplet Pricing](https://www.digitalocean.com/pricing/droplets)
- [DigitalOcean API Documentation](https://docs.digitalocean.com/reference/api/)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)
- [Ollama Docker Documentation](https://hub.docker.com/r/ollama/ollama)
