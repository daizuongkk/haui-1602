"""
Alert-merging use case: join structured alerts with multilingual bulletins.

Merge key is (location name, date). Days missing a translation are kept with an
empty `messages` and `has_translation=False` (graceful degradation).
The output dict shape is a contract consumed by the frontend — keep it stable.
"""
from typing import List, Tuple

from backend.infrastructure import audio_catalog, json_store
from backend.shared import alert_levels


def _highest_from_alerts(alerts: List[dict]) -> str:
    return alert_levels.most_severe(a.get("level", alert_levels.GREEN) for a in alerts)


def merge_records(active_alerts: List[dict], alert_messages: List[dict]) -> List[dict]:
    messages_by_key = {(m["location"], m["date"]): m for m in alert_messages}

    merged = []
    for record in active_alerts:
        key = (record["location"], record["date"])
        message = messages_by_key.get(key)
        alerts = record.get("alerts", [])

        merged.append({
            "location": record["location"],
            "location_id": record.get("location_id"),
            "latitude": record.get("latitude"),
            "longitude": record.get("longitude"),
            "elevation": record.get("elevation"),
            "date": record["date"],
            "highest_alert_level": message["highest_alert_level"] if message else _highest_from_alerts(alerts),
            "weather_summary": record.get("weather_summary", {}),
            "alerts": alerts,
            "messages": message["messages"] if message else {},
            "audio": audio_catalog.available_audio(record["location"], record["date"]),
            "has_translation": message is not None,
        })
    return merged


def load_merged() -> Tuple[List[dict], List[dict]]:
    """Read all data files and return (locations, merged_records)."""
    locations = json_store.load_locations()
    active_alerts = json_store.load_active_alerts()
    alert_messages = json_store.load_alert_messages()
    return locations, merge_records(active_alerts, alert_messages)
