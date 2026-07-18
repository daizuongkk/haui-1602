"""CLI for text-to-speech: alert.json → per-language MP3 files."""
from backend.application.tts_pipeline import TtsPipeline
from backend.config import settings
from backend.infrastructure import json_store
from backend.infrastructure.gtts_speech import GttsSpeechSynthesizer
from backend.infrastructure.logging_config import get_logger

logger = get_logger()


def main() -> None:
    try:
        bulletins = json_store.load_alert_messages()
    except FileNotFoundError:
        logger.error("Không tìm thấy file: %s", settings.ALERT_MESSAGES_FILE)
        return

    written = TtsPipeline(GttsSpeechSynthesizer(), logger=logger).run(bulletins)
    logger.info("Hoàn thành. Đã tạo %d file audio tại: %s", written, settings.AUDIO_ROOT)


if __name__ == "__main__":
    main()
