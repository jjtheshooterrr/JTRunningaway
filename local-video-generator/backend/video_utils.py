import imageio
import os
from PIL import Image
from typing import List

def save_video(frames: List[Image.Image], output_path: str, fps: int = 8):
    """
    Saves a list of PIL images as an MP4 video.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # imageio expects numpy arrays or filenames
    # Convert PIL images to numpy arrays if needed, but imageio.mimwrite handles PIL images too usually.
    # To be safe, let's convert.
    # frames_np = [np.array(f) for f in frames] 
    # Actually imageio handles it.
    
    imageio.mimwrite(output_path, frames, fps=fps, codec="libx264")

def save_thumbnail(image: Image.Image, output_path: str):
    """
    Saves a PIL image as a thumbnail.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)
