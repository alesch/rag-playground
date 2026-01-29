# DigitalOcean Deployment Plan

## Overview

Deploy the Complaila RAG system to DigitalOcean using a cost-efficient architecture, with: 
- a s‑1vcpu‑8gb Droplet
- Block Storage for:
  - Databse persistance (local SQLite file), 
  - Ollama models
  - Ollama binary


## Implementation Steps

### Phase 3: DigitalOcean Infrastructure

#### 3.2 Create Initial Setup Droplet

```bash
# Create Basic 8GB Droplet
doctl compute droplet create complaila-setup \
  --region nyc3 \
  --image ubuntu-24-04-minimal \
  --size s-1vcpu-8gb \
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
# Mount volume
sudo mkdir -p /mnt/complaila-storage
sudo mount -o discard,defaults /dev/disk/by-id/scsi-0DO_Volume_complaila-storage /mnt/complaila-storage
echo '/dev/disk/by-id/scsi-0DO_Volume_complaila-storage /mnt/complaila-storage ext4 defaults,nofail,discard 0 0' | sudo tee -a /etc/fstab

# Configure Volume structure
sudo mkdir -p /mnt/complaila-storage/models
sudo mkdir -p /mnt/complaila-storage/bin
sudo mkdir -p /mnt/complaila-storage/data
sudo chown -R $(whoami):$(whoami) /mnt/complaila-storage

# Download models using the binary on the volume
export OLLAMA_MODELS=/mnt/storage/models

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
