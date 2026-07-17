"""
TRANSLATOR — Module chinh goi Gemini 2.5 Flash de dich ban tin canh bao.
Buoc 4: Goi Gemini
Buoc 5: Response Validation (tich hop trong retry loop)
Retry Policy: Toi da 2 lan retry khi timeout, JSON loi, thieu field, sai schema.
"""
import json
import time
from google import genai
from agent.prompt import SYSTEM_PROMPT, build_user_prompt
from agent.validator import validate_gemini_response
from agent.logger import setup_logger

logger = setup_logger()

# Cau hinh Gemini
GEMINI_MODEL = "gemini-3.1-flash-lite"
GEMINI_TEMPERATURE = 0.2
MAX_RETRIES = 2  # Retry toi da 2 lan (tong cong 3 lan thu)
RETRY_DELAY = 3  # Delay giua cac lan retry (giay)


def translate_forecast(forecast_entry, api_key):
    """
    Gọi Gemini 2.5 Pro để sinh bản tin cảnh báo đa ngôn ngữ.
    
    Quy trình:
    1. Xây dựng prompt từ dữ liệu dự báo
    2. Gọi Gemini API với temperature=0.2, response_mime_type=application/json
    3. Parse và validate response
    4. Retry tối đa 2 lần nếu lỗi
    
    Args:
        forecast_entry: dict — Một bản ghi dự báo từ active_alerts.json
        api_key: str — GEMINI_API_KEY
        
    Returns:
        tuple: (result_dict | None, metadata_dict)
            - result_dict: JSON kết quả dịch nếu thành công, None nếu thất bại
            - metadata_dict: Thông tin về lần gọi API (tokens, latency, status...)
    """
    client = genai.Client(api_key=api_key)
    user_prompt = build_user_prompt(forecast_entry)

    metadata = {
        "model": GEMINI_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
        "input_tokens": None,
        "output_tokens": None,
        "latency_ms": None,
        "status": "FAILED",
        "response_json": None
    }

    for attempt in range(MAX_RETRIES + 1):
        attempt_num = attempt + 1
        logger.info(f"  🔄 Gọi {GEMINI_MODEL} (lần {attempt_num}/{MAX_RETRIES + 1})...")

        start_time = time.time()

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_prompt}]}
                ],
                config=genai.types.GenerateContentConfig(
                    temperature=GEMINI_TEMPERATURE,
                    response_mime_type="application/json",
                )
            )

            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            metadata["latency_ms"] = latency_ms

            # Lấy thông tin token usage
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                metadata["input_tokens"] = getattr(response.usage_metadata, 'prompt_token_count', None)
                metadata["output_tokens"] = getattr(response.usage_metadata, 'candidates_token_count', None)

            # Lấy text phản hồi
            response_text = response.text
            if not response_text or not response_text.strip():
                logger.warning(f"  ⚠ Gemini trả về phản hồi rỗng (lần {attempt_num})")
                continue

            metadata["response_json"] = response_text

            # Parse JSON
            result = json.loads(response_text)

            # Bước 5: Response Validation
            is_valid, error = validate_gemini_response(result)
            if not is_valid:
                logger.warning(f"  ⚠ Response validation thất bại: {error} (lần {attempt_num})")
                continue

            # Thành công!
            metadata["status"] = "SUCCESS"
            logger.info(
                f"  ✅ Thành công! ({latency_ms}ms | "
                f"Input: {metadata.get('input_tokens', '?')} tokens | "
                f"Output: {metadata.get('output_tokens', '?')} tokens)"
            )

            return result, metadata

        except json.JSONDecodeError as e:
            end_time = time.time()
            metadata["latency_ms"] = int((end_time - start_time) * 1000)
            logger.warning(f"  ⚠ Lỗi parse JSON từ Gemini: {e} (lần {attempt_num})")
            # Gemini có thể trả Markdown thay vì JSON thuần
            try:
                metadata["response_json"] = response.text
            except Exception:
                pass
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            continue

        except Exception as e:
            end_time = time.time()
            metadata["latency_ms"] = int((end_time - start_time) * 1000)
            logger.error(f"  Loi khi goi Gemini API: {type(e).__name__}: {e} (lan {attempt_num})")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            continue

    # Đã hết retry
    logger.error(f"  ❌ Đã thử {MAX_RETRIES + 1} lần. Đánh dấu FAILED.")
    return None, metadata
