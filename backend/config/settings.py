"""
Central configuration — all tunable parameters and paths in one place.

Layering: this module has no project dependencies. Every other layer reads its
configuration from here (Convention over Configuration), so thresholds, model
choices, and file locations are never hardcoded inside business logic.
"""
import os
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths (data contracts shared across the pipeline, agent and API)
# --------------------------------------------------------------------------- #
# backend/config/settings.py → repo root is two levels up (backend/ → repo root).
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
LOCATIONS_FILE = DATA_DIR / "locations.json"          # 3 huyện (nguồn để sinh xã)
COMMUNES_FILE = DATA_DIR / "communes.json"            # xã/cụm xã — đơn vị dự báo vi mô
ACTIVE_ALERTS_FILE = DATA_DIR / "active_alerts.json"
OUTPUT_DIR = DATA_DIR / "output"
ALERT_MESSAGES_FILE = OUTPUT_DIR / "alert.json"
AUDIO_ROOT = OUTPUT_DIR / "audio"
ENV_FILE = PROJECT_ROOT / ".env"

# --------------------------------------------------------------------------- #
# Cơ sở dữ liệu trạng thái/vòng đời (SQLite) — tách khỏi artifact JSON pipeline.
# --------------------------------------------------------------------------- #
DB_FILE = DATA_DIR / "app.db"
DB_URL = os.getenv("DB_URL", f"sqlite:///{DB_FILE}")

# Cán bộ mẫu (xác thực nhẹ qua header X-Officer-Id — không mật khẩu).
OFFICERS_SEED = [
    {"id": "officer_pcln", "name": "Nguyễn Văn A", "role": "Trực ban PCTT&TKCN tỉnh", "district_id": None},
    {"id": "officer_mn", "name": "Lò Thị B", "role": "Cán bộ huyện Mường Nhé", "district_id": "muong_nhe"},
    {"id": "officer_tg", "name": "Vừ A C", "role": "Cán bộ huyện Tuần Giáo", "district_id": "tuan_giao"},
    {"id": "officer_mc", "name": "Giàng A D", "role": "Cán bộ huyện Mường Chà", "district_id": "muong_cha"},
]

# Số xã đại diện sinh cho mỗi huyện khi chưa có dữ liệu xã thật.
COMMUNES_PER_DISTRICT = 4

# --------------------------------------------------------------------------- #
# Weather data source (Open-Meteo)
# --------------------------------------------------------------------------- #
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_TIMEZONE = "Asia/Ho_Chi_Minh"

# 29 hourly variables requested from Open-Meteo.
WEATHER_VARIABLES = [
    "temperature_2m", "apparent_temperature", "relative_humidity_2m", "dew_point_2m",
    "precipitation", "rain", "showers", "snowfall", "snow_depth",
    "precipitation_probability", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
    "surface_pressure", "pressure_msl", "cloud_cover", "visibility",
    "soil_temperature_0cm", "soil_temperature_6cm", "soil_temperature_18cm", "soil_temperature_54cm",
    "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm",
    "soil_moisture_9_to_27cm", "soil_moisture_27_to_81cm",
    "cape", "evapotranspiration", "et0_fao_evapotranspiration",
    "freezing_level_height", "weather_code", "is_day",
]

# Atmospheric temperature lapse rate (°C per metre) for terrain downscaling.
LAPSE_RATE = 0.0065

# --------------------------------------------------------------------------- #
# Hazard thresholds — the rule engine's tunable policy. Adjust sensitivity here,
# never inside domain/hazard_rules.py.
# --------------------------------------------------------------------------- #
THRESHOLDS = {
    # 1. Điểm rủi ro Mưa lớn & Ngập úng
    "flood_yellow": 75.0,
    "flood_orange": 95.0,
    "flood_red": 115.0,

    # 2. Điểm rủi ro Lũ quét & Sạt lở đất
    "landslide_yellow": 105.0,
    "landslide_orange": 125.0,
    "landslide_red": 145.0,

    # 3. Điểm rủi ro Dông, lốc, sét
    "thunderstorm_yellow": 75.0,
    "thunderstorm_orange": 98.0,
    "thunderstorm_red": 120.0,

    # 4. Điểm rủi ro Mưa đá
    "hail_yellow": 75.0,
    "hail_orange": 98.0,
    "hail_red": 120.0,

    # 5. Điểm rủi ro Rét đậm, rét hại & Sương muối
    "cold_yellow": 30.0,
    "cold_orange": 55.0,
    "cold_red": 80.0,

    # 6. Điểm rủi ro Sương mù dày đặc (Quy đổi theo tầm nhìn xa)
    "fog_yellow": 180.0,   # Tầm nhìn < 200m
    "fog_orange": 190.0,   # Tầm nhìn < 100m
    "fog_red": 196.0,      # Tầm nhìn < 40m

    # 7. Điểm rủi ro Cháy rừng
    "wildfire_yellow": 110.0,
    "wildfire_orange": 145.0,
    "wildfire_red": 180.0,
}

# Physics/statistics that shape the landslide risk score (were inline magic numbers).
LANDSLIDE_SCORE_WEIGHTS = {"rain_24h": 0.5, "soil_moisture_deep": 150, "water_balance": 0.3}

# Neutral daily-summary defaults used only when a source series is entirely missing.
DAILY_SUMMARY_DEFAULTS = {
    "max_temp_adjusted": 25.0, "min_temp_adjusted": 15.0, "min_soil_temp_adjusted": 15.0,
    "max_precipitation_1h": 0.0, "sum_precipitation_24h": 0.0,
    "max_wind_gust": 10.0, "max_wind_speed": 5.0, "max_cape": 0.0,
    "sum_evapo_24h": 0.5, "min_freezing_height": 5000.0, "min_visibility": 10000.0,
    "avg_humidity": 80.0, "min_humidity": 60.0,
    "avg_soil_moisture_27_to_81cm": 0.3, "avg_soil_moisture_0_to_1cm": 0.3, "min_cloud": 50.0,
}

# --------------------------------------------------------------------------- #
# Language / translation
# --------------------------------------------------------------------------- #
LANGUAGES = ("vi", "thai", "hmong")
TTS_LANGUAGE_MAP = {"vi": "vi", "thai": "th", "hmong": "vi"}
TTS_RATE_LIMIT_DELAY_SECONDS = 3.0

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
GEMINI_TEMPERATURE = 0.2
GEMINI_MAX_RETRIES = 2
GEMINI_RETRY_DELAY_SECONDS = 3
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"

# --------------------------------------------------------------------------- #
# HTTP API
# --------------------------------------------------------------------------- #
# Deploy: đặt API_CORS_ORIGINS="*" hoặc "https://ten-app.vercel.app,..." qua biến môi trường.
_cors_env = os.getenv("API_CORS_ORIGINS")
API_CORS_ORIGINS = (
    [o.strip() for o in _cors_env.split(",") if o.strip()]
    if _cors_env
    else ["http://localhost:5173", "http://127.0.0.1:5173"]
)
