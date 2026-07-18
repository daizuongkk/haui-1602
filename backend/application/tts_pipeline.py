"""
Text-to-speech use case: render each non-Green bulletin to per-language MP3s.

Layout: audio/<Location>/<DDMMYYYY>/<lang>.mp3 (via infrastructure.audio_catalog).
A pause between calls avoids the TTS provider's rate limit.
"""
import time

from backend.config import settings
from backend.infrastructure import audio_catalog
from backend.infrastructure.logging_config import get_logger
from backend.infrastructure.ports import SpeechSynthesizer
from backend.shared import alert_levels


class TtsPipeline:
    def __init__(self, synthesizer: SpeechSynthesizer, logger=None) -> None:
        self._synth = synthesizer
        self._log = logger or get_logger()

    def run(self, alert_bulletins: list) -> int:
        """Generate audio for every bulletin above Green. Returns files written."""
        written = 0
        for entry in alert_bulletins:
            if entry.get("highest_alert_level", alert_levels.GREEN) == alert_levels.GREEN:
                continue
            written += self._render_entry(entry)
        return written

    def _render_entry(self, entry: dict) -> int:
        day_dir = audio_catalog.audio_dir(entry.get("location", "unknown"), entry.get("date", "unknown"))
        day_dir.mkdir(parents=True, exist_ok=True)

        written = 0
        for lang, text in entry.get("messages", {}).items():
            if not text:
                continue
            destination = day_dir / f"{lang}.mp3"
            try:
                self._synth.synthesize(text, lang, destination)
                self._log.info("Generated: %s", destination.name)
                written += 1
            except Exception as exc:  # noqa: BLE001 - one failed clip must not stop the batch
                self._log.error("TTS failed for %s: %s", destination.name, exc)
            time.sleep(settings.TTS_RATE_LIMIT_DELAY_SECONDS)
        return written
