import argparse

from app.scheduler.scheduler import SchedulerLockError, start_scheduler
from app.services.analysis_service import process_unprocessed_emails
from app.services.email_service import fetch_and_save_emails
from app.services.notification_service import send_email_digest
from app.utils.logger import get_logger


logger = get_logger()


def run_pipeline(max_results: int = 10) -> dict:
    """
    Execute the complete email summarizer pipeline once:
    1. Fetch new Gmail messages and persist unique emails in MySQL.
    2. Analyze unprocessed emails with Gemini and store analysis results.
    3. Build and send a Telegram digest for unsent processed emails.
    """
    logger.info("Starting AI Email Summarizer pipeline run...")

    results = {
        "new_emails_saved": 0,
        "emails_analyzed": 0,
        "digest_sent": False,
        "errors": [],
    }

    try:
        results["new_emails_saved"] = fetch_and_save_emails(max_results=max_results)
    except Exception as e:
        logger.error(f"Pipeline stage 'fetch_and_save_emails' failed: {e}")
        results["errors"].append(f"fetch: {e}")

    try:
        results["emails_analyzed"] = process_unprocessed_emails()
    except Exception as e:
        logger.error(f"Pipeline stage 'process_unprocessed_emails' failed: {e}")
        results["errors"].append(f"analyze: {e}")

    try:
        results["digest_sent"] = send_email_digest()
    except Exception as e:
        logger.error(f"Pipeline stage 'send_email_digest' failed: {e}")
        results["errors"].append(f"notify: {e}")

    logger.info(
        "Pipeline run finished | "
        f"new_emails_saved={results['new_emails_saved']} | "
        f"emails_analyzed={results['emails_analyzed']} | "
        f"digest_sent={results['digest_sent']} | "
        f"errors={len(results['errors'])}"
    )

    return results


def main():
    parser = argparse.ArgumentParser(description="AI Email Summarizer Agent")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run the pipeline once immediately and exit.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum latest Gmail messages to inspect per run (default: 10).",
    )
    args = parser.parse_args()

    if args.once:
        run_pipeline(max_results=args.max_results)
    else:
        try:
            start_scheduler(max_results=args.max_results)
        except SchedulerLockError as e:
            logger.error(str(e))
            raise SystemExit(1) from e


if __name__ == "__main__":
    main()
