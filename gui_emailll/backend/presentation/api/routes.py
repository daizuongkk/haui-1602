"""HTTP routes — thin adapters over application use cases."""
from fastapi import APIRouter, HTTPException

from backend.application.alert_merging import load_merged
from backend.application.broadcasting import build_broadcast
from backend.infrastructure import json_store
from backend.presentation.api.schemas import BroadcastRequest
from backend.shared import alert_levels

router = APIRouter(prefix="/api")


def _date_sort_key(record: dict):
    return tuple(reversed(record["date"].split("/")))  # dd/mm/yyyy → (yyyy, mm, dd)


@router.get("/locations")
def get_locations():
    return json_store.load_locations()


@router.get("/summary")
def get_summary():
    locations, merged = load_merged()
    worst_by_location = {}
    for record in merged:
        current = worst_by_location.get(record["location_id"])
        if current is None or alert_levels.PRIORITY[record["highest_alert_level"]] > alert_levels.PRIORITY[current]:
            worst_by_location[record["location_id"]] = record["highest_alert_level"]

    districts = []
    for location in locations:
        level = worst_by_location.get(location["id"], alert_levels.GREEN)
        districts.append({
            "location_id": location["id"],
            "location": location["name"],
            "latitude": location["lat"],
            "longitude": location["lon"],
            "elevation": location["real_elevation"],
            "highest_alert_level": level,
            "level_label": alert_levels.LABELS[level],
        })

    counts = {level: 0 for level in alert_levels.PRIORITY}
    for district in districts:
        counts[district["highest_alert_level"]] += 1
    return {"districts": districts, "counts": counts}


@router.get("/alerts/active")
def get_active_alerts():
    _, merged = load_merged()
    return [r for r in merged if alert_levels.PRIORITY[r["highest_alert_level"]] >= alert_levels.PRIORITY[alert_levels.YELLOW]]


@router.get("/forecast/{location_id}")
def get_forecast(location_id: str):
    locations, merged = load_merged()
    if not any(loc["id"] == location_id for loc in locations):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy địa điểm '{location_id}'")
    days = [r for r in merged if r["location_id"] == location_id]
    days.sort(key=_date_sort_key)
    return days


@router.post("/alerts/broadcast")
def broadcast_alert(request: BroadcastRequest):
    _, merged = load_merged()
    record = next(
        (r for r in merged if r["location_id"] == request.location_id and r["date"] == request.date),
        None,
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi cảnh báo cho địa điểm/ngày này")
    return build_broadcast(record, request.channels)


@router.get("/health")
def health():
    _, merged = load_merged()
    return {"status": "ok", "records": len(merged)}
