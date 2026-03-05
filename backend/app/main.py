"""FastAPI app: upload video, run YOLOv8 in background, serve status and result video."""
from pathlib import Path

from fastapi import File, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from .config import JOBS_DIR
from .jobs import create_job, get_job, update_job
from . import inference

app = FastAPI(title="p-soccer", description="Football video analysis with YOLOv8")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _run_job(job_id: str) -> None:
    stats, error = inference.run(job_id)
    if error:
        update_job(job_id, status="failed", error=error)
    else:
        update_job(job_id, status="completed", stats=stats)


@app.post("/jobs")
async def create_upload_job(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload a video file and start analysis. Returns job_id for polling."""
    if not file.filename or not file.filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".webm")):
        raise HTTPException(400, detail="Please upload a video file (e.g. .mp4)")

    job_id = create_job()
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    input_path = job_dir / "input.mp4"

    try:
        contents = await file.read()
        input_path.write_bytes(contents)
    except Exception as e:
        update_job(job_id, status="failed", error=str(e))
        raise HTTPException(500, detail=f"Failed to save upload: {e}")

    background_tasks.add_task(_run_job, job_id)
    return {"job_id": job_id, "status": "pending"}


@app.get("/jobs/{job_id}")
async def job_status(job_id: str):
    """Get job status and, when completed, statistics."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, detail="Job not found")
    return job


@app.get("/jobs/{job_id}/video")
async def job_video(job_id: str):
    """Download the annotated result video."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(400, detail="Job not ready for download")

    output_path = JOBS_DIR / job_id / "output.mp4"
    if not output_path.exists():
        raise HTTPException(404, detail="Result video not found")

    return FileResponse(
        path=str(output_path),
        media_type="video/mp4",
        filename=f"p-soccer-{job_id[:8]}.mp4",
    )


# Serve frontend (static files)
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def index():
        return FileResponse(FRONTEND_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        return {"message": "p-soccer API. Upload video to POST /jobs, poll GET /jobs/{job_id}, download GET /jobs/{job_id}/video"}
