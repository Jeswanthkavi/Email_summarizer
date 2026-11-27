import os
import signal
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config.settings import BASE_DIR, TIMEZONE
from app.scheduler.jobs import run_scheduled_pipeline
from app.utils.logger import get_logger


logger = get_logger()

SCHEDULE_HOURS = "9,13,17,22"
SCHEDULE_MINUTE = 0
LOCK_FILE = BASE_DIR / "logs" / "scheduler.lock"


class SchedulerLockError(RuntimeError):
    """Raised when another scheduler instance already holds the process lock."""


def acquire_scheduler_lock(lock_path: Path = LOCK_FILE):
    """Acquire an OS-level non-blocking lock to prevent duplicate scheduler processes."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    handle = os.fdopen(fd, "r+")
    try:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        raise SchedulerLockError(
            f"Another scheduler instance is already running (lock: {lock_path})."
        ) from exc

    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()))
    handle.flush()
    return handle


def release_scheduler_lock(handle) -> None:
    """Release and close the OS-level scheduler process lock."""
    if handle is None:
        return
    try:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass
    finally:
        handle.close()


def _on_scheduler_event(event) -> None:
    if event.code == EVENT_JOB_ERROR:
        logger.error(f"APScheduler job '{event.job_id}' raised an error: {event.exception}")
    elif event.code == EVENT_JOB_MISSED:
        logger.warning(f"APScheduler job '{event.job_id}' missed scheduled run at {event.scheduled_run_time}.")
    elif event.code == EVENT_JOB_EXECUTED:
        logger.info(f"APScheduler job '{event.job_id}' completed.")


def build_scheduler(max_results: int = 10) -> BlockingScheduler:
    """Create and configure the BlockingScheduler for 09:00, 13:00, 17:00, 22:00 IST."""
    tz = ZoneInfo(TIMEZONE)
    scheduler = BlockingScheduler(timezone=tz)

    trigger = CronTrigger(
        hour=SCHEDULE_HOURS,
        minute=SCHEDULE_MINUTE,
        timezone=tz,
    )

    scheduler.add_job(
        run_scheduled_pipeline,
        trigger=trigger,
        kwargs={"max_results": max_results},
        id="email_digest_pipeline",
        name="AI Email Summarizer Pipeline",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
        replace_existing=True,
    )

    scheduler.add_listener(
        _on_scheduler_event,
        EVENT_JOB_ERROR | EVENT_JOB_MISSED | EVENT_JOB_EXECUTED,
    )

    return scheduler


def start_scheduler(max_results: int = 10) -> None:
    """Acquire single-instance lock and start the blocking APScheduler loop."""
    lock_handle = acquire_scheduler_lock()
    scheduler = build_scheduler(max_results=max_results)

    def _shutdown(signum, frame):
        logger.info(f"Received signal {signum}; shutting down scheduler...")
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, _shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _shutdown)

    job = scheduler.get_job("email_digest_pipeline")
    logger.info(
        f"Scheduler configured in timezone={TIMEZONE} | "
        f"schedule=09:00, 13:00, 17:00, 22:00 | "
        f"trigger={job.trigger}"
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
    finally:
        release_scheduler_lock(lock_handle)


if __name__ == "__main__":
    start_scheduler()
