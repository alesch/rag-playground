# Docker-Based Deployment Approach - Notes

## Overview

This branch contains a Docker-based deployment approach where:

1. Application code is packaged in a Docker image
2. Image is pushed to DigitalOcean Container Registry
3. A VM is created with Docker pre-installed
4. The VM pulls and runs the containerized application

## Implementation

- `Dockerfile` - Multi-stage build with Ollama binary
- `deploy/config.env` - Configuration for droplet and registry
- `deploy/create_droplet.sh` - Creates VM and mounts persistent volume
- `deploy/run_container.sh` - Runs Docker container interactively
- `deploy/destroy_droplet.sh` - Cleans up resources

## Shortcomings

### 1. Complexity

- **Nested virtualization**: VM running Docker running container
- **Multiple layers**: Ubuntu VM → Docker Engine → Container → Python
- **Harder debugging**: Need to understand both VM and container environments

### 2. Update Friction

- **Image rebuild required**: Every code change requires:
  - `docker build`
  - `docker push` (uploads ~300MB even for small changes)
  - `docker pull` on the VM
- **Slow iteration**: 2-3 minutes per code change cycle
- **Cache invalidation**: Manual pull required to get latest image

### 3. Resource Overhead

- **Docker daemon**: Consumes ~200MB RAM on the VM
- **Image storage**: Takes up VM disk space
- **Network overhead**: Pulling images over the internet

### 4. Configuration Complexity

- **Environment variables**: Must be passed through multiple layers
- **Volume mounts**: Docker volume syntax adds complexity
- **Registry authentication**: Requires token management

### 5. Cost

- **Registry storage**: $0.02/GB/month for stored images
- **Bandwidth**: Pulling 300MB images repeatedly

## When This Approach Makes Sense

- **Multi-environment deployments**: Same image runs on dev/staging/prod
- **Complex dependencies**: When you need exact reproducibility
- **Kubernetes/orchestration**: If scaling to multiple containers
- **CI/CD pipelines**: When using Docker-native tools

## Why It Doesn't Fit This Use Case

- **Single-use VMs**: We create and destroy VMs for each test run
- **Persistent volume**: Data already persists outside containers
- **Simple stack**: Just Python + Ollama, no complex dependencies
- **Infrequent changes**: Not deploying continuously

## Alternative Approach (Recommended)

Use VM snapshots instead:

1. Create base VM with Python + dependencies installed
2. Snapshot the VM (immutable, fast to boot)
3. Create VMs from snapshot for each test run
4. Clone/pull code from git at runtime
5. Run Python directly (no Docker layer)

Benefits:

- Faster iteration (git pull vs docker pull)
- Simpler architecture (one less layer)
- Lower overhead (no Docker daemon)
- Easier debugging (direct Python execution)
