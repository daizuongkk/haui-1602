"""
═══════════════════════════════════════════════════════════════════════
AI AGENT DỊCH ĐA NGÔN NGỮ BẢN TIN CẢNH BÁO THỜI TIẾT ĐIỆN BIÊN
═══════════════════════════════════════════════════════════════════════

Đọc active_alerts.json → Gọi Gemini 2.5 Pro → Xuất alert.json
(Tiếng Việt + Tiếng Thái Điện Biên + Tiếng H'Mông)

Agent KHÔNG gửi SMS / Zalo / Notification.
Điểm kết thúc là alert.json.

Cách chạy:  python app/main.py
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.validator import validate_input
from agent.translator import translate_forecast
from agent.logger import setup_logger

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

logger = setup_logger()

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
ALERT_LEVEL_PRIORITY = {"Red": 3, "Orange": 2, "Yellow": 1, "Green": 0}


def get_highest_alert_level(alerts):
    """Xác định mức cảnh báo cao nhất. Red > Orange > Yellow > Green."""
    if not alerts:
        return "Green"
    max_level = "Green"
    for alert in alerts:
        level = alert.get("level", "Green")
        if ALERT_LEVEL_PRIORITY.get(level, 0) > ALERT_LEVEL_PRIORITY.get(max_level, 0):
            max_level = level
    return max_level


def run_agent():
    print("=" * 72)
    print("  AI AGENT DICH DA NGON NGU BAN TIN CANH BAO THOI TIET DIEN BIEN")
    print("  Tieng Viet | Tieng Thai (Dien Bien) | Tieng H'Mong")
    print("=" * 72)
    print()

    # === BUOC 1: DOC DU LIEU ===
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    input_file = os.path.join(project_root, "active_alerts.json")
    if not os.path.exists(input_file):
        input_file = os.path.join(project_root, "forecast.json")

    logger.info("Buoc 1: Doc du lieu tu %s...", os.path.basename(input_file))

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            forecast_data = json.load(f)
    except FileNotFoundError:
        logger.error("Khong tim thay file: %s", input_file)
        return
    except json.JSONDecodeError as e:
        logger.error("File JSON khong hop le: %s", e)
        return

    # Validate
    logger.info("Kiem tra tinh hop le du lieu dau vao...")
    is_valid, error = validate_input(forecast_data)
    if not is_valid:
        logger.error("Du lieu khong hop le: %s", error)
        return

    logger.info("Du lieu hop le - %d ban ghi du bao", len(forecast_data))
    print()

    # Kiem tra API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("Thieu GEMINI_API_KEY! Them vao file .env: GEMINI_API_KEY=your_key_here")
        return

    # === XU LY TUNG BAN GHI ===
    all_alerts = []
    stats = {"total": len(forecast_data), "success": 0, "failed": 0}

    for idx, entry in enumerate(forecast_data):
        location = entry.get("location", "N/A")
        date = entry.get("date", "N/A")
        alerts = entry.get("alerts", [])
        highest_level = get_highest_alert_level(alerts)

        logger.info("-" * 60)
        logger.info("[%d/%d] %s - %s (Muc: %s)", idx + 1, len(forecast_data), location, date, highest_level)

        # Goi Gemini
        logger.info("  Goi Gemini 2.5 Pro...")
        result, metadata = translate_forecast(entry, api_key)

        if result is None:
            logger.error("  FAILED - Khong the dich ban tin cho %s - %s", location, date)
            stats["failed"] += 1
            continue

        all_alerts.append(result)
        stats["success"] += 1

    # === XUAT alert.json ===
    print()
    logger.info("=" * 60)
    logger.info("Xuat file alert.json...")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "alert.json")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_alerts, f, ensure_ascii=False, indent=2)
        logger.info("Xuat thanh cong: %s", output_path)
    except Exception as e:
        logger.error("Loi khi ghi file: %s", e)

    # Thong ke
    print()
    logger.info("=" * 60)
    logger.info("THONG KE:")
    logger.info("  Tong so ban ghi  : %d", stats["total"])
    logger.info("  Thanh cong       : %d", stats["success"])
    logger.info("  That bai         : %d", stats["failed"])
    logger.info("=" * 60)

    print()
    print("Agent hoan thanh. Ket qua tai: %s" % output_path)


if __name__ == "__main__":
    run_agent()
