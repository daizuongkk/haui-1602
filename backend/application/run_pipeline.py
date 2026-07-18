"""
Orchestrator: chạy toàn bộ chuỗi và lưu cảnh báo vào DB (trạng thái pending_approval).

  fetch (Open-Meteo, theo xã) → đánh giá hiểm họa → ghi active_alerts.json
  → dịch đa ngôn ngữ (Gemini, BẮT BUỘC có key) → TTS (best-effort)
  → hợp nhất → upsert vào DB.

Tách khỏi CLI: presentation chỉ gọi hàm này rồi hiển thị kết quả.
"""
import os
from typing import Optional

from sqlalchemy.orm import Session

from backend.application import alert_service
from backend.application.alert_merging import merge_records
from backend.application.forecast_pipeline import ForecastPipeline
from backend.application.translation_service import TranslationService
from backend.application.tts_pipeline import TtsPipeline
from backend.config import settings
from backend.infrastructure import json_store
from backend.infrastructure.gemini_client import GeminiClient
from backend.infrastructure.gtts_speech import GttsSpeechSynthesizer
from backend.infrastructure.logging_config import get_logger
from backend.infrastructure.openmeteo import OpenMeteoWeatherProvider
from backend.infrastructure.ports import LlmJsonClient, SpeechSynthesizer, WeatherProvider


class PipelineError(Exception):
    """Lỗi orchestrator (ví dụ thiếu GEMINI_API_KEY khi cần dịch)."""


def run_pipeline(
    session: Session,
    *,
    weather: Optional[WeatherProvider] = None,
    llm: Optional[LlmJsonClient] = None,
    synth: Optional[SpeechSynthesizer] = None,
    do_translate: bool = True,
    do_tts: bool = True,
    logger=None,
) -> dict:
    log = logger or get_logger()
    weather = weather or OpenMeteoWeatherProvider()

    run = ForecastPipeline(weather).run()
    json_store.save_active_alerts(run.alert_records)
    log.info("Pipeline: %d bản ghi cảnh báo, %d lỗi địa điểm", len(run.alert_records), len(run.errors))

    bulletins = []
    if do_translate and run.alert_records:
        llm = llm or _default_llm()
        service = TranslationService(llm, logger=log)
        # Tạm thời chỉ dịch 1 bản ghi đầu tiên để kiểm tra hệ thống chạy nhanh
        for entry in run.alert_records[:1]:
            result = service.translate(entry)
            if result:
                bulletins.append(result)
            # Tránh lỗi rate limit 15 RPM của gói Gemini miễn phí
            import time
            time.sleep(2.5)
        json_store.save_alert_messages(bulletins)

    if do_tts and bulletins:
        try:
            TtsPipeline(synth or GttsSpeechSynthesizer(), logger=log).run(bulletins)
        except Exception as exc:  # noqa: BLE001 - audio là best-effort, không chặn pipeline
            log.error("TTS thất bại (bỏ qua): %s", exc)

    merged = merge_records(run.alert_records, bulletins)
    communes_by_id = {c["id"]: c for c in json_store.load_communes()}

    created = updated = changed_count = 0
    for m in merged:
        commune = communes_by_id.get(m.get("location_id"), {})
        rec = _to_upsert_record(m, commune)
        _, was_created, was_changed = alert_service.upsert_alert(session, rec)
        created += int(was_created)
        updated += int(not was_created)
        changed_count += int(was_changed and not was_created)

    return {
        "alert_records": len(run.alert_records),
        "translated": len(bulletins),
        "created": created,
        "updated": updated,
        "reset_to_pending": changed_count,
        "location_errors": [{"location": e.location.name, "error": e.message} for e in run.errors],
    }


def _default_llm() -> LlmJsonClient:
    api_key = os.getenv(settings.GEMINI_API_KEY_ENV)
    if not api_key:
        raise PipelineError(
            f"Thiếu {settings.GEMINI_API_KEY_ENV} — cần cho bước sinh bản tin AI. "
            f"Thêm vào .env, hoặc gọi với do_translate=False để chỉ đánh giá hiểm họa."
        )
    return GeminiClient(api_key)


def _to_upsert_record(merged: dict, commune: dict) -> dict:
    """Bổ sung thông tin huyện (từ communes.json) vào bản ghi đã hợp nhất."""
    return {
        "commune_id": merged.get("location_id"),
        "commune_name": merged.get("location"),
        "district_id": commune.get("district_id", merged.get("location_id", "")),
        "district_name": commune.get("district_name", merged.get("location", "")),
        "latitude": merged.get("latitude", 0.0),
        "longitude": merged.get("longitude", 0.0),
        "elevation": merged.get("elevation", 0.0),
        "date": merged["date"],
        "highest_alert_level": merged["highest_alert_level"],
        "weather_summary": merged.get("weather_summary", {}),
        "hazards": merged.get("alerts", []),
        "messages": merged.get("messages", {}),
        "audio": merged.get("audio", {}),
        "has_translation": merged.get("has_translation", bool(merged.get("messages"))),
    }
