"""Tests for the pure domain: downscaling, aggregation, hazard rules, levels."""
from backend.domain.aggregation import max_pressure_drop_3h, summarize_day
from backend.domain.downscaling import downscale_temperature
from backend.domain.hazard_rules import evaluate_hazards
from backend.shared import alert_levels


def test_downscale_applies_lapse_rate():
    # 100 m higher than the model grid → ~0.65 °C colder.
    assert downscale_temperature(20.0, real_elevation=1000, model_elevation=900) == 19.4


def test_downscale_passes_through_none():
    assert downscale_temperature(None, 1000, 900) is None


def test_max_pressure_drop_ignores_missing_and_finds_largest():
    pressures = [1010, 1008, 1006, 1000, None, 1002]
    assert max_pressure_drop_3h(pressures) == 10  # 1010 → 1000 over 3h


def test_summarize_day_uses_defaults_for_empty_series():
    empty = {k: [] for k in (
        "temperature_2m", "soil_temperature_0cm", "precipitation", "wind_gusts_10m",
        "wind_speed_10m", "cape", "evapotranspiration", "freezing_level_height",
        "visibility", "relative_humidity_2m", "soil_moisture_27_to_81cm",
        "soil_moisture_0_to_1cm", "cloud_cover", "surface_pressure",
    )}
    summary = summarize_day(empty, real_elevation=900, model_elevation=900)
    assert summary["max_temp_adjusted"] == 25.0
    assert summary["sum_precipitation_24h"] == 0.0


def test_levels_most_severe():
    assert alert_levels.most_severe(["Yellow", "Red", "Orange"]) == "Red"
    assert alert_levels.most_severe([]) == "Green"


def test_hazard_rules_return_named_tuples_with_index_access():
    day = {
        "max_precipitation_1h": 45.0, "sum_precipitation_24h": 160.0,
        "avg_soil_moisture_27_to_81cm": 0.43, "avg_soil_moisture_0_to_1cm": 0.45,
        "sum_evapo_24h": 0.2, "max_cape": 1200, "max_wind_gust": 35.0, "max_wind_speed": 12.0,
        "min_freezing_height": 5200.0, "min_temp_adjusted": 21.0, "min_soil_temp_adjusted": 20.0,
        "min_visibility": 800.0, "max_pressure_drop_3h": 1.0, "avg_humidity": 98.0,
        "min_humidity": 90.0, "min_cloud": 95.0,
    }
    alerts = evaluate_hazards(day, landslide_risk_factor=1.2)
    by_hazard = {a.hazard: a.level for a in alerts}
    assert by_hazard["Lũ quét & Sạt lở"] == "Red"
    assert by_hazard["Mưa lớn & Ngập úng"] == "Red"
    assert alerts[0][0] == alerts[0].hazard  # positional access preserved
