import torch
from diffusers import StableDiffusionXLPipeline, StableVideoDiffusionPipeline
import os
import sys

# GPU Check
if not torch.cuda.is_available():
    print("CRITICAL ERROR: CUDA is not available. This application requires a NVIDIA GPU.")
    sys.exit(1)

device = "cuda"
print(f"Loading models on {device}...")

try:
    # Load SDXL
    sdxl = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True
    ).to(device)
    
    # Load SVD
    svd = StableVideoDiffusionPipeline.from_pretrained(
        "stabilityai/stable-video-diffusion-img2vid",
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True
    ).to(device)
    
    print("Models loaded successfully.")

except Exception as e:
    print(f"Failed to load models: {e}")
    sys.exit(1)
