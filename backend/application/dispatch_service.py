"""
Use case phân phối: dựng payload đa kênh, 'gửi' qua MessageChannel (mô phỏng),
LƯU bản ghi dispatch và chuyển cảnh báo sang 'distributed'.

Chỉ phát khi cảnh báo đã 'approved' (hoặc 'distributed' — phát bổ sung kênh).
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.application import alert_service
from backend.application.broadcasting import build_broadcast
from backend.infrastructure import channels as channels_mod
from backend.infrastructure.db.models import Dispatch
from backend.shared import alert_status

_DISPATCHABLE = {alert_status.APPROVED, alert_status.DISTRIBUTED}


def list_dispatches(session: Session, alert_id: int) -> List[Dispatch]:
    return list(
        session.scalars(
            select(Dispatch).where(Dispatch.alert_id == alert_id).order_by(Dispatch.created_at.desc())
        )
    )


def dispatch(
    session: Session,
    alert_id: int,
    channel_names: List[str],
    officer_id: Optional[str] = None,
    adapters: Optional[dict] = None,
) -> dict:
    alert = alert_service.get_alert(session, alert_id)
    if alert is None:
        raise alert_service.AlertError(f"Không tìm thấy cảnh báo #{alert_id}")
    if alert.status not in _DISPATCHABLE:
        raise alert_service.AlertError(
            f"Chỉ phát cảnh báo đã duyệt. Trạng thái hiện tại: "
            f"'{alert_status.LABELS.get(alert.status, alert.status)}'"
        )

    adapters = adapters or channels_mod.default_channels()
    record = {
        "location": alert.commune_name,
        "date": alert.date,
        "highest_alert_level": alert.highest_alert_level,
        "alerts": alert.hazards,
        "messages": alert.messages,
        "audio": alert.audio,
        "has_translation": alert.has_translation,
    }
    built = build_broadcast(record, channel_names)

    saved: List[Dispatch] = []
    for name in channel_names:
        payload = built["channels"].get(name, {})
        adapter = adapters.get(name)
        if adapter is None:
            result_status, error = "failed", f"Kênh không hỗ trợ: {name}"
        else:
            res = adapter.send(payload)
            result_status, error = res.status, res.error
        row = Dispatch(
            alert_id=alert.id, channel=name, status=result_status,
            payload=payload, officer_id=officer_id, error=error,
        )
        session.add(row)
        saved.append(row)

    if any(d.status == "sent_sim" for d in saved) and alert.status == alert_status.APPROVED:
        alert.status = alert_status.DISTRIBUTED
    session.flush()

    return {"alert": alert, "dispatches": saved, "broadcast": built}
