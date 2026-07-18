"""Google Text-to-Speech synthesizer (implements ports.SpeechSynthesizer)."""
from pathlib import Path

from gtts import gTTS

from backend.config import settings


class GttsSpeechSynthesizer:
    def synthesize(self, text: str, lang: str, destination: Path) -> None:
        tts_lang = settings.TTS_LANGUAGE_MAP.get(lang, "vi")
        gTTS(text=text, lang=tts_lang, slow=False).save(str(destination))
