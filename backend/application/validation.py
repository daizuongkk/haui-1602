"""Input and LLM-response validation for the translation pipeline."""
from typing import Optional, Tuple

from backend.shared import alert_levels

ValidationResult = Tuple[bool, Optional[str]]

_REQUIRED_RESPONSE_FIELDS = ("location", "date", "highest_alert_level", "messages")
_REQUIRED_LANGUAGES = {"vi": "tiếng Việt", "thai": "tiếng Thái", "hmong": "tiếng H'Mông"}


def validate_input(forecast_data) -> ValidationResult:
    """Validate the forecast array read from active_alerts.json."""
    if forecast_data is None:
        return False, "Dữ liệu đầu vào là None"
    if not isinstance(forecast_data, list):
        return False, "Dữ liệu đầu vào phải là một mảng JSON"
    if len(forecast_data) == 0:
        return False, "Mảng dữ liệu rỗng, không có bản ghi nào"

    for i, entry in enumerate(forecast_data):
        if not isinstance(entry, dict):
            return False, f"Phần tử [{i}] không phải là object JSON"
        if not entry.get("location"):
            return False, f"Phần tử [{i}] thiếu hoặc rỗng trường 'location'"
        if not entry.get("date"):
            return False, f"Phần tử [{i}] thiếu hoặc rỗng trường 'date'"
        if "alerts" not in entry:
            return False, f"Phần tử [{i}] thiếu trường 'alerts'"
    return True, None


def validate_gemini_response(response_data) -> ValidationResult:
    """Validate the model output has all fields, all three languages and a valid level."""
    if not isinstance(response_data, dict):
        return False, "Phản hồi phải là JSON object, không phải mảng hay giá trị đơn"

    for field in _REQUIRED_RESPONSE_FIELDS:
        if field not in response_data:
            return False, f"Thiếu trường bắt buộc '{field}'"
        if not response_data[field]:
            return False, f"Trường '{field}' rỗng hoặc null"

    messages = response_data.get("messages", {})
    if not isinstance(messages, dict):
        return False, "Trường 'messages' phải là JSON object"

    for lang_key, lang_name in _REQUIRED_LANGUAGES.items():
        if lang_key not in messages:
            return False, f"Thiếu bản dịch {lang_name} (messages.{lang_key})"
        if not str(messages[lang_key]).strip():
            return False, f"Bản dịch {lang_name} (messages.{lang_key}) rỗng"

    if response_data["highest_alert_level"] not in alert_levels.PRIORITY:
        return False, (
            f"Mức cảnh báo '{response_data['highest_alert_level']}' không hợp lệ. "
            f"Phải là: {list(alert_levels.PRIORITY)}"
        )
    return True, None
