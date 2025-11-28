Local Video Generator Walkthrough
Setup
Prerequisites
NVIDIA GPU (16GB+ VRAM recommended)
Python 3.10+
Node.js 18+
Git
Installation
Clone the repository (if you haven't already):
git clone https://github.com/your-username/local-video-generator.git
cd local-video-generator
Backend
Navigate to backend/:
cd backend
Create virtual environment and install dependencies:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Start the API:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
Start the Worker (in a new terminal):
cd backend
.venv\Scripts\activate
python worker.py
Frontend
Navigate to frontend/:
cd frontend
Install dependencies:
npm install
Start the dev server:
npm run dev
Open http://localhost:3000.
Usage
Enter a prompt (e.g., "A cyberpunk city at night").
Select style, duration, and aspect ratio.
Click Generate Video.
Wait for the status to change from "Queued" to "Generating" to "Done".
Watch and download your video!
Verification
Health Check: http://localhost:8000/api/health should return {"status": "ok", "cuda": true, ...}.
Job Creation: Submitting a form should create a job in backend/data/jobs.db.
Video Generation: backend/outputs/videos/ should contain generated MP4 files.
