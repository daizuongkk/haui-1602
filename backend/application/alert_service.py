"""
Use case cảnh báo: upsert từ pipeline + thao tác vòng đời (duyệt/từ chối/đổi trạng thái).

Data-access gộp thẳng vào đây (services là nơi gọi duy nhất) thay vì thêm một tầng
repository chỉ có một consumer.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.infrastructure.db.models import Alert
from backend.shared import alert_levels, alert_status


def iso_from_ddmmyyyy(date: str) -> str:
    """dd/mm/yyyy → yyyy-mm-dd (để sắp xếp). Trả nguyên nếu sai định dạng."""
    parts = date.split("/")
    if len(parts) != 3:
        return date
    dd, mm, yyyy = parts
    return f"{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"


def get_alert(session: Session, alert_id: int) -> Optional[Alert]:
    return session.get(Alert, alert_id)


def list_alerts(
    session: Session,
    status: Optional[str] = None,
    commune_id: Optional[str] = None,
    district_id: Optional[str] = None,
    date: Optional[str] = None,
) -> List[Alert]:
    stmt = select(Alert)
    if status:
        stmt = stmt.where(Alert.status == status)
    if commune_id:
        stmt = stmt.where(Alert.commune_id == commune_id)
    if district_id:
        stmt = stmt.where(Alert.district_id == district_id)
    if date:
        stmt = stmt.where(Alert.date == date)
    # Nặng nhất trước, rồi theo ngày.
    stmt = stmt.order_by(Alert.iso_date.desc())
    alerts = list(session.scalars(stmt))
    alerts.sort(key=lambda a: alert_levels.PRIORITY.get(a.highest_alert_level, 0), reverse=True)
    return alerts


def upsert_alert(session: Session, rec: dict) -> Tuple[Alert, bool, bool]:
    """
    Tạo/cập nhật một cảnh báo theo khóa (commune_id, date).
    `rec` phải có: commune_id, commune_name, district_id, district_name,
    latitude, longitude, elevation, date, highest_alert_level,
    weather_summary, hazards, messages, audio, has_translation.
    Trả về (alert, created, changed).
    """
    existing = session.scalar(
        select(Alert).where(Alert.commune_id == rec["commune_id"], Alert.date == rec["date"])
    )
    fields = {
        "commune_name": rec["commune_name"],
        "district_id": rec["district_id"],
        "district_name": rec["district_name"],
        "latitude": rec.get("latitude", 0.0),
        "longitude": rec.get("longitude", 0.0),
        "elevation": rec.get("elevation", 0.0),
        "iso_date": iso_from_ddmmyyyy(rec["date"]),
        "highest_alert_level": rec["highest_alert_level"],
        "weather_summary": rec.get("weather_summary", {}),
        "hazards": rec.get("hazards", []),
        "messages": rec.get("messages", {}),
        "audio": rec.get("audio", {}),
        "has_translation": rec.get("has_translation", bool(rec.get("messages"))),
    }

    if existing is None:
        alert = Alert(commune_id=rec["commune_id"], date=rec["date"], status=alert_status.PENDING, **fields)
        session.add(alert)
        session.flush()
        return alert, True, True

    changed = (
        existing.highest_alert_level != fields["highest_alert_level"]
        or existing.hazards != fields["hazards"]
        or existing.messages != fields["messages"]
    )
    for key, value in fields.items():
        setattr(existing, key, value)
    if changed and existing.status != alert_status.PENDING:
        # Nội dung dự báo đổi sau khi đã xử lý → phải duyệt lại.
        existing.status = alert_status.PENDING
        existing.approved_by = None
        existing.approved_at = None
        existing.note = "Dữ liệu dự báo thay đổi — cần duyệt lại."
    session.flush()
    return existing, False, changed


def approve(session: Session, alert_id: int, officer_id: str) -> Alert:
    alert = _require(session, alert_id)
    _guard(alert, alert_status.APPROVED)
    alert.status = alert_status.APPROVED
    alert.approved_by = officer_id
    alert.approved_at = datetime.now(timezone.utc)
    alert.rejected_reason = None
    session.flush()
    return alert


def reject(session: Session, alert_id: int, officer_id: str, reason: str) -> Alert:
    alert = _require(session, alert_id)
    _guard(alert, alert_status.REJECTED)
    alert.status = alert_status.REJECTED
    alert.approved_by = officer_id
    alert.rejected_reason = reason
    session.flush()
    return alert


def set_status(session: Session, alert_id: int, target: str) -> Alert:
    alert = _require(session, alert_id)
    _guard(alert, target)
    alert.status = target
    session.flush()
    return alert


class AlertError(Exception):
    """Lỗi nghiệp vụ cảnh báo (không tìm thấy / chuyển trạng thái sai luồng)."""


def _require(session: Session, alert_id: int) -> Alert:
    alert = session.get(Alert, alert_id)
    if alert is None:
        raise AlertError(f"Không tìm thấy cảnh báo #{alert_id}")
    return alert


def _guard(alert: Alert, target: str) -> None:
    if not alert_status.can_transition(alert.status, target):
        raise AlertError(
            f"Không thể chuyển '{alert_status.LABELS.get(alert.status, alert.status)}' "
            f"→ '{alert_status.LABELS.get(target, target)}'"
        )
