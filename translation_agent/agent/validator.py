"""
VALIDATOR — Kiểm tra tính hợp lệ dữ liệu đầu vào và phản hồi Gemini.
Bước 1: Input Validation
Bước 5: Response Validation
"""


def validate_input(forecast_data):
    """
    Bước 1 — Input Validation.
    
    Kiểm tra:
    - JSON hợp lệ (đã được parse trước khi gọi hàm này)
    - Có location
    - Có date
    - Có alerts
    - Không null
    
    Returns: (is_valid: bool, error_message: str | None)
    """
    if forecast_data is None:
        return False, "Dữ liệu đầu vào là None"

    if not isinstance(forecast_data, list):
        return False, "Dữ liệu đầu vào phải là một mảng JSON"

    if len(forecast_data) == 0:
        return False, "Mảng dữ liệu rỗng, không có bản ghi nào"

    for i, entry in enumerate(forecast_data):
        if not isinstance(entry, dict):
            return False, f"Phần tử [{i}] không phải là object JSON"

        if "location" not in entry or not entry["location"]:
            return False, f"Phần tử [{i}] thiếu hoặc rỗng trường 'location'"

        if "date" not in entry or not entry["date"]:
            return False, f"Phần tử [{i}] thiếu hoặc rỗng trường 'date'"

        if "alerts" not in entry:
            return False, f"Phần tử [{i}] thiếu trường 'alerts'"

    return True, None


def validate_gemini_response(response_data):
    """
    Bước 5 — Response Validation.
    
    Kiểm tra:
    - Parse JSON thành công (đã parse trước khi gọi)
    - Có đủ field: location, date, highest_alert_level, messages
    - Có messages.vi
    - Có messages.thai
    - Có messages.hmong
    
    Returns: (is_valid: bool, error_message: str | None)
    """
    if response_data is None:
        return False, "Phản hồi từ Gemini là None"

    if not isinstance(response_data, dict):
        return False, "Phản hồi phải là JSON object, không phải mảng hay giá trị đơn"

    # Kiểm tra các trường bắt buộc ở root level
    required_fields = ["location", "date", "highest_alert_level", "messages"]
    for field in required_fields:
        if field not in response_data:
            return False, f"Thiếu trường bắt buộc '{field}'"
        if not response_data[field]:
            return False, f"Trường '{field}' rỗng hoặc null"

    # Kiểm tra messages object
    messages = response_data.get("messages", {})
    if not isinstance(messages, dict):
        return False, "Trường 'messages' phải là JSON object"

    # Kiểm tra 3 ngôn ngữ bắt buộc
    required_langs = {
        "vi": "tiếng Việt",
        "thai": "tiếng Thái",
        "hmong": "tiếng H'Mông"
    }
    for lang_key, lang_name in required_langs.items():
        if lang_key not in messages:
            return False, f"Thiếu bản dịch {lang_name} (messages.{lang_key})"
        if not messages[lang_key] or not str(messages[lang_key]).strip():
            return False, f"Bản dịch {lang_name} (messages.{lang_key}) rỗng"

    # Kiểm tra highest_alert_level hợp lệ
    valid_levels = ["Red", "Orange", "Yellow", "Green"]
    if response_data["highest_alert_level"] not in valid_levels:
        return False, f"Mức cảnh báo '{response_data['highest_alert_level']}' không hợp lệ. Phải là: {valid_levels}"

    return True, None
