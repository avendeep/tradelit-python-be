"""
Scheduler management endpoints
"""

from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.scheduler import scheduler_service

router = APIRouter()


@router.get("/jobs", response_model=List[Dict[str, Any]])
async def get_scheduled_jobs():
    """
    Get all registered scheduled jobs

    Returns:
        List of job details including ID, name, status (active/paused), next run time, and trigger info
    """
    jobs = scheduler_service.get_jobs()

    job_list = []
    for job in jobs:
        # A job is active if it has a next_run_time (not paused)
        is_active = job.next_run_time is not None

        job_info = {
            "id": job.id,
            "name": job.name,
            "status": "active" if is_active else "paused",
            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        }
        job_list.append(job_info)

    return job_list


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    """Pause a scheduled job"""
    scheduler_service.pause_job(job_id)
    return {"message": f"Job {job_id} paused successfully"}


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    """Resume a paused job"""
    scheduler_service.resume_job(job_id)
    return {"message": f"Job {job_id} resumed successfully"}


@router.delete("/jobs/{job_id}")
async def remove_job(job_id: str):
    """Remove a scheduled job"""
    scheduler_service.remove_job(job_id)
    return {"message": f"Job {job_id} removed successfully"}
