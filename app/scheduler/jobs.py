import threading

from app.utils.logger import get_logger


logger = get_logger()

_pipeline_lock = threading.Lock()


def run_scheduled_pipeline(max_results: int = 10) -> dict | None:
    """
    Execute the email pipeline under an overlap-prevention lock.
    Exceptions are caught and logged so future scheduled runs continue unaffected.
    """
    if not _pipeline_lock.acquire(blocking=False):
        logger.warning(
            "Previous pipeline execution is still running; skipping overlapping scheduled run."
        )
        return None

    try:
        from app.main import run_pipeline

        return run_pipeline(max_results=max_results)
    except Exception:
        logger.exception("Scheduled pipeline execution failed with an unhandled error.")
        return None
    finally:
        _pipeline_lock.release()
