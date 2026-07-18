"""
Use case phản hồi: ghi phản hồi người dân + tổng hợp đếm theo loại.

kind ∈ {received (đã nhận), safe (an toàn), need_help (cần hỗ trợ)}.
"""
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.application import alert_service
from backend.infrastructure.db.models import Feedback
from backend.shared import alert_status


def record_feedback(
    session: Session,
    alert_id: int,
    kind: str,
    note: Optional[str] = None,
    contact: Optional[str] = None,
) -> Feedback:
    if kind not in alert_status.FEEDBACK_KINDS:
        raise alert_service.AlertError(f"Loại phản hồi không hợp lệ: {kind}")
    if alert_service.get_alert(session, alert_id) is None:
        raise alert_service.AlertError(f"Không tìm thấy cảnh báo #{alert_id}")
    row = Feedback(alert_id=alert_id, kind=kind, note=note, contact=contact)
    session.add(row)
    session.flush()
    return row


def list_feedback(session: Session, alert_id: int) -> List[Feedback]:
    return list(
        session.scalars(
            select(Feedback).where(Feedback.alert_id == alert_id).order_by(Feedback.created_at.desc())
        )
    )


def counts_for_alert(session: Session, alert_id: int) -> dict:
    rows = session.execute(
        select(Feedback.kind, func.count()).where(Feedback.alert_id == alert_id).group_by(Feedback.kind)
    ).all()
    counts = {k: 0 for k in alert_status.FEEDBACK_KINDS}
    for kind, n in rows:
        counts[kind] = n
    return counts


def total_need_help(session: Session) -> int:
    return session.scalar(
        select(func.count()).select_from(Feedback).where(Feedback.kind == "need_help")
    ) or 0
