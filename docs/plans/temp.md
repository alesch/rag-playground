Python RAG System with Ollama
Setup: s-1vcpu-4gb Droplet + Block Storage for models.

Tool: DigitalOcean CLI (doctl).

1. Create the Droplet
Run the following command to spin up your Ubuntu server:

Bash

doctl compute droplet create rag-dp \
  --image ubuntu-24-04-x64 \
  --region nyc3 \
  --size s-1vcpu-4gb \
  --ssh-keys 53658267 \
  --tags rag,ollama \
  --wait

Note: Replace <your-ssh-key-id> with the ID found via doctl compute ssh-key list.

2. Prepare Block Storage
Create a dedicated volume for your LLM models to keep the root partition clean.

Bash

# Create the volume (adjust size as needed)
doctl compute volume create ollama-volume \
  --size 50 \
  --region nyc3

# Retrieve your Droplet ID
doctl compute droplet list --format ID,Name --tag-name rag

Droplet ID = 548050840

3. Attach and Mount the Volume
Connect the storage to your Droplet and prepare the file system.

Attach
Bash

doctl compute volume-action attach <volume-id> <droplet-id>
Mount (Run inside the Droplet via SSH)
Bash

ssh root@<droplet-ip>

# Create mount point and mount volume
mkdir -p /mnt/ollama
mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_ollama-volume /mnt/ollama
chmod a+rwx /mnt/ollama
4. Install Ollama & Pull Models
Install the Ollama binary directly into your mounted volume.

Bash

# Install to custom path
curl -fsSL https://ollama.com/install.sh | sudo sh -s -- -b /mnt/ollama/bin
export PATH="/mnt/ollama/bin:$PATH"

# Pull models
ollama pull llama3.2
ollama pull deepseek-r1
5. Deploy the Python RAG App
Set up your environment and run your application.

Bash

git clone https://github.com/your-org/your-rag-repo.git
cd your-rag-repo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the application
python app.py
6. Persist Mount Across Reboots
To ensure your models are available after a restart, add the volume to your fstab file:

Bash

echo '/dev/disk/by-id/scsi-0DO_Volume_ollama-volume /mnt/ollama ext4 defaults,nofail,discard 0 0' | sudo tee -a /etc/fstab
Summary Table
Step	Purpose	Key Benefit
1. Droplet	Compute Layer	4GB RAM handles Ollama + App logic.
2. Volume	Model Storage	Prevents "Disk Full" errors on root drive.
3. Attach	Connectivity	Decouples data from the specific VM instance.
4. Install	AI Engine	Custom binary path keeps the setup portable.
5. Python	Logic Layer	standard venv setup for clean dependencies.
