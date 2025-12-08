"""
Scheduler service for managing cron jobs
Uses APScheduler for job scheduling and management
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Optional
import logging
import asyncio

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

        IMPORTANT: fetch_option_chain is the primary task that must complete first.
        All other tasks depend on option chain data being available in the database.
        Tasks are orchestrated to run sequentially after fetch_option_chain completes.
        """
        from app.services.tasks.fetch_option_chain import fetch_option_chain_task
        from app.services.tasks.trading_bot_analysis import trading_bot_analysis_task
        from app.services.tasks.fetch_intraday_candles import fetch_intraday_candles_task
        from datetime import datetime, time, timezone, timedelta

        async def orchestrated_task_runner():
            """
            Orchestrator that ensures fetch_option_chain runs first,
            then executes dependent tasks only if data is successfully stored.
            """
            try:
                from app.core.config import settings
                
                # Time window check (can be disabled for development)
                if not settings.SKIP_TIME_CONSTRAINT:
                    # IST is UTC+5:30
                    ist_timezone = timezone(timedelta(hours=5, minutes=30))
                    now = datetime.now(ist_timezone)
                    current_time = now.time()
                    
                    start_time = time(9, 15)
                    end_time = time(15, 30)

                    if not (start_time <= current_time <= end_time):
                        # Log only once per hour to avoid spamming, or just debug
                        # For now, using debug to keep logs clean
                        logger.debug(f"⏳ Outside trading hours ({start_time} - {end_time}). Current time: {current_time}. Skipping tasks.")
                        return
                else:
                    logger.info("⚙️ SKIP_TIME_CONSTRAINT is enabled - running analysis outside trading hours")

                logger.info("🚀 Starting orchestrated task execution...")

                # Step 1: Fetch and store option chain data (PRIMARY TASK)
                logger.info("📊 Step 1/2: Fetching option chain data...")
                await fetch_option_chain_task()
                logger.info("✅ Option chain fetch completed")

                # Step 2: Run dependent tasks sequentially
                logger.info("🤖 Step 2/2: Running dependent tasks...")

                # Task 2a: Trading bot analysis (depends on option chain data)
                try:
                    await trading_bot_analysis_task()
                except Exception as e:
                    logger.error(f"❌ Error in trading_bot_analysis_task: {str(e)}")

                # Add more dependent tasks here as needed
                # Task 2b: Another task
                # try:
                #     await another_dependent_task()
                # except Exception as e:
                #     logger.error(f"❌ Error in another_dependent_task: {str(e)}")

                # Task 2b: Fetch Intraday Candles
                try:
                    await fetch_intraday_candles_task()
                except Exception as e:
                    logger.error(f"❌ Error in fetch_intraday_candles_task: {str(e)}")

                logger.info("✅ All orchestrated tasks completed")

            except Exception as e:
                logger.error(f"❌ Error in orchestrated task runner: {str(e)}")

        # Register the orchestrated task runner - runs every minute
        self.add_job(
            func=orchestrated_task_runner,
            job_id="orchestrated_tasks",
            name="Orchestrated Tasks (Option Chain → Dependent Tasks)",
            trigger="cron",
            minute="*",  # Every minute
            # hour="9-15",  # Uncomment to run only during market hours (9 AM to 3 PM)
        )

        logger.info("✅ Orchestrated task pipeline registered")
        logger.info("📋 Execution order: fetch_option_chain → trading_bot_analysis")


# Singleton instance
scheduler_service = SchedulerService()
