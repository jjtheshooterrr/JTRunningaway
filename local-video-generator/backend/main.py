import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import torch

from job_store import create_job, get_job, get_recent_jobs, Job

load_dotenv()

app = FastAPI()

# CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# Pydantic models
class GenerateRequest(BaseModel):
    prompt: str
    style: Optional[str] = None
    duration_seconds: int = 4
    aspect_ratio: str = "16:9"
    seed: Optional[int] = None

class JobResponse(BaseModel):
    job_id: str
    status: str

class JobDetailResponse(BaseModel):
    job_id: str
    prompt: str
    style: Optional[str]
    duration_seconds: int
    aspect_ratio: str
    seed: Optional[int]
    status: str
    error_message: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    created_at: str

class RecentJobsResponse(BaseModel):
    jobs: list[JobDetailResponse]

# Helpers
def get_base_url():
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "8000")
    # For local dev, simpler to just assume localhost:8000 or use request.base_url in a real app
    return f"http://localhost:{port}"

def map_job_to_response(job: Job) -> JobDetailResponse:
    base_url = get_base_url()
    video_url = None
    if job.video_path:
        # video_path is relative to backend root, e.g. outputs/videos/id.mp4
        # we serve outputs/ at /outputs
        # so we need to strip 'outputs/' from the start if it's there or just construct it
        # The worker saves as backend/outputs/videos/... 
        # Let's assume worker saves relative to backend root.
        # If job.video_path is "outputs/videos/abc.mp4", then url is base_url + "/outputs/videos/abc.mp4"
        # But we mounted "outputs" at "/outputs". So if path is "outputs/...", it matches.
        video_url = f"{base_url}/{job.video_path.replace(os.sep, '/')}"
    
    thumbnail_url = None
    if job.thumbnail_path:
        thumbnail_url = f"{base_url}/{job.thumbnail_path.replace(os.sep, '/')}"

    return JobDetailResponse(
        job_id=job.id,
        prompt=job.prompt,
        style=job.style,
        duration_seconds=job.duration_seconds,
        aspect_ratio=job.aspect_ratio,
        seed=job.seed,
        status=job.status,
        error_message=job.error_message,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        created_at=job.created_at.isoformat()
    )

@app.post("/api/generate", response_model=JobResponse)
def generate(req: GenerateRequest):
    if not req.prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    if req.duration_seconds not in [2, 4, 6]:
        req.duration_seconds = 4 # Default or error? Spec says allow 2,4,6. Let's fallback to 4 if invalid or just error.
        # User spec: "duration_seconds: only allow 2, 4, or 6. If missing, default 4."
        # Pydantic handles missing default. Here we validate value.
    
    if req.aspect_ratio not in ["1:1", "16:9", "9:16"]:
        req.aspect_ratio = "16:9"

    # Derive params
    fps = 8
    num_frames = req.duration_seconds * fps
    
    width, height = 768, 432 # 16:9 default
    if req.aspect_ratio == "1:1":
        width, height = 768, 768
    elif req.aspect_ratio == "9:16":
        width, height = 432, 768
    
    seed = req.seed if req.seed is not None else random.randint(0, 2**32 - 1)

    params = {
        "fps": fps,
        "num_frames": num_frames,
        "width": width,
        "height": height,
        "seed": seed
    }

    job = create_job(
        prompt=req.prompt,
        style=req.style,
        duration_seconds=req.duration_seconds,
        aspect_ratio=req.aspect_ratio,
        seed=seed,
        params=params
    )

    return JobResponse(job_id=job.id, status=job.status)

@app.get("/api/job/{job_id}", response_model=JobDetailResponse)
def get_job_detail(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return map_job_to_response(job)

@app.get("/api/jobs/recent", response_model=RecentJobsResponse)
def get_recent(limit: int = 20, offset: int = 0):
    jobs = get_recent_jobs(limit, offset)
    return RecentJobsResponse(jobs=[map_job_to_response(j) for j in jobs])

@app.get("/api/health")
def health():
    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else "cpu"
    return {
        "status": "ok",
        "cuda": cuda_available,
        "device": device_name
    }
