from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    Email,
    EmailAnalysis,
)


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
    analysis
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

    db.commit()

    db.refresh(
        email_analysis
    )


    return email_analysis


# ============================================================
# MARK EMAIL AS PROCESSED
# ============================================================

def mark_email_processed(
    db,
    email_id
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

    db.commit()

    db.refresh(
        email
    )


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