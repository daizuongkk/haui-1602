import sys
import os
import json
import logging
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.validator import validate_input
from agent.translator import translate_forecast
from agent.logger import setup_logger
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

logger = setup_logger()

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
ALERT_LEVEL_PRIORITY = {"Red": 3, "Orange": 2, "Yellow": 1, "Green": 0}


def get_highest_alert_level(alerts: List[Dict[str, Any]]) -> str:
    """Determine the highest alert level from a list of alerts."""
    if not alerts:
        return "Green"
    max_level = "Green"
    for alert in alerts:
        level = alert.get("level", "Green")
        if ALERT_LEVEL_PRIORITY.get(level, 0) > ALERT_LEVEL_PRIORITY.get(max_level, 0):
            max_level = level
    return max_level


def run_translation_pipeline() -> None:
    """Execute the main translation pipeline for weather alerts."""
    logger.info("Initializing multi-lingual weather alert translation pipeline.")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(project_root, "active_alerts.json")
    
    if not os.path.exists(input_file):
        input_file = os.path.join(project_root, "forecast.json")

    logger.info("Reading input data from %s", os.path.basename(input_file))

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            forecast_data = json.load(f)
    except FileNotFoundError:
        logger.error("Input file not found: %s", input_file)
        return
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format: %s", e)
        return

    is_valid, error = validate_input(forecast_data)
    if not is_valid:
        logger.error("Input validation failed: %s", error)
        return

    logger.info("Input validation successful. Total records: %d", len(forecast_data))

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY is missing from environment variables.")
        return

    all_alerts = []
    stats = {"total": len(forecast_data), "success": 0, "failed": 0}

    for idx, entry in enumerate(forecast_data):
        location = entry.get("location", "Unknown")
        date = entry.get("date", "Unknown")
        alerts = entry.get("alerts", [])
        highest_level = get_highest_alert_level(alerts)

        logger.info("Processing [%d/%d]: %s - %s (Level: %s)", idx + 1, len(forecast_data), location, date, highest_level)

        result, metadata = translate_forecast(entry, api_key)

        if result is None:
            logger.error("Translation failed for %s - %s", location, date)
            stats["failed"] += 1
            continue

        all_alerts.append(result)
        stats["success"] += 1

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "alert.json")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_alerts, f, ensure_ascii=False, indent=2)
        logger.info("Translation pipeline completed. Output saved to %s", output_path)
    except Exception as e:
        logger.error("Failed to write output file: %s", e)

    logger.info("Execution Statistics: Total=%d | Success=%d | Failed=%d", stats["total"], stats["success"], stats["failed"])


if __name__ == "__main__":
    run_translation_pipeline()
