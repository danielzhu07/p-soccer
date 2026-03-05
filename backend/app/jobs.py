"""In-memory job store. Keys are job_id, values are job state dicts."""
from __future__ import annotations

import uuid
from typing import Any

_jobs: dict[str, dict[str, Any]] = {}


def create_job() -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "status": "pending",
        "progress": None,
        "stats": None,
        "error": None,
    }
    return job_id


def get_job(job_id: str) -> dict[str, Any] | None:
    return _jobs.get(job_id)


def update_job(job_id: str, **kwargs: Any) -> None:
    if job_id in _jobs:
        _jobs[job_id].update(kwargs)
