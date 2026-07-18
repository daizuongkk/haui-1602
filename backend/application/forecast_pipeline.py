"""
Forecast pipeline use case: fetch → aggregate per day → evaluate hazards.

Returns structured results and never prints — presentation decides how to render.
Only days that trigger at least one alert become alert records (active_alerts.json).
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from backend.config import settings
from backend.domain.aggregation import summarize_day
from backend.domain.hazard_rules import evaluate_hazards
from backend.domain.models import DailySummary, HazardAlert, Location
from backend.infrastructure import json_store
from backend.infrastructure.ports import WeatherProvider

# Hourly variables the aggregator needs, sliced per day from the API response.
_SERIES_KEYS = (
    "temperature_2m", "soil_temperature_0cm", "precipitation", "wind_gusts_10m",
    "wind_speed_10m", "cape", "evapotranspiration", "freezing_level_height",
    "visibility", "relative_humidity_2m", "soil_moisture_27_to_81cm",
    "soil_moisture_0_to_1cm", "cloud_cover", "surface_pressure",
)
_HOURS_PER_DAY = 24


@dataclass
class DayForecast:
    location: Location
    model_elevation: float
    date: str
    summary: DailySummary
    alerts: List[HazardAlert]


@dataclass
class LocationError:
    location: Location
    message: str


@dataclass
class ForecastRun:
    days: List[DayForecast] = field(default_factory=list)
    alert_records: List[dict] = field(default_factory=list)
    errors: List[LocationError] = field(default_factory=list)


class ForecastPipeline:
    def __init__(self, weather_provider: WeatherProvider) -> None:
        self._weather = weather_provider

    def run(self) -> ForecastRun:
        run = ForecastRun()
        for location in self._load_locations():
            try:
                self._process_location(location, run)
            except Exception as exc:  # one bad location must not sink the batch
                run.errors.append(LocationError(location, str(exc)))
        return run

    @staticmethod
    def _load_locations() -> List[Location]:
        return [Location.from_dict(d) for d in json_store.load_locations()]

    def _process_location(self, location: Location, run: ForecastRun) -> None:
        raw = self._weather.fetch(location.lat, location.lon)
        model_elevation = raw.get("elevation", 0)
        hourly = raw.get("hourly", {})
        times = hourly.get("time", [])
        num_days = len(times) // _HOURS_PER_DAY

        for day_index in range(num_days):
            start = day_index * _HOURS_PER_DAY
            end = start + _HOURS_PER_DAY
            series = {key: hourly.get(key, [])[start:end] for key in _SERIES_KEYS}
            date = _format_date(times[start])

            summary = summarize_day(series, location.real_elevation, model_elevation)
            alerts = evaluate_hazards(summary, location.landslide_risk_factor)

            run.days.append(DayForecast(location, model_elevation, date, summary, alerts))
            if alerts:
                run.alert_records.append(_build_alert_record(location, date, summary, alerts))


def _format_date(iso_timestamp: str) -> str:
    date_only = iso_timestamp.split("T")[0]
    return datetime.strptime(date_only, "%Y-%m-%d").strftime("%d/%m/%Y")


def _build_alert_record(location: Location, date: str, summary: DailySummary, alerts: List[HazardAlert]) -> dict:
    return {
        "location": location.name,
        "location_id": location.id,
        "latitude": location.lat,
        "longitude": location.lon,
        "elevation": location.real_elevation,
        "date": date,
        "weather_summary": {
            "min_temp": summary["min_temp_adjusted"],
            "max_temp": summary["max_temp_adjusted"],
            "total_rain": round(summary["sum_precipitation_24h"], 1),
            "max_rain_1h": round(summary["max_precipitation_1h"], 1),
            "max_wind_gust": round(summary["max_wind_gust"], 1),
            "max_cape": round(summary["max_cape"], 1),
            "min_visibility": round(summary["min_visibility"], 1),
            "deep_soil_moisture": round(summary["avg_soil_moisture_27_to_81cm"], 2),
        },
        "alerts": [
            {"hazard": a.hazard, "level": a.level, "description": a.description} for a in alerts
        ],
    }
