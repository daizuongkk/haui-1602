"""
Broadcast simulation use case.

Builds the SMS / Zalo OA / loudspeaker payloads for an alert record to
demonstrate the distribution layer. Pure content assembly — sends nothing.
"""
from typing import List

from backend.config import settings
from backend.shared import alert_levels

DEFAULT_CHANNELS = ("sms", "zalo", "loudspeaker")
_NO_HAZARD = "Thời tiết bình thường"


def build_broadcast(record: dict, channels: List[str]) -> dict:
    level = record["highest_alert_level"]
    label = alert_levels.LABELS[level]
    emoji = alert_levels.EMOJI[level]
    hazards = ", ".join(a["hazard"] for a in record["alerts"]) or _NO_HAZARD
    vi_message = record.get("messages", {}).get("vi", "")
    audio = record.get("audio", {})

    result = {
        "location": record["location"],
        "date": record["date"],
        "highest_alert_level": level,
        "level_label": label,
        "channels": {},
        "simulated": True,
    }

    if "sms" in channels:
        text = (
            f"[{emoji} {label.upper()}] {record['location']} {record['date']}: {hazards}. "
            f"Theo doi canh bao, chu dong phong tranh. Alo 112/114 khi can cuu ho."
        )
        result["channels"]["sms"] = {
            "to": "Hộ dân đã đăng ký (mô phỏng)",
            "text": text,
            "length": len(text),
        }

    if "zalo" in channels:
        result["channels"]["zalo"] = {
            "type": "zalo_oa_notification",
            "to": "Nhóm cán bộ xã/bản theo dõi OA (mô phỏng)",
            "title": f"{emoji} Cảnh báo {label} — {record['location']}",
            "subtitle": f"{record['date']} · {hazards}",
            "body": vi_message,
            "audio": audio.get("vi"),
        }

    if "loudspeaker" in channels:
        result["channels"]["loudspeaker"] = {
            "type": "village_loudspeaker_webhook",
            "to": "Cụm loa truyền thanh xã (mô phỏng)",
            "instructions": "Phát 3 lần liên tiếp, ưu tiên giờ cao điểm sáng/chiều",
            "audio": {lang: audio.get(lang) for lang in settings.LANGUAGES},
            "has_translation": record.get("has_translation", bool(record.get("messages"))),
        }

    return result
