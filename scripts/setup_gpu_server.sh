#!/bin/bash
# =============================================================================
# DGB AUDIO - ACE-Step GPU Server Setup Script
# =============================================================================
# Run this on a cloud VM with NVIDIA GPU (RunPod, Vast.ai, Lambda Labs, etc.)
# Tested on: Ubuntu 22.04 with CUDA 12.x
# =============================================================================

set -e

echo "=========================================="
echo "🎸 DGB AUDIO - ACE-Step GPU Server Setup"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt-get install -y git python3.11 python3.11-venv python3-pip ffmpeg

# Clone the repository (or use your own)
echo "📥 Cloning ACE-Step..."
cd /workspace
if [ ! -d "ACE-Step" ]; then
    git clone https://github.com/ace-step/ACE-Step.git
fi
cd ACE-Step

# Create virtual environment
echo "🐍 Creating Python environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA
echo "🔥 Installing PyTorch with CUDA..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install ACE-Step
echo "🎵 Installing ACE-Step..."
pip install -e .

# Verify GPU
echo "🖥️ Checking GPU..."
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

# Download model (this will cache it for future use)
echo "📥 Pre-downloading ACE-Step model (~6.6GB)..."
python -c "
from acestep import ACEStepPipeline
pipe = ACEStepPipeline()
print('Model downloaded successfully!')
"

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the server, run:"
echo "  cd /workspace/ACE-Step"
echo "  source venv/bin/activate"
echo "  acestep --share --port 7870"
echo ""
echo "The --share flag will give you a public URL to use remotely!"
echo "=========================================="
