"""
Nạp dữ liệu khởi tạo vào DB.

- `seed_officers`: cán bộ mẫu (idempotent) để header X-Officer-Id hoạt động.
- `seed_demo_alerts`: ánh xạ 21 bản ghi cảnh báo THẬT hiện có (active_alerts.json +
  alert.json + audio) xuống các xã, tạo cảnh báo `pending_approval`. Nhờ đó toàn bộ
  workflow (duyệt → phát → phản hồi) demo được OFFLINE, không cần LLM/mạng.
"""
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.application import alert_service, communes as communes_gen
from backend.application.alert_merging import load_merged
from backend.config import settings
from backend.infrastructure import json_store
from backend.infrastructure.db.models import Officer


def seed_officers(session: Session) -> int:
    added = 0
    for spec in settings.OFFICERS_SEED:
        if session.get(Officer, spec["id"]) is None:
            session.add(Officer(id=spec["id"], name=spec["name"], role=spec.get("role", "")))
            added += 1
    session.flush()
    return added


def ensure_communes() -> List[dict]:
    communes = json_store.load_communes()
    if not communes:
        communes = communes_gen.generate_and_save()
    return communes


def seed_demo_alerts(session: Session, dates_per_commune: int = 3) -> int:
    """Tạo cảnh báo demo cho từng xã từ dữ liệu thật của huyện tương ứng."""
    communes = ensure_communes()
    _, merged = load_merged()  # 21 bản ghi thật (đã kèm messages + audio)

    by_district: dict[str, list] = {}
    for rec in merged:
        by_district.setdefault(rec.get("location_id"), []).append(rec)
    for recs in by_district.values():
        recs.sort(key=lambda r: alert_service.iso_from_ddmmyyyy(r["date"]), reverse=True)

    created = 0
    for commune in communes:
        district_recs = by_district.get(commune["district_id"], [])[:dates_per_commune]
        for src in district_recs:
            rec = {
                "commune_id": commune["id"],
                "commune_name": commune["name"],
                "district_id": commune["district_id"],
                "district_name": commune["district_name"],
                "latitude": commune["lat"],
                "longitude": commune["lon"],
                "elevation": commune["real_elevation"],
                "date": src["date"],
                "highest_alert_level": src["highest_alert_level"],
                "weather_summary": src.get("weather_summary", {}),
                "hazards": src.get("alerts", []),
                "messages": src.get("messages", {}),
                "audio": src.get("audio", {}),
                "has_translation": src.get("has_translation", bool(src.get("messages"))),
            }
            _, was_created, _ = alert_service.upsert_alert(session, rec)
            created += int(was_created)
    return created


def seed_all(session: Session) -> dict:
    return {
        "officers": seed_officers(session),
        "communes": len(ensure_communes()),
        "alerts": seed_demo_alerts(session),
    }
