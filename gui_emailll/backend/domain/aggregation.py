"""
Daily aggregation — condense 24 hourly readings into one `DailySummary`.

Pure functions extracted from the former monolithic pipeline loop. Terrain
correction is applied to temperatures here so every downstream hazard decision
uses elevation-adjusted values.
"""
from typing import List, Optional, Sequence

from backend.config import settings
from backend.domain.downscaling import downscale_temperature
from backend.domain.models import DailySummary

_DEFAULTS = settings.DAILY_SUMMARY_DEFAULTS


def _present(values: Sequence[Optional[float]]) -> List[float]:
    """Drop missing (None) readings."""
    return [v for v in values if v is not None]


def max_pressure_drop_3h(pressures: Sequence[Optional[float]]) -> float:
    """Largest fall in surface pressure across any 3-hour window (0 if none)."""
    largest = 0.0
    for i in range(len(pressures) - 3):
        start, end = pressures[i], pressures[i + 3]
        if start is not None and end is not None:
            largest = max(largest, start - end)
    return largest


def summarize_day(series: dict, real_elevation: float, model_elevation: float) -> DailySummary:
    """
    Aggregate one day's hourly series into the summary the rule engine consumes.

    `series` holds the sliced hourly lists keyed by Open-Meteo variable name.
    Neutral defaults (config.DAILY_SUMMARY_DEFAULTS) fill a metric only when its
    entire source series is missing.
    """
    temps = _present(
        downscale_temperature(t, real_elevation, model_elevation) for t in series["temperature_2m"]
    )
    soil_temps = _present(
        downscale_temperature(t, real_elevation, model_elevation) for t in series["soil_temperature_0cm"]
    )
    rains = series["precipitation"]
    present_rains = _present(rains)
    winds = _present(series["wind_gusts_10m"])
    wind_speeds = _present(series["wind_speed_10m"])
    capes = _present(series["cape"])
    evapos = _present(series["evapotranspiration"])
    freezings = _present(series["freezing_level_height"])
    visibilities = _present(series["visibility"])
    humidities = _present(series["relative_humidity_2m"])
    soil_deep = _present(series["soil_moisture_27_to_81cm"])
    soil_shallow = _present(series["soil_moisture_0_to_1cm"])
    clouds = _present(series["cloud_cover"])

    return DailySummary(
        max_temp_adjusted=max(temps) if temps else _DEFAULTS["max_temp_adjusted"],
        min_temp_adjusted=min(temps) if temps else _DEFAULTS["min_temp_adjusted"],
        min_soil_temp_adjusted=min(soil_temps) if soil_temps else _DEFAULTS["min_soil_temp_adjusted"],
        max_precipitation_1h=max(present_rains) if rains else _DEFAULTS["max_precipitation_1h"],
        sum_precipitation_24h=sum(present_rains) if rains else _DEFAULTS["sum_precipitation_24h"],
        max_wind_gust=max(winds) if winds else _DEFAULTS["max_wind_gust"],
        max_wind_speed=max(wind_speeds) if wind_speeds else _DEFAULTS["max_wind_speed"],
        max_cape=max(capes) if capes else _DEFAULTS["max_cape"],
        sum_evapo_24h=sum(evapos) if evapos else _DEFAULTS["sum_evapo_24h"],
        min_freezing_height=min(freezings) if freezings else _DEFAULTS["min_freezing_height"],
        min_visibility=min(visibilities) if visibilities else _DEFAULTS["min_visibility"],
        max_pressure_drop_3h=max_pressure_drop_3h(series["surface_pressure"]),
        avg_humidity=sum(humidities) / len(humidities) if humidities else _DEFAULTS["avg_humidity"],
        min_humidity=min(humidities) if humidities else _DEFAULTS["min_humidity"],
        avg_soil_moisture_27_to_81cm=sum(soil_deep) / len(soil_deep) if soil_deep else _DEFAULTS["avg_soil_moisture_27_to_81cm"],
        avg_soil_moisture_0_to_1cm=sum(soil_shallow) / len(soil_shallow) if soil_shallow else _DEFAULTS["avg_soil_moisture_0_to_1cm"],
        min_cloud=min(clouds) if clouds else _DEFAULTS["min_cloud"],
    )
