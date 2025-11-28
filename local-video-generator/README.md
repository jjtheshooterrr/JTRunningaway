# Local Video Generator

A local text-to-video playground using SDXL + SVD.

## Requirements
- NVIDIA GPU with ~16-24GB VRAM recommended.
- Python 3.10+
- Node.js 18+

## Setup

### Backend
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
# source .venv/bin/activate

pip install -r requirements.txt

# Start API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Worker
In a separate terminal:
```bash
cd backend
.venv\Scripts\activate
python worker.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Visit http://localhost:3000
