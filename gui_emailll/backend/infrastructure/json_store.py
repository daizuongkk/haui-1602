"""
JSON persistence — the only place that reads/writes the pipeline's data files.

Keeps UTF-8 + `ensure_ascii=False` in one spot so Vietnamese output is never
mangled, and centralises the data-contract file locations from config.
"""
import json
from pathlib import Path
from typing import Any

from backend.config import settings


def read_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_locations() -> list:
    return read_json(settings.LOCATIONS_FILE)


def load_active_alerts() -> list:
    return read_json(settings.ACTIVE_ALERTS_FILE)


def save_active_alerts(records: list) -> None:
    write_json(settings.ACTIVE_ALERTS_FILE, records)


def load_alert_messages() -> list:
    return read_json(settings.ALERT_MESSAGES_FILE)


def save_alert_messages(records: list) -> None:
    write_json(settings.ALERT_MESSAGES_FILE, records)
