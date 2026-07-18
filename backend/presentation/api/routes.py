"""HTTP routes — thin adapters over application use cases (fully documented for OpenAPI)."""
from typing import List

from fastapi import APIRouter, HTTPException, Path

from backend.application.alert_merging import load_merged
from backend.application.broadcasting import build_broadcast
from backend.infrastructure import json_store
from backend.presentation.api.schemas import (
    AlertRecord,
    BroadcastRequest,
    BroadcastResponse,
    ErrorResponse,
    HealthResponse,
    LocationOut,
    SummaryResponse,
)
from backend.shared import alert_levels

router = APIRouter(prefix="/api")

_NOT_FOUND = {404: {"model": ErrorResponse, "description": "Không tìm thấy tài nguyên"}}


def _date_sort_key(record: dict):
    return tuple(reversed(record["date"].split("/")))  # dd/mm/yyyy → (yyyy, mm, dd)


@router.get(
    "/locations",
    response_model=List[LocationOut],
    tags=["Địa điểm"],
    summary="Danh sách huyện được giám sát",
    description="Trả về 3 huyện demo (Mường Nhé, Mường Chà, Tuần Giáo) kèm toạ độ, độ cao và hệ số rủi ro sạt lở.",
)
def get_locations():
    return json_store.load_locations()


@router.get(
    "/summary",
    response_model=SummaryResponse,
    tags=["Cảnh báo"],
    summary="Tổng quan mức cảnh báo theo huyện",
    description=(
        "Mức cảnh báo cao nhất hiện tại của **từng huyện** (dùng để tô màu bản đồ) và **số huyện theo từng mức** "
        "(KPI cho dashboard). Ưu tiên mức: Red > Orange > Yellow > Green."
    ),
)
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


@router.get(
    "/alerts/active",
    response_model=List[AlertRecord],
    tags=["Cảnh báo"],
    summary="Các ngày đang có cảnh báo",
    description=(
        "Tất cả bản ghi cảnh báo đang hiệu lực (mức ≥ Vàng), đã hợp nhất số liệu thời tiết, danh sách hiểm họa, "
        "bản tin đa ngôn ngữ và URL audio."
    ),
)
def get_active_alerts():
    _, merged = load_merged()
    return [r for r in merged if alert_levels.PRIORITY[r["highest_alert_level"]] >= alert_levels.PRIORITY[alert_levels.YELLOW]]


@router.get(
    "/forecast/{location_id}",
    response_model=List[AlertRecord],
    tags=["Dự báo"],
    summary="Dự báo 3–7 ngày của một huyện",
    description="Chuỗi dự báo theo ngày (đã sắp xếp tăng dần) cho một huyện, mỗi ngày là một bản ghi đã làm giàu.",
    responses=_NOT_FOUND,
)
def get_forecast(
    location_id: str = Path(
        description="Mã huyện",
        examples=["muong_nhe"],
        openapi_examples={
            "muong_nhe": {"summary": "Huyện Mường Nhé", "value": "muong_nhe"},
            "muong_cha": {"summary": "Huyện Mường Chà", "value": "muong_cha"},
            "tuan_giao": {"summary": "Huyện Tuần Giáo", "value": "tuan_giao"},
        },
    ),
):
    locations, merged = load_merged()
    if not any(loc["id"] == location_id for loc in locations):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy địa điểm '{location_id}'")
    days = [r for r in merged if r["location_id"] == location_id]
    days.sort(key=_date_sort_key)
    return days


@router.post(
    "/alerts/broadcast",
    response_model=BroadcastResponse,
    response_model_exclude_none=True,
    tags=["Phân phối"],
    summary="Mô phỏng phân phối cảnh báo đa kênh",
    description=(
        "Dựng sẵn nội dung sẽ gửi qua **SMS / Zalo OA / loa phát thanh** cho một cảnh báo, để minh hoạ lớp phân phối. "
        "⚠️ **Chỉ mô phỏng — hệ thống không gửi tin thật.**"
    ),
    responses=_NOT_FOUND,
)
def broadcast_alert(request: BroadcastRequest):
    _, merged = load_merged()
    record = next(
        (r for r in merged if r["location_id"] == request.location_id and r["date"] == request.date),
        None,
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi cảnh báo cho địa điểm/ngày này")
    return build_broadcast(record, request.channels)


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Hệ thống"],
    summary="Kiểm tra tình trạng dịch vụ",
    description="Trạng thái dịch vụ và số bản ghi cảnh báo hiện có.",
)
def health():
    _, merged = load_merged()
    return {"status": "ok", "records": len(merged)}
