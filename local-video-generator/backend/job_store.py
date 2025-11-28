import json
import uuid
from datetime import datetime
from typing import Optional, List, Any
from sqlmodel import Field, Session, SQLModel, create_engine, select, JSON, Column

import os

# Database setup
# Use absolute path relative to this file to avoid CWD issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

sqlite_file_name = os.path.join(DATA_DIR, "jobs.db")
# SQLite URL requires 3 slashes for relative, 4 for absolute (on *nix), but on Windows it can be tricky.
# SQLAlchemy handles absolute paths well if we just pass the path.
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

class Job(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    prompt: str
    style: Optional[str] = None
    duration_seconds: int = 4
    aspect_ratio: str = "16:9"
    seed: Optional[int] = None
    status: str = "queued"  # queued, running, done, failed
    error_message: Optional[str] = None
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    params: dict = Field(default={}, sa_column=Column(JSON))

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Ensure DB exists on import
create_db_and_tables()

def create_job(
    prompt: str,
    style: Optional[str] = None,
    duration_seconds: int = 4,
    aspect_ratio: str = "16:9",
    seed: Optional[int] = None,
    params: dict = {}
) -> Job:
    with Session(engine) as session:
        job = Job(
            prompt=prompt,
            style=style,
            duration_seconds=duration_seconds,
            aspect_ratio=aspect_ratio,
            seed=seed,
            params=params
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        return job

def get_job(job_id: str) -> Optional[Job]:
    with Session(engine) as session:
        return session.get(Job, job_id)

def get_recent_jobs(limit: int = 20, offset: int = 0) -> List[Job]:
    with Session(engine) as session:
        statement = select(Job).order_by(Job.created_at.desc()).offset(offset).limit(limit)
        return session.exec(statement).all()

def get_next_queued_job() -> Optional[Job]:
    with Session(engine) as session:
        # Find the oldest queued job
        statement = select(Job).where(Job.status == "queued").order_by(Job.created_at.asc()).limit(1)
        job = session.exec(statement).first()
        
        if job:
            # "Claim" the job by setting it to running immediately
            # In a real concurrent DB we'd use FOR UPDATE, but for local SQLite this reduces race conditions
            # sufficient for a single worker or low concurrency.
            job.status = "running"
            job.updated_at = datetime.utcnow()
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        return None

def update_job_status(job_id: str, status: str, **fields: Any):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if job:
            job.status = status
            job.updated_at = datetime.utcnow()
            for key, value in fields.items():
                setattr(job, key, value)
            session.add(job)
            session.commit()
            session.refresh(job)
