import time
import torch
import os
from job_store import get_next_queued_job, update_job_status
from models import sdxl, svd, device
from video_utils import save_video, save_thumbnail

def generate_video_for_job(job):
    print(f"Starting job {job.id}...")
    
    # 1. Build prompt
    full_prompt = job.prompt
    if job.style and job.style != "None":
        full_prompt = f"{job.style}, 4k, high quality: {job.prompt}"
    
    params = job.params
    width = params.get("width", 768)
    height = params.get("height", 432)
    num_frames = params.get("num_frames", 32)
    fps = params.get("fps", 8)
    seed = params.get("seed", 0)
    
    generator = torch.Generator(device=device).manual_seed(seed)
    
    # 2. Text -> Image (SDXL)
    print("Generating image...")
    image = sdxl(
        prompt=full_prompt,
        width=width,
        height=height,
        num_inference_steps=30,
        generator=generator
    ).images[0]
    
    # 3. Image -> Video (SVD)
    print("Generating video frames...")
    # SVD typically takes 1024x576 or similar. We might need to resize if aspect ratio is vastly different
    # But for now let's pass the image as is. SVD resizes internally or we might need to be careful.
    # The user spec said "Use width & height" for SDXL. SVD usually works best with specific resolutions but let's try.
    
    frames = svd(
        image,
        num_frames=num_frames,
        decode_chunk_size=8,
        generator=generator,
        num_inference_steps=30
    ).frames[0]
    
    # 4. Save
    video_filename = f"{job.id}.mp4"
    thumb_filename = f"{job.id}.jpg"
    
    # Paths relative to backend root
    video_path = os.path.join("outputs", "videos", video_filename)
    thumb_path = os.path.join("outputs", "thumbs", thumb_filename)
    
    print(f"Saving to {video_path}...")
    save_video(frames, video_path, fps=fps)
    
    # Save thumbnail (first frame)
    save_thumbnail(frames[0], thumb_path)
    
    return video_path, thumb_path

def main():
    print("Worker started. Waiting for jobs...")
    while True:
        try:
            job = get_next_queued_job()
            if not job:
                time.sleep(1)
                continue
            
            print(f"Picked up job {job.id}")
            # Status is already 'running' from get_next_queued_job (claim)
            
            try:
                video_path, thumb_path = generate_video_for_job(job)
                update_job_status(
                    job.id,
                    "done",
                    video_path=video_path,
                    thumbnail_path=thumb_path
                )
                print(f"Job {job.id} completed.")
            except Exception as e:
                print(f"Job {job.id} failed: {e}")
                update_job_status(job.id, "failed", error_message=str(e))
                torch.cuda.empty_cache()
                
        except Exception as e:
            print(f"Worker loop error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
