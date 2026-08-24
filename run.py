from app.database.connection import (
    Base,
    engine
)

from app.database import models

from app.utils.logger import get_logger


logger = get_logger()


def create_tables():

    try:

        Base.metadata.create_all(
            bind=engine
        )

        logger.success(
            "Database tables created successfully."
        )

    except Exception as e:

        logger.error(
            f"Failed to create database tables: {e}"
        )

        raise


if __name__ == "__main__":

    logger.info(
        "Initializing AI Email Agent database..."
    )

    create_tables()