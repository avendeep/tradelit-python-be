"""
Scheduler service for managing cron jobs
Uses APScheduler for job scheduling and management
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled tasks"""

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._jobs = {}

    def start(self):
        """Start the scheduler"""
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler(
                timezone="Asia/Kolkata",  # Set to IST timezone
                job_defaults={
                    "coalesce": True,  # Combine missed runs into one
                    "max_instances": 1,  # Only one instance of each job at a time
                    "misfire_grace_time": 30,  # Allow 30 seconds grace for missed jobs
                },
            )
            logger.info("✅ Scheduler initialized")

        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Scheduler started")

    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("🛑 Scheduler shutdown")

    def add_job(
        self,
        func: Callable,
        job_id: str,
        trigger: str = "cron",
        name: Optional[str] = None,
        **trigger_args,
    ):
        """
        Add a scheduled job

        Args:
            func: The function to execute
            job_id: Unique identifier for the job
            trigger: Trigger type (default: 'cron')
            name: Human-readable job name
            **trigger_args: Additional trigger arguments (e.g., minute='*', hour='9-15')
        """
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized. Call start() first.")

        if job_id in self._jobs:
            logger.warning(f"Job {job_id} already exists. Skipping.")
            return

        job = self.scheduler.add_job(
            func, trigger, id=job_id, name=name or job_id, **trigger_args
        )

        self._jobs[job_id] = job
        logger.info(f"✅ Added scheduled job: {name or job_id} (ID: {job_id})")

    def remove_job(self, job_id: str):
        """Remove a scheduled job"""
        if job_id in self._jobs:
            self.scheduler.remove_job(job_id)
            del self._jobs[job_id]
            logger.info(f"🗑️ Removed job: {job_id}")

    def pause_job(self, job_id: str):
        """Pause a scheduled job"""
        if job_id in self._jobs:
            self.scheduler.pause_job(job_id)
            logger.info(f"⏸️ Paused job: {job_id}")

    def resume_job(self, job_id: str):
        """Resume a paused job"""
        if job_id in self._jobs:
            self.scheduler.resume_job(job_id)
            logger.info(f"▶️ Resumed job: {job_id}")

    def get_jobs(self):
        """Get all scheduled jobs"""
        if not self.scheduler:
            return []
        return self.scheduler.get_jobs()

    def register_tasks(self):
        """
        Register all scheduled tasks
        This method should be called after starting the scheduler
        Add new tasks here to keep them organized
        """
        from app.services.tasks.fetch_option_chain import fetch_option_chain_task

        # Register option chain fetch task - runs every minute
        self.add_job(
            func=fetch_option_chain_task,
            job_id="fetch_option_chain",
            name="Fetch Option Chain Data",
            trigger="cron",
            minute="*",  # Every minute
            # hour="9-15",  # Uncomment to run only during market hours (9 AM to 3 PM)
        )

        # Add more tasks here as needed
        # Example:
        # self.add_job(
        #     func=another_task,
        #     job_id="another_task_id",
        #     name="Another Task Name",
        #     trigger="cron",
        #     minute="*/5",  # Every 5 minutes
        # )

        logger.info("✅ All scheduled tasks registered")


# Singleton instance
scheduler_service = SchedulerService()
