import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List
from gtts import gTTS

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class AlertTTSGenerator:
    """
    Handles the conversion of weather alert text to speech (TTS).
    Parses structural JSON data and outputs localized audio files using Google TTS.
    """

    LANGUAGE_MAP = {
        'vi': 'vi',
        'thai': 'th',
        'hmong': 'vi'
    }

    def __init__(self, input_file: Path, output_dir: Path) -> None:
        self.input_file = input_file
        self.output_dir = output_dir

    def _read_data(self) -> List[Dict[str, Any]]:
        """Reads and parses the alert JSON file."""
        if not self.input_file.exists():
            logging.error(f"File not found: {self.input_file}")
            return []

        try:
            with self.input_file.open('r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing failed: {e}")
            return []

    def _synthesize_audio(self, text: str, lang: str, file_path: Path) -> None:
        """Invokes gTTS to generate audio."""
        try:
            tts_lang = self.LANGUAGE_MAP.get(lang, 'vi')
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            tts.save(str(file_path))
            logging.info(f"Generated: {file_path.name}")
        except Exception as e:
            logging.error(f"TTS generation failed for {file_path.name}: {e}")

    def execute(self) -> None:
        """Main execution pipeline."""
        alerts = self._read_data()
        if not alerts:
            logging.warning("No data available for processing.")
            return

        for entry in alerts:
            level = entry.get("highest_alert_level", "Green")
            if level == "Green":
                continue

            location = entry.get("location", "unknown")
            date = entry.get("date", "unknown")
            messages = entry.get("messages", {})

            # Clean names for folder creation
            safe_loc = location.replace(" ", "_")
            safe_date = date.replace("/", "")

            for lang_key, text in messages.items():
                if not text:
                    continue

                # Cấu trúc folder khoa học: audio / <Tên Huyện> / <Ngày> / <Ngôn Ngữ>.mp3
                nested_dir = self.output_dir / safe_loc / safe_date
                nested_dir.mkdir(parents=True, exist_ok=True)

                filename = f"{lang_key}.mp3"
                output_path = nested_dir / filename

                self._synthesize_audio(text, lang_key, output_path)
                time.sleep(3.0)  # Sleep 3 giây để tránh Google Rate Limit 429


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    
    generator = AlertTTSGenerator(
        input_file=base_dir / "output" / "alert.json",
        output_dir=base_dir / "output" / "audio"
    )
    generator.execute()
