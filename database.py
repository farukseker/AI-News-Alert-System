from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager

from models import NewsAlertRecordBase, NewsBase

from config import get_settings

from logging_config import get_logger


settings = get_settings()

# Remove `check_same_thread` since it's not needed for PostgreSQL
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

NewsBase.metadata.create_all(bind=engine)
NewsAlertRecordBase.metadata.create_all(bind=engine)

logger = get_logger(__name__)

def init_db():
    global engine, SessionLocal
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    logger.info("Database initialized", db_url=settings.DATABASE_URL)


def close_db():
    global engine
    if engine:
        engine.dispose()
        logger.info("Database connection closed")


@contextmanager
def get_db_session():
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_session():
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    with SessionLocal() as session:
        yield session