"""
Audio catalog — maps a (location, date, language) to its MP3 path and public URL.

Encapsulates the on-disk naming convention shared with the TTS writer, so the
API and the synthesizer agree without duplicating the sanitisation rules.
"""
from pathlib import Path
from urllib.parse import quote

from backend.config import settings


def _safe_location(location_name: str) -> str:
    return location_name.replace(" ", "_")


def _safe_date(date: str) -> str:
    return date.replace("/", "")


def audio_dir(location_name: str, date: str) -> Path:
    return settings.AUDIO_ROOT / _safe_location(location_name) / _safe_date(date)


def audio_url(location_name: str, date: str, lang: str) -> str:
    """Public `/audio/...` URL, percent-encoded (paths carry Vietnamese diacritics)."""
    return f"/audio/{quote(_safe_location(location_name))}/{quote(_safe_date(date))}/{lang}.mp3"


def available_audio(location_name: str, date: str) -> dict:
    """URLs only for languages whose MP3 actually exists on disk."""
    day_dir = audio_dir(location_name, date)
    return {
        lang: audio_url(location_name, date, lang)
        for lang in settings.LANGUAGES
        if (day_dir / f"{lang}.mp3").exists()
    }
