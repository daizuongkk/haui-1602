"""
Pydantic schemas (DTOs) for the HTTP API.

These models drive the auto-generated OpenAPI/Swagger documentation: every field
carries a description and the models carry realistic examples, so `/docs` and
`/redoc` fully describe request/response shapes.
"""
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.application.broadcasting import DEFAULT_CHANNELS

# Four-level severity scale used across the whole system.
AlertLevel = Literal["Green", "Yellow", "Orange", "Red"]
Language = Literal["vi", "thai", "hmong"]


# --------------------------------------------------------------------------- #
# Locations
# --------------------------------------------------------------------------- #
class LocationOut(BaseModel):
    id: str = Field(description="Mã định danh huyện", examples=["muong_nhe"])
    name: str = Field(description="Tên huyện", examples=["Huyện Mường Nhé"])
    lat: float = Field(description="Vĩ độ", examples=[22.1989])
    lon: float = Field(description="Kinh độ", examples=[102.4481])
    real_elevation: int = Field(description="Độ cao thực tế (m) — dùng để hạ độ phân giải nhiệt độ", examples=[900])
    landslide_risk_factor: float = Field(description="Hệ số rủi ro sạt lở riêng của huyện", examples=[1.2])


# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #
class DistrictSummary(BaseModel):
    location_id: str = Field(description="Mã huyện", examples=["muong_nhe"])
    location: str = Field(description="Tên huyện", examples=["Huyện Mường Nhé"])
    latitude: float = Field(examples=[22.1989])
    longitude: float = Field(examples=[102.4481])
    elevation: int = Field(description="Độ cao thực tế (m)", examples=[900])
    highest_alert_level: AlertLevel = Field(description="Mức cảnh báo cao nhất hiện tại của huyện")
    level_label: str = Field(description="Nhãn tiếng Việt của mức cảnh báo", examples=["Cực kỳ nguy hiểm"])


class SummaryResponse(BaseModel):
    districts: List[DistrictSummary] = Field(description="Mức cảnh báo hiện tại theo từng huyện (tô màu bản đồ)")
    counts: Dict[AlertLevel, int] = Field(description="Số huyện theo từng mức cảnh báo")

    model_config = ConfigDict(json_schema_extra={"example": {
        "districts": [{
            "location_id": "muong_nhe", "location": "Huyện Mường Nhé",
            "latitude": 22.1989, "longitude": 102.4481, "elevation": 900,
            "highest_alert_level": "Red", "level_label": "Cực kỳ nguy hiểm",
        }],
        "counts": {"Green": 0, "Yellow": 0, "Orange": 2, "Red": 1},
    }})


# --------------------------------------------------------------------------- #
# Alerts / Forecast
# --------------------------------------------------------------------------- #
class WeatherSummary(BaseModel):
    min_temp: float = Field(description="Nhiệt độ thấp nhất đã hiệu chỉnh (°C)", examples=[21.0])
    max_temp: float = Field(description="Nhiệt độ cao nhất đã hiệu chỉnh (°C)", examples=[28.5])
    total_rain: float = Field(description="Tổng lượng mưa 24h (mm)", examples=[59.5])
    max_rain_1h: float = Field(description="Cường độ mưa lớn nhất trong 1h (mm)", examples=[12.0])
    max_wind_gust: float = Field(description="Gió giật mạnh nhất (km/h)", examples=[19.8])
    max_cape: float = Field(description="CAPE lớn nhất (J/kg) — chỉ số đối lưu", examples=[1620.0])
    min_visibility: float = Field(description="Tầm nhìn xa thấp nhất (m)", examples=[800.0])
    deep_soil_moisture: float = Field(description="Độ ẩm đất tầng sâu 27–81cm (m³/m³)", examples=[0.42])


class HazardAlertOut(BaseModel):
    hazard: str = Field(description="Tên nhóm hiểm họa", examples=["Lũ quét & Sạt lở"])
    level: AlertLevel = Field(description="Mức cảnh báo của hiểm họa")
    description: str = Field(description="Mô tả chi tiết + khuyến cáo")


