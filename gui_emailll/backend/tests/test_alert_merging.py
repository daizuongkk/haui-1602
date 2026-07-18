"""Tests for the alert-merging use case (frontend data contract)."""
from backend.application.alert_merging import merge_records, load_merged


def test_merge_joins_messages_by_location_and_date():
    active = [{
        "location": "Huyện X", "location_id": "x", "date": "01/01/2026",
        "latitude": 1.0, "longitude": 2.0, "elevation": 100,
        "weather_summary": {"min_temp": 10}, "alerts": [{"hazard": "H", "level": "Orange"}],
    }]
    messages = [{
        "location": "Huyện X", "date": "01/01/2026",
        "highest_alert_level": "Orange",
        "messages": {"vi": "xin chào", "thai": "...", "hmong": "..."},
    }]
    out = merge_records(active, messages)
    assert out[0]["messages"]["vi"] == "xin chào"
    assert out[0]["highest_alert_level"] == "Orange"
    assert out[0]["has_translation"] is True


def test_merge_degrades_when_translation_missing():
    active = [{
        "location": "Huyện Y", "location_id": "y", "date": "02/01/2026",
        "weather_summary": {}, "alerts": [{"hazard": "H", "level": "Red"}],
    }]
    out = merge_records(active, [])
    assert out[0]["has_translation"] is False
    assert out[0]["messages"] == {}
    assert out[0]["highest_alert_level"] == "Red"  # derived from alerts


def test_load_merged_real_data_covers_three_districts_seven_days():
    locations, merged = load_merged()
    assert len(locations) == 3
    assert len(merged) == 21
    missing = [r for r in merged if not r["has_translation"]]
    assert len(missing) == 1
    assert (missing[0]["location"], missing[0]["date"]) == ("Huyện Tuần Giáo", "20/07/2026")
    for record in merged:
        if record["has_translation"]:
            assert set(record["audio"]) == {"vi", "thai", "hmong"}
