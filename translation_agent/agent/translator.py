import json
import time
import logging
from typing import Tuple, Dict, Any, Optional

from google import genai
from agent.prompt import SYSTEM_PROMPT, build_user_prompt
from agent.validator import validate_gemini_response
from agent.logger import setup_logger

logger = setup_logger()

GEMINI_MODEL = "gemini-3.1-flash-lite"
GEMINI_TEMPERATURE = 0.2
MAX_RETRIES = 2
RETRY_DELAY = 3


def translate_forecast(forecast_entry: Dict[str, Any], api_key: str) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """
    Translates weather forecast alerts using Google's Gemini API.
    
    Args:
        forecast_entry: A dictionary containing location, date, and alert details.
        api_key: The API key for Google Gemini.
        
    Returns:
        A tuple containing the parsed JSON response (or None on failure) and a metadata dictionary.
    """
    client = genai.Client(api_key=api_key)
    user_prompt = build_user_prompt(forecast_entry)

    metadata: Dict[str, Any] = {
        "model": GEMINI_MODEL,
        "input_tokens": None,
        "output_tokens": None,
        "latency_ms": None,
        "status": "FAILED"
    }

    for attempt in range(MAX_RETRIES + 1):
        logger.info("Calling %s API (Attempt %d/%d)", GEMINI_MODEL, attempt + 1, MAX_RETRIES + 1)
        start_time = time.time()

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    {"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\n{user_prompt}"}]}
                ],
                config=genai.types.GenerateContentConfig(
                    temperature=GEMINI_TEMPERATURE,
                    response_mime_type="application/json",
                )
            )

            latency_ms = int((time.time() - start_time) * 1000)
            metadata["latency_ms"] = latency_ms

            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                metadata["input_tokens"] = getattr(response.usage_metadata, 'prompt_token_count', None)
                metadata["output_tokens"] = getattr(response.usage_metadata, 'candidates_token_count', None)

            response_text = response.text
            if not response_text or not response_text.strip():
                logger.warning("Empty response received from API.")
                continue

            result = json.loads(response_text)

            is_valid, error = validate_gemini_response(result)
            if not is_valid:
                logger.warning("Response validation failed: %s", error)
                continue

            metadata["status"] = "SUCCESS"
            logger.info("Translation successful (%dms, Input: %s tokens, Output: %s tokens)", 
                        latency_ms, metadata.get("input_tokens", "?"), metadata.get("output_tokens", "?"))

            return result, metadata

        except json.JSONDecodeError as e:
            logger.warning("JSON decode error: %s", e)
        except Exception as e:
            logger.error("API call failed: %s: %s", type(e).__name__, e)

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    logger.error("Maximum retries reached. Translation failed.")
    return None, metadata
