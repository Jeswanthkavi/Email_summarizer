from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import (
    Email,
    EmailAnalysis,
)


def _truncate_utf8(value: str | None, max_bytes: int = 60000) -> str | None:
    """Safely truncate text so it fits MySQL TEXT (65,535 bytes) without splitting UTF-8 characters."""
    if value is None:
        return None
    encoded = value.encode("utf-8", errors="ignore")
    if len(encoded) <= max_bytes:
        return value
    return encoded[:max_bytes].decode("utf-8", errors="ignore")


# ============================================================
# SAVE EMAIL (WITH DUPLICATE PREVENTION)
# ============================================================

def save_email(
    db: Session,
    email_data: dict,
) -> Email | None:
    """Persist a fetched email if its gmail_message_id is not already stored."""
    gmail_message_id = email_data.get("gmail_message_id")
    if not gmail_message_id:
        raise ValueError("email_data must include 'gmail_message_id'")

    existing = (
        db.query(Email)
        .filter(Email.gmail_message_id == gmail_message_id)
        .first()
    )
    if existing is not None:
        return None

    received_at = email_data.get("received_at") or email_data.get("date")
    if received_at is not None:
        received_at = str(received_at)[:255]

    thread_id = email_data.get("thread_id")
    if thread_id is not None:
        thread_id = str(thread_id)[:255]

    email = Email(
        gmail_message_id=str(gmail_message_id)[:255],
        thread_id=thread_id,
        sender=_truncate_utf8(email_data.get("sender")),
        subject=_truncate_utf8(email_data.get("subject")),
        received_at=received_at,
        body=_truncate_utf8(email_data.get("body")),
    )

    try:
        db.add(email)
        db.commit()
        db.refresh(email)
        return email
    except IntegrityError:
        db.rollback()
        return None


# ============================================================
# GET UNPROCESSED EMAILS
# ============================================================

def get_unprocessed_emails(db):

    return (
        db.query(Email)
        .filter(
            Email.processed.is_(False)
        )
        .order_by(
            Email.created_at.asc()
        )
        .all()
    )


# ============================================================
# GET EMAIL ANALYSIS
# ============================================================

def get_email_analysis(
    db,
    email_id
):

    return (
        db.query(EmailAnalysis)
        .filter(
            EmailAnalysis.email_id == email_id
        )
        .first()
    )


# ============================================================
# GET RECENT EMAIL ANALYSES
# ============================================================

def get_recent_email_analyses(
    db: Session,
    limit: int = 50
):

    result = db.execute(

        select(
            Email,
            EmailAnalysis
        )
        .join(
            EmailAnalysis,
            Email.id == EmailAnalysis.email_id
        )
        .order_by(
            EmailAnalysis.analyzed_at.desc()
        )
        .limit(limit)

    )

    return result.all()


# ============================================================
# SAVE EMAIL ANALYSIS
# ============================================================

def save_email_analysis(
    db,
    email_id,
    analysis,
    commit: bool = True,
):

    if not isinstance(
        analysis,
        dict
    ):

        raise TypeError(
            "analysis must be a dictionary"
        )


    email_analysis = (
        get_email_analysis(
            db,
            email_id
        )
    )


    if email_analysis is None:

        email_analysis = EmailAnalysis(
            email_id=email_id
        )


    email_analysis.summary = (
        analysis.get(
            "summary"
        )
    )

    email_analysis.category = (
        analysis.get(
            "category"
        )
    )

    email_analysis.priority = (
        analysis.get(
            "priority"
        )
    )

    email_analysis.action_required = (
        analysis.get(
            "action_required"
        )
    )


    db.add(
        email_analysis
    )

    if commit:
        db.commit()
        db.refresh(
            email_analysis
        )
    else:
        db.flush()


    return email_analysis


# ============================================================
# MARK EMAIL AS PROCESSED
# ============================================================

def mark_email_processed(
    db,
    email_id,
    commit: bool = True,
):

    email = (
        db.query(Email)
        .filter(
            Email.id == email_id
        )
        .first()
    )


    if email is None:

        return None


    email.processed = True


    db.add(
        email
    )

    if commit:
        db.commit()
        db.refresh(
            email
        )
    else:
        db.flush()


    return email


# ============================================================
# GET EMAILS NOT YET SENT IN TELEGRAM DIGEST
# ============================================================

def get_unsent_digest_emails(
    db: Session,
    limit: int = 50
):

    result = db.execute(

        select(
            Email,
            EmailAnalysis
        )
        .join(
            EmailAnalysis,
            Email.id == EmailAnalysis.email_id
        )
        .where(
            Email.processed.is_(True)
        )
        .where(
            Email.digest_sent.is_(False)
        )
        .order_by(
            Email.created_at.asc()
        )
        .limit(limit)

    )

    return result.all()


# ============================================================
# MARK EMAILS AS SENT IN TELEGRAM DIGEST
# ============================================================

def mark_emails_digest_sent(
    db: Session,
    email_ids: list[int]
):

    if not email_ids:

        return


    result = db.execute(

        select(Email)
        .where(
            Email.id.in_(
                email_ids
            )
        )

    )


    emails = (
        result.scalars().all()
    )


    for email in emails:

        email.digest_sent = True


    db.commit()