"""HTTP routes — adapter mỏng trên các use case. Cấp xã + vòng đời cảnh báo."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.application import (
    alert_service,
    dispatch_service,
    feedback_service,
    seed,
)
from backend.application.run_pipeline import PipelineError, run_pipeline
from backend.infrastructure import json_store
from backend.infrastructure.db.models import Alert, Officer
from backend.infrastructure.db.session import SessionLocal
from backend.presentation.api import schemas
from backend.shared import alert_levels, alert_status

router = APIRouter(prefix="/api")


# --------------------------------------------------------------------------- #
# Dependencies
# --------------------------------------------------------------------------- #
def get_db() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def require_officer(
    x_officer_id: str = Header(..., alias="X-Officer-Id", description="Mã cán bộ đang thao tác"),
    db: Session = Depends(get_db),
) -> Officer:
    officer = db.get(Officer, x_officer_id)
    if officer is None:
        raise HTTPException(status_code=401, detail=f"Cán bộ không hợp lệ: '{x_officer_id}'")
    return officer


def get_current_officer_opt(
    x_officer_id: Optional[str] = Header(None, alias="X-Officer-Id", description="Mã cán bộ đang thao tác (tùy chọn)"),
    db: Session = Depends(get_db),
) -> Optional[Officer]:
    if not x_officer_id:
        return None
    return db.get(Officer, x_officer_id)


def _raise(exc: alert_service.AlertError):
    msg = str(exc)
    raise HTTPException(status_code=404 if msg.startswith("Không tìm thấy") else 400, detail=msg)


# --------------------------------------------------------------------------- #
# Serializers (ORM → dict)
# --------------------------------------------------------------------------- #
def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _alert_dict(db: Session, a: Alert, detail: bool = False) -> dict:
    data = {
        "id": a.id,
        "commune_id": a.commune_id,
        "commune_name": a.commune_name,
        "district_id": a.district_id,
        "district_name": a.district_name,
        "latitude": a.latitude,
        "longitude": a.longitude,
        "elevation": a.elevation,
        "date": a.date,
        "highest_alert_level": a.highest_alert_level,
        "status": a.status,
        "status_label": alert_status.LABELS.get(a.status, a.status),
        "weather_summary": a.weather_summary or {},
        "hazards": a.hazards or [],
        "messages": a.messages or {},
        "audio": a.audio or {},
        "has_translation": a.has_translation,
        "approved_by": a.approved_by,
        "approved_at": _iso(a.approved_at),
        "rejected_reason": a.rejected_reason,
        "note": a.note,
        "feedback_counts": feedback_service.counts_for_alert(db, a.id),
        "dispatch_count": len(a.dispatches),
        "created_at": _iso(a.created_at),
        "updated_at": _iso(a.updated_at),
    }
    if detail:
        data["dispatches"] = [_dispatch_dict(d) for d in
                              dispatch_service.list_dispatches(db, a.id)]
        data["feedback"] = [_feedback_dict(f) for f in
                           feedback_service.list_feedback(db, a.id)]
    return data


def _dispatch_dict(d) -> dict:
    return {
        "id": d.id, "alert_id": d.alert_id, "channel": d.channel, "status": d.status,
        "payload": d.payload or {}, "officer_id": d.officer_id, "error": d.error,
        "created_at": _iso(d.created_at),
    }


def _feedback_dict(f) -> dict:
    return {
        "id": f.id, "alert_id": f.alert_id, "kind": f.kind,
        "kind_label": alert_status.FEEDBACK_LABELS.get(f.kind, f.kind),
        "note": f.note, "contact": f.contact, "created_at": _iso(f.created_at),
    }


# --------------------------------------------------------------------------- #
# Địa điểm & cán bộ
# --------------------------------------------------------------------------- #
@router.get("/communes", response_model=List[schemas.CommuneOut], tags=["Địa điểm"],
            summary="Danh sách xã/cụm xã được giám sát")
def get_communes(officer: Optional[Officer] = Depends(get_current_officer_opt)):
    communes = seed.ensure_communes()
    if officer and officer.district_id:
        communes = [c for c in communes if c["district_id"] == officer.district_id]
    return communes


@router.get("/locations", response_model=List[schemas.CommuneOut], tags=["Địa điểm"],
            summary="Alias của /communes (tương thích ngược)")
def get_locations(officer: Optional[Officer] = Depends(get_current_officer_opt)):
    communes = seed.ensure_communes()
    if officer and officer.district_id:
        communes = [c for c in communes if c["district_id"] == officer.district_id]
    return communes


@router.get("/officers", response_model=List[schemas.OfficerOut], tags=["Cán bộ"],
            summary="Danh sách cán bộ (chọn danh tính khi phê duyệt/phát)")
def get_officers(db: Session = Depends(get_db)):
    return list(db.scalars(select(Officer)))


# --------------------------------------------------------------------------- #
# Tổng quan bản đồ
# --------------------------------------------------------------------------- #
_ACTIVE = {alert_status.PENDING, alert_status.APPROVED, alert_status.DISTRIBUTED}


@router.get("/summary", response_model=schemas.SummaryResponse, tags=["Cảnh báo"],
            summary="Mức cảnh báo cao nhất mỗi xã + đếm theo mức (tô bản đồ, KPI)")
def get_summary(db: Session = Depends(get_db)):
    communes = seed.ensure_communes()
    worst: dict = {}
    for a in db.scalars(select(Alert).where(Alert.status.in_(_ACTIVE))):
        cur = worst.get(a.commune_id)
        if cur is None or alert_levels.PRIORITY[a.highest_alert_level] > alert_levels.PRIORITY[cur]:
            worst[a.commune_id] = a.highest_alert_level

    out, counts = [], {lv: 0 for lv in alert_levels.PRIORITY}
    for c in communes:
        level = worst.get(c["id"], alert_levels.GREEN)
        counts[level] += 1
        out.append({
            "commune_id": c["id"], "commune_name": c["name"],
            "district_id": c["district_id"], "district_name": c["district_name"],
            "latitude": c["lat"], "longitude": c["lon"], "elevation": c["real_elevation"],
            "highest_alert_level": level, "level_label": alert_levels.LABELS[level],
        })
    return {"communes": out, "counts": counts}


# --------------------------------------------------------------------------- #
# Cảnh báo — danh sách / chi tiết / dự báo
# --------------------------------------------------------------------------- #
@router.get("/alerts", response_model=List[schemas.AlertOut], tags=["Cảnh báo"],
            summary="Danh sách cảnh báo (lọc theo trạng thái/xã/huyện/ngày)")
def list_alerts(
    db: Session = Depends(get_db),
    status: Optional[schemas.AlertStatus] = Query(None),
    commune_id: Optional[str] = Query(None),
    district_id: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
):
    alerts = alert_service.list_alerts(db, status=status, commune_id=commune_id,
                                       district_id=district_id, date=date)
    return [_alert_dict(db, a) for a in alerts]


@router.get("/alerts/{alert_id}", response_model=schemas.AlertDetailOut, tags=["Cảnh báo"],
            summary="Chi tiết một cảnh báo (kèm dispatch + phản hồi)")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    a = alert_service.get_alert(db, alert_id)
    if a is None:
        raise HTTPException(404, f"Không tìm thấy cảnh báo #{alert_id}")
    return _alert_dict(db, a, detail=True)


@router.get("/forecast/{commune_id}", response_model=List[schemas.AlertOut], tags=["Dự báo"],
            summary="Chuỗi dự báo/cảnh báo theo ngày của một xã")
def get_forecast(commune_id: str, db: Session = Depends(get_db)):
    alerts = alert_service.list_alerts(db, commune_id=commune_id)
    alerts.sort(key=lambda a: a.iso_date)
    return [_alert_dict(db, a) for a in alerts]


# --------------------------------------------------------------------------- #
# Vòng đời: duyệt / từ chối / trạng thái
# --------------------------------------------------------------------------- #
def _send_notifications_bg(alert_id: int):
    """Gửi email thông báo chạy nền để tránh nghẽn luồng API chính."""
    import os
    import pyodbc
    from backend.infrastructure.db.session import session_scope
    from backend.application import alert_service
    from data import notification_service
    
    conn_str = os.getenv("SQL_CONNECTION_STRING", "").strip('"').strip("'")
    if not conn_str:
        print("[WARNING] Không có SQL_CONNECTION_STRING trong .env. Bỏ qua gửi email.")
        return

    with session_scope() as session:
        a = alert_service.get_alert(session, alert_id)
        if not a:
            return
        
        alert_dict = {
            "location": a.commune_name,
            "date": a.date,
            "highest_alert_level": a.highest_alert_level,
            "messages": a.messages or {}
        }
    
    conn = None
    try:
        conn = pyodbc.connect(conn_str)
        cur = conn.cursor()
        
        # Gọi trực tiếp bộ xử lý của notification_service để truy vấn người dân từ SQL Server và gửi mail
        notification_service.process_alert(cur, alert_dict)
        conn.commit()
        print(f"✔ [NOTIFICATION] Đã tự động gửi email cho cảnh báo #{alert_id}.")
    except Exception as exc:
        print(f"❌ [NOTIFICATION] Lỗi gửi email cảnh báo tự động: {exc}")
    finally:
        if conn:
            conn.close()


@router.post("/alerts/{alert_id}/approve", response_model=schemas.AlertOut, tags=["Phê duyệt"],
             summary="Cán bộ duyệt cảnh báo")
def approve(alert_id: int, officer: Officer = Depends(require_officer), db: Session = Depends(get_db)):
    try:
        a = alert_service.approve(db, alert_id, officer.id)
        
        # Kích hoạt gửi email cảnh báo tự động chạy nền (Asynchronous)
        import threading
        threading.Thread(target=_send_notifications_bg, args=(alert_id,), daemon=True).start()
        
    except alert_service.AlertError as exc:
        _raise(exc)
    return _alert_dict(db, a)


@router.post("/alerts/{alert_id}/reject", response_model=schemas.AlertOut, tags=["Phê duyệt"],
             summary="Cán bộ từ chối cảnh báo (kèm lý do)")
def reject(alert_id: int, body: schemas.RejectRequest,
           officer: Officer = Depends(require_officer), db: Session = Depends(get_db)):
    try:
        a = alert_service.reject(db, alert_id, officer.id, body.reason)
    except alert_service.AlertError as exc:
        _raise(exc)
    return _alert_dict(db, a)


@router.patch("/alerts/{alert_id}/status", response_model=schemas.AlertOut, tags=["Phê duyệt"],
              summary="Cập nhật trạng thái (distributed/closed)")
def set_status(alert_id: int, body: schemas.StatusRequest,
               officer: Officer = Depends(require_officer), db: Session = Depends(get_db)):
    try:
        a = alert_service.set_status(db, alert_id, body.status)
    except alert_service.AlertError as exc:
        _raise(exc)
    return _alert_dict(db, a)


# --------------------------------------------------------------------------- #
# Phân phối đa kênh (mô phỏng, có log)
# --------------------------------------------------------------------------- #
@router.post("/alerts/{alert_id}/dispatch", response_model=schemas.DispatchResponse, tags=["Phân phối"],
             summary="Phát cảnh báo qua SMS/Zalo/loa (mô phỏng, lưu trạng thái)")
def dispatch(alert_id: int, body: schemas.DispatchRequest,
             officer: Officer = Depends(require_officer), db: Session = Depends(get_db)):
    try:
        result = dispatch_service.dispatch(db, alert_id, body.channels, officer.id)
        
        # Kích hoạt gửi email cảnh báo tự động chạy nền khi cán bộ bấm phát
        import threading
        threading.Thread(target=_send_notifications_bg, args=(alert_id,), daemon=True).start()
        
    except alert_service.AlertError as exc:
        _raise(exc)
    return {"alert": _alert_dict(db, result["alert"]),
            "dispatches": [_dispatch_dict(d) for d in result["dispatches"]]}


@router.get("/alerts/{alert_id}/dispatches", response_model=List[schemas.DispatchOut], tags=["Phân phối"],
            summary="Lịch sử phân phối của một cảnh báo")
def list_dispatches(alert_id: int, db: Session = Depends(get_db)):
    return [_dispatch_dict(d) for d in dispatch_service.list_dispatches(db, alert_id)]


# --------------------------------------------------------------------------- #
# Phản hồi người dân
# --------------------------------------------------------------------------- #
@router.post("/alerts/{alert_id}/feedback", response_model=schemas.FeedbackOut, tags=["Phản hồi"],
             summary="Người dân gửi phản hồi (đã nhận / an toàn / cần hỗ trợ)")
def create_feedback(alert_id: int, body: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    try:
        f = feedback_service.record_feedback(db, alert_id, body.kind, body.note, body.contact)
    except alert_service.AlertError as exc:
        _raise(exc)
    return _feedback_dict(f)


@router.get("/alerts/{alert_id}/feedback", response_model=List[schemas.FeedbackOut], tags=["Phản hồi"],
            summary="Danh sách phản hồi của một cảnh báo")
def list_feedback(alert_id: int, db: Session = Depends(get_db)):
    return [_feedback_dict(f) for f in feedback_service.list_feedback(db, alert_id)]


# --------------------------------------------------------------------------- #
# Pipeline & dashboard & health
# --------------------------------------------------------------------------- #
@router.post("/pipeline/run", response_model=schemas.PipelineRunResponse, tags=["Pipeline"],
             summary="Chạy pipeline: fetch → đánh giá → dịch → TTS → lưu (pending_approval)")
def pipeline_run(body: schemas.PipelineRunRequest, db: Session = Depends(get_db)):
    try:
        return run_pipeline(db, do_translate=body.do_translate, do_tts=body.do_tts)
    except PipelineError as exc:
        raise HTTPException(400, str(exc))


@router.get("/dashboard/overview", response_model=schemas.DashboardOverview, tags=["Dashboard"],
            summary="KPI điều hành: đếm theo mức/trạng thái, chờ duyệt, cần hỗ trợ")
def dashboard_overview(db: Session = Depends(get_db)):
    alerts = list(db.scalars(select(Alert)))
    level_counts = {lv: 0 for lv in alert_levels.PRIORITY}
    status_counts = {st: 0 for st in alert_status.ALL}
    for a in alerts:
        level_counts[a.highest_alert_level] += 1
        status_counts[a.status] += 1

    at_risk = {a.commune_id for a in alerts
               if a.status in _ACTIVE and a.highest_alert_level != alert_levels.GREEN}
    return {
        "total_alerts": len(alerts),
        "level_counts": level_counts,
        "status_counts": status_counts,
        "pending_approval": status_counts[alert_status.PENDING],
        "distributed": status_counts[alert_status.DISTRIBUTED],
        "communes_at_risk": len(at_risk),
        "need_help": feedback_service.total_need_help(db),
    }


@router.get("/health", response_model=schemas.HealthResponse, tags=["Hệ thống"])
def health(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total = db.scalar(select(func.count()).select_from(Alert)) or 0
    return {"status": "ok", "alerts": total}
