"""Engine + session factory cho SQLite. `init_db()` tạo bảng khi khởi động."""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import settings
from backend.infrastructure.db.models import Base

# check_same_thread=False: FastAPI phục vụ nhiều thread; SQLite cần cờ này.
_engine = create_engine(
    settings.DB_URL,
    echo=False,
    connect_args={"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(_engine)


@contextmanager
def session_scope() -> Session:
    """Session có commit/rollback tự động — dùng cho CLI/script."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_engine():
    return _engine
