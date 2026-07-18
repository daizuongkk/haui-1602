"""
Pydantic schemas (DTOs) cho HTTP API — dữ liệu dự báo + vòng đời cảnh báo.

Các model này định hình tài liệu OpenAPI/Swagger. Khóa dữ liệu vị trí là cấp
**xã/cụm xã** (`commune_id`); `date` giữ định dạng `dd/mm/yyyy` (hợp đồng cũ).
"""
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

AlertLevel = Literal["Green", "Yellow", "Orange", "Red"]
Language = Literal["vi", "thai", "hmong"]
Channel = Literal["sms", "zalo", "loudspeaker"]
FeedbackKind = Literal["received", "safe", "need_help"]
AlertStatus = Literal["pending_approval", "approved", "rejected", "distributed", "closed"]


# --------------------------------------------------------------------------- #
# Địa điểm & cán bộ
# --------------------------------------------------------------------------- #
class CommuneOut(BaseModel):
    id: str
    name: str
    district_id: str
    district_name: str
    lat: float
    lon: float
    real_elevation: int
    landslide_risk_factor: float


class OfficerOut(BaseModel):
    id: str
    name: str
    role: str
    district_id: Optional[str] = None


# --------------------------------------------------------------------------- #
# Tổng quan bản đồ
# --------------------------------------------------------------------------- #
class CommuneSummary(BaseModel):
    commune_id: str
    commune_name: str
    district_id: str
    district_name: str
    latitude: float
    longitude: float
    elevation: float
    highest_alert_level: AlertLevel
    level_label: str


class SummaryResponse(BaseModel):
    communes: List[CommuneSummary]
    counts: Dict[AlertLevel, int]


# --------------------------------------------------------------------------- #
# Cảnh báo
# --------------------------------------------------------------------------- #
class WeatherSummary(BaseModel):
    min_temp: float
    max_temp: float
    total_rain: float
    max_rain_1h: float
    max_wind_gust: float
    max_cape: float
    min_visibility: float
    deep_soil_moisture: float


class HazardAlertOut(BaseModel):
    hazard: str
    level: AlertLevel
    description: str


class AlertOut(BaseModel):
    id: int
    commune_id: str
    commune_name: str
    district_id: str
    district_name: str
    latitude: float
    longitude: float
    elevation: float
    date: str = Field(description="dd/mm/yyyy")
    highest_alert_level: AlertLevel
    status: AlertStatus
    status_label: str
    weather_summary: dict
    hazards: List[HazardAlertOut]
    messages: Dict[Language, str]
    audio: Dict[Language, str]
    has_translation: bool
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejected_reason: Optional[str] = None
    note: Optional[str] = None
    feedback_counts: Dict[str, int]
    dispatch_count: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DispatchOut(BaseModel):
    id: int
    alert_id: int
    channel: Channel
    status: str = Field(description="sent_sim | failed")
    payload: dict
    officer_id: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    alert_id: int
    kind: FeedbackKind
    kind_label: str
    note: Optional[str] = None
    contact: Optional[str] = None
    created_at: Optional[str] = None


class AlertDetailOut(AlertOut):
    dispatches: List[DispatchOut]
    feedback: List[FeedbackOut]


# --------------------------------------------------------------------------- #
# Requests
# --------------------------------------------------------------------------- #
class RejectRequest(BaseModel):
    reason: str = Field(min_length=1, description="Lý do từ chối")


class StatusRequest(BaseModel):
    status: AlertStatus


class DispatchRequest(BaseModel):
    channels: List[Channel] = Field(default=["sms", "zalo", "loudspeaker"])


class FeedbackCreate(BaseModel):
    kind: FeedbackKind
    note: Optional[str] = None
    contact: Optional[str] = None


# --------------------------------------------------------------------------- #
# Pipeline & dashboard
# --------------------------------------------------------------------------- #
class PipelineRunRequest(BaseModel):
    do_translate: bool = Field(default=True, description="Sinh bản tin AI (cần GEMINI_API_KEY)")
    do_tts: bool = Field(default=True, description="Sinh audio (best-effort)")


class PipelineRunResponse(BaseModel):
    alert_records: int
    translated: int
    created: int
    updated: int
    reset_to_pending: int
    location_errors: List[dict]


class DispatchResponse(BaseModel):
    alert: AlertOut
    dispatches: List[DispatchOut]


class DashboardOverview(BaseModel):
    total_alerts: int
    level_counts: Dict[AlertLevel, int]
    status_counts: Dict[str, int]
    pending_approval: int
    distributed: int
    communes_at_risk: int
    need_help: int


class HealthResponse(BaseModel):
    status: str
    alerts: int


class ErrorResponse(BaseModel):
    detail: str
