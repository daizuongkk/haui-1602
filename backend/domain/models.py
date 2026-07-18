"""
Domain models — plain data structures with no behaviour or I/O.

`HazardAlert` is a NamedTuple so existing positional access (`alert[0]`) keeps
working while new code can read `alert.hazard`. `DailySummary` is a TypedDict:
it documents the aggregated day shape the rule engine consumes without imposing
a runtime conversion on the hot path.
"""
from dataclasses import dataclass
from typing import NamedTuple, TypedDict


class HazardAlert(NamedTuple):
    hazard: str
    level: str
    description: str


@dataclass(frozen=True)
class Location:
    id: str
    name: str
    lat: float
    lon: float
    real_elevation: float
    landslide_risk_factor: float

    @classmethod
    def from_dict(cls, data: dict) -> "Location":
        return cls(
            id=data["id"],
            name=data["name"],
            lat=data["lat"],
            lon=data["lon"],
            real_elevation=data["real_elevation"],
            landslide_risk_factor=data["landslide_risk_factor"],
        )


class DailySummary(TypedDict):
    max_temp_adjusted: float
    min_temp_adjusted: float
    min_soil_temp_adjusted: float
    max_precipitation_1h: float
    sum_precipitation_24h: float
    max_wind_gust: float
    max_wind_speed: float
    max_cape: float
    sum_evapo_24h: float
    min_freezing_height: float
    min_visibility: float
    max_pressure_drop_3h: float
    avg_humidity: float
    min_humidity: float
    avg_soil_moisture_27_to_81cm: float
    avg_soil_moisture_0_to_1cm: float
    min_cloud: float
