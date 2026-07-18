"""
ORM models (SQLAlchemy 2.0) cho lớp trạng thái/vòng đời.

Chỉ phần CÓ TRẠNG THÁI ở đây (alert lifecycle, phân phối, phản hồi, cán bộ).
Dữ liệu dự báo thô vẫn nằm ở artifact JSON của pipeline.
"""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from backend.shared import alert_status


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Officer(Base):
    __tablename__ = "officers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="")
    district_id: Mapped[str | None] = mapped_column(String, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (UniqueConstraint("commune_id", "date", name="uq_commune_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Định danh vị trí (cấp xã) + huyện.
    commune_id: Mapped[str] = mapped_column(String, index=True)
    commune_name: Mapped[str] = mapped_column(String)
    district_id: Mapped[str] = mapped_column(String, index=True)
    district_name: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(default=0.0)
    longitude: Mapped[float] = mapped_column(default=0.0)
    elevation: Mapped[float] = mapped_column(default=0.0)

    date: Mapped[str] = mapped_column(String, index=True)      # dd/mm/yyyy (hợp đồng cũ)
    iso_date: Mapped[str] = mapped_column(String, default="")  # yyyy-mm-dd để sắp xếp

    highest_alert_level: Mapped[str] = mapped_column(String, index=True)
    weather_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    hazards: Mapped[list] = mapped_column(JSON, default=list)
    messages: Mapped[dict] = mapped_column(JSON, default=dict)
    audio: Mapped[dict] = mapped_column(JSON, default=dict)
    has_translation: Mapped[bool] = mapped_column(default=False)

    # Vòng đời.
    status: Mapped[str] = mapped_column(String, default=alert_status.PENDING, index=True)
    approved_by: Mapped[str | None] = mapped_column(ForeignKey("officers.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    dispatches: Mapped[list["Dispatch"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan"
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan"
    )


class Dispatch(Base):
    __tablename__ = "dispatches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String)           # sms | zalo | loudspeaker
    status: Mapped[str] = mapped_column(String)            # sent_sim | failed
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    officer_id: Mapped[str | None] = mapped_column(ForeignKey("officers.id"), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    alert: Mapped["Alert"] = relationship(back_populates="dispatches")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String, index=True)  # received | safe | need_help
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    alert: Mapped["Alert"] = relationship(back_populates="feedback")
