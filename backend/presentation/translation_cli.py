"""CLI for the translation agent: active_alerts.json → multilingual alert.json."""
import os

from dotenv import load_dotenv

from backend.application.translation_service import TranslationService
from backend.application.validation import validate_input
from backend.config import settings
from backend.infrastructure import json_store
from backend.infrastructure.gemini_client import GeminiClient
from backend.infrastructure.logging_config import get_logger

load_dotenv(settings.ENV_FILE)
logger = get_logger()


def main() -> None:
    print("=" * 72)
    print("  AI AGENT DỊCH ĐA NGÔN NGỮ BẢN TIN CẢNH BÁO THỜI TIẾT ĐIỆN BIÊN")
    print("  Tiếng Việt | Tiếng Thái (Điện Biên) | Tiếng H'Mông")
    print("=" * 72 + "\n")

    try:
        forecast_data = json_store.load_active_alerts()
    except FileNotFoundError:
        logger.error("Không tìm thấy file: %s", settings.ACTIVE_ALERTS_FILE)
        return

    is_valid, error = validate_input(forecast_data)
    if not is_valid:
        logger.error("Dữ liệu không hợp lệ: %s", error)
        return
    logger.info("Dữ liệu hợp lệ - %d bản ghi dự báo\n", len(forecast_data))

    api_key = os.getenv(settings.GEMINI_API_KEY_ENV)
    if not api_key:
        logger.error("Thiếu %s! Thêm vào file .env ở thư mục gốc", settings.GEMINI_API_KEY_ENV)
        return

    service = TranslationService(GeminiClient(api_key), logger=logger)
    bulletins, failed = [], 0
    for index, entry in enumerate(forecast_data, start=1):
        logger.info("[%d/%d] %s - %s", index, len(forecast_data), entry.get("location"), entry.get("date"))
        result = service.translate(entry)
        if result is None:
            failed += 1
            continue
        bulletins.append(result)

    json_store.save_alert_messages(bulletins)
    logger.info("=" * 60)
    logger.info("Tổng: %d | Thành công: %d | Thất bại: %d", len(forecast_data), len(bulletins), failed)
    logger.info("Kết quả: %s", settings.ALERT_MESSAGES_FILE)


if __name__ == "__main__":
    main()
