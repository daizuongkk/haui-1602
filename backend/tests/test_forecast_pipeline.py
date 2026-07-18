"""Test the forecast pipeline wiring against a fake weather provider (no network)."""
from backend.application.forecast_pipeline import ForecastPipeline


class _FakeProvider:
    """Returns 24h of benign weather plus one extreme-rain hour to trigger an alert."""

    def fetch(self, lat, lon):
        hours = [f"2026-01-0{1 + h // 24}T{h % 24:02d}:00" for h in range(24)]
        base = {
            "temperature_2m": [20.0] * 24,
            "soil_temperature_0cm": [19.0] * 24,
            "precipitation": [200.0] + [0.0] * 23,  # extreme 1h rain → Red rain alert
            "wind_gusts_10m": [10.0] * 24,
            "wind_speed_10m": [5.0] * 24,
            "cape": [100.0] * 24,
            "evapotranspiration": [0.1] * 24,
            "freezing_level_height": [5000.0] * 24,
            "visibility": [10000.0] * 24,
            "relative_humidity_2m": [80.0] * 24,
            "soil_moisture_27_to_81cm": [0.3] * 24,
            "soil_moisture_0_to_1cm": [0.3] * 24,
            "cloud_cover": [50.0] * 24,
            "surface_pressure": [1010.0] * 24,
            "time": hours,
        }
        return {"elevation": 900, "hourly": base}


def test_pipeline_produces_alert_record_from_extreme_rain():
    run = ForecastPipeline(_FakeProvider()).run()
    assert not run.errors
    assert run.alert_records, "extreme rain should yield at least one alert record"
    record = run.alert_records[0]
    assert record["weather_summary"]["max_rain_1h"] == 200.0
    assert any(a["hazard"] == "Mưa lớn & Ngập úng" and a["level"] == "Red" for a in record["alerts"])
