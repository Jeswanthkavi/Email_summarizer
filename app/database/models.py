from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.connection import Base


class Email(Base):

    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    gmail_message_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    thread_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    sender: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    subject: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    received_at: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    digest_sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    analysis = relationship(
        "EmailAnalysis",
        back_populates="email",
        uselist=False,
        cascade="all, delete-orphan"
    )

class EmailAnalysis(Base):

    __tablename__ = "email_analysis"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    email_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "emails.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    priority: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    action_required: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    email = relationship(
        "Email",
        back_populates="analysis"
    )