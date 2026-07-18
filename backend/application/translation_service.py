"""
Translation use case: generate a multilingual bulletin for one forecast record.

Owns the retry/parse/validate policy; the LLM client (a port) only performs the
raw generation call, so the loop can be tested against a fake client.
"""
import json
import time
from typing import Optional

from backend.application.prompts import SYSTEM_PROMPT, build_user_prompt
from backend.application.validation import validate_gemini_response
from backend.config import settings
from backend.infrastructure.logging_config import get_logger
from backend.infrastructure.ports import LlmJsonClient


class TranslationService:
    def __init__(self, llm: LlmJsonClient, logger=None) -> None:
        self._llm = llm
        self._log = logger or get_logger()

    def translate(self, forecast_entry: dict) -> Optional[dict]:
        """Return the validated bulletin dict, or None after exhausting retries."""
        user_prompt = build_user_prompt(forecast_entry)
        attempts = settings.GEMINI_MAX_RETRIES + 1

        for attempt in range(attempts):
            self._log.info("  Gọi %s (lần %d/%d)...", settings.GEMINI_MODEL, attempt + 1, attempts)
            try:
                text = self._llm.generate(SYSTEM_PROMPT, user_prompt)
                if not text.strip():
                    self._log.warning("  Phản hồi rỗng (lần %d)", attempt + 1)
                    continue

                result = json.loads(text)
                is_valid, error = validate_gemini_response(result)
                if not is_valid:
                    self._log.warning("  Response validation thất bại: %s (lần %d)", error, attempt + 1)
                    continue

                self._log.info("  Thành công.")
                return result

            except json.JSONDecodeError as exc:
                self._log.warning("  Lỗi parse JSON: %s (lần %d)", exc, attempt + 1)
            except Exception as exc:  # noqa: BLE001 - surfaced via log, retried
                self._log.error("  Lỗi gọi LLM: %s: %s (lần %d)", type(exc).__name__, exc, attempt + 1)

            if attempt < settings.GEMINI_MAX_RETRIES:
                time.sleep(settings.GEMINI_RETRY_DELAY_SECONDS)

        self._log.error("  Đã thử %d lần. Đánh dấu FAILED.", attempts)
        return None