class AlertRecord(BaseModel):
    location: str = Field(examples=["Huyện Mường Nhé"])
    location_id: str = Field(examples=["muong_nhe"])
    latitude: float = Field(examples=[22.1989])
    longitude: float = Field(examples=[102.4481])
    elevation: int = Field(examples=[900])
    date: str = Field(description="Ngày dạng dd/mm/yyyy", examples=["20/07/2026"])
    highest_alert_level: AlertLevel = Field(description="Mức cảnh báo cao nhất trong ngày")
    weather_summary: WeatherSummary
    alerts: List[HazardAlertOut] = Field(description="Danh sách hiểm họa được phát hiện")
    messages: Dict[Language, str] = Field(
        default_factory=dict,
        description="Bản tin đa ngôn ngữ. Rỗng nếu ngày đó chưa có bản dịch (has_translation=false).",
    )
    audio: Dict[Language, str] = Field(
        default_factory=dict,
        description="URL file mp3 theo ngôn ngữ (chỉ gồm ngôn ngữ có audio thực tế). Phục vụ tại /audio/...",
    )
    has_translation: bool = Field(description="Ngày này đã có bản tin đa ngôn ngữ hay chưa")

    model_config = ConfigDict(json_schema_extra={"example": {
        "location": "Huyện Mường Nhé", "location_id": "muong_nhe",
        "latitude": 22.1989, "longitude": 102.4481, "elevation": 900,
        "date": "20/07/2026", "highest_alert_level": "Red",
        "weather_summary": {
            "min_temp": 21.0, "max_temp": 28.5, "total_rain": 59.5, "max_rain_1h": 12.0,
            "max_wind_gust": 19.8, "max_cape": 1620.0, "min_visibility": 800.0, "deep_soil_moisture": 0.42,
        },
        "alerts": [{
            "hazard": "Lũ quét & Sạt lở", "level": "Red",
            "description": "Đất ngậm nước bão hòa kết hợp mưa lớn. Nguy cơ lũ quét và sạt lở núi cực cao!",
        }],
        "messages": {"vi": "Mường Nhé ngày 20/07/2026: Cảnh báo đỏ về lũ quét và sạt lở...", "thai": "...", "hmong": "..."},
        "audio": {"vi": "/audio/Huy%E1%BB%87n_M%C6%B0%E1%BB%9Dng_Nh%C3%A9/20072026/vi.mp3"},
        "has_translation": True,
    }})


# --------------------------------------------------------------------------- #
# Broadcast (mô phỏng phân phối)
# --------------------------------------------------------------------------- #
class BroadcastRequest(BaseModel):
    location_id: str = Field(description="Mã huyện", examples=["muong_nhe"])
    date: str = Field(description="Ngày dạng dd/mm/yyyy", examples=["20/07/2026"])
    channels: List[Literal["sms", "zalo", "loudspeaker"]] = Field(
        default=list(DEFAULT_CHANNELS),
        description="Các kênh muốn tạo nội dung mô phỏng",
    )

    model_config = ConfigDict(json_schema_extra={"example": {
        "location_id": "muong_nhe", "date": "20/07/2026", "channels": ["sms", "zalo", "loudspeaker"],
    }})


class SmsChannel(BaseModel):
    to: str = Field(examples=["Hộ dân đã đăng ký (mô phỏng)"])
    text: str = Field(description="Nội dung SMS ngắn có mã cảnh báo emoji")
    length: int = Field(description="Số ký tự", examples=[144])


class ZaloChannel(BaseModel):
    type: str = Field(examples=["zalo_oa_notification"])
    to: str
    title: str
    subtitle: str
    body: str = Field(description="Bản tin tiếng Việt")
    audio: Optional[str] = Field(default=None, description="URL audio tiếng Việt (nếu có)")


class LoudspeakerChannel(BaseModel):
    type: str = Field(examples=["village_loudspeaker_webhook"])
    to: str
    instructions: str = Field(examples=["Phát 3 lần liên tiếp, ưu tiên giờ cao điểm sáng/chiều"])
    audio: Dict[Language, Optional[str]] = Field(description="URL audio theo 3 ngôn ngữ")
    has_translation: bool


class BroadcastChannels(BaseModel):
    sms: Optional[SmsChannel] = None
    zalo: Optional[ZaloChannel] = None
    loudspeaker: Optional[LoudspeakerChannel] = None


class BroadcastResponse(BaseModel):
    location: str = Field(examples=["Huyện Mường Nhé"])
    date: str = Field(examples=["20/07/2026"])
    highest_alert_level: AlertLevel
    level_label: str = Field(examples=["Cực kỳ nguy hiểm"])
    channels: BroadcastChannels
    simulated: bool = Field(description="Luôn true — hệ thống KHÔNG gửi tin thật", examples=[True])


# --------------------------------------------------------------------------- #
# System
# --------------------------------------------------------------------------- #
class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    records: int = Field(description="Số bản ghi cảnh báo đang có", examples=[21])


class ErrorResponse(BaseModel):
    detail: str = Field(description="Thông báo lỗi", examples=["Không tìm thấy địa điểm 'xyz'"])
