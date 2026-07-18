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
LOCATIONS_FILE = DATA_DIR / "locations.json"
ACTIVE_ALERTS_FILE = DATA_DIR / "active_alerts.json"
OUTPUT_DIR = DATA_DIR / "output"
ALERT_MESSAGES_FILE = OUTPUT_DIR / "alert.json"
AUDIO_ROOT = OUTPUT_DIR / "audio"
ENV_FILE = PROJECT_ROOT / ".env"

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
    "rain_heavy_24h": 50, "rain_very_heavy_24h": 100, "rain_extreme_24h": 150,
    "rain_extreme_1h": 40, "rain_heavy_1h": 25,

    "landslide_red_score": 120, "landslide_orange_score": 80,
    "landslide_soil_moist_deep": 0.35,
    "landslide_red_min_rain_24h": 50, "landslide_orange_min_rain_24h": 30,
    "landslide_yellow_min_rain_24h": 30,

    "cape_red": 2500, "cape_orange": 1500, "cape_yellow": 800,
    "cape_hail_red": 2000, "cape_hail_orange": 1200,

    "wind_gust_red": 70, "wind_gust_orange": 50,
    "pressure_drop_3h_red": 3.0, "pressure_drop_3h_orange": 2.0,

    "freezing_height_red": 3800, "freezing_height_orange": 4200,
    "hail_red_min_rain_1h": 10,

    "cold_severe_temp": 13, "cold_moderate_temp": 15,
    "frost_temp_threshold": 5, "frost_soil_temp": 0,
    "frost_red_max_cloud": 20, "frost_red_min_humidity": 80,

    "fog_red_visibility": 200, "fog_orange_visibility": 500, "fog_yellow_visibility": 1000,

    "wildfire_humidity": 45, "wildfire_temp": 35,
    "wildfire_wind_speed": 15, "wildfire_soil_moist": 0.15,
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

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
GEMINI_TEMPERATURE = 0.2
GEMINI_MAX_RETRIES = 2
GEMINI_RETRY_DELAY_SECONDS = 3
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"

# --------------------------------------------------------------------------- #
# HTTP API
# --------------------------------------------------------------------------- #
API_CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
