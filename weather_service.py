import urllib.request
import json
from config import WEATHER_VARIABLES, LAPSE_RATE

def fetch_weather_data(lat, lon):
    """
    Gọi Open-Meteo Forecast API để tải dữ liệu dự báo 7 ngày tới.
    Trả về: Đối tượng JSON phản hồi từ API.
    """
    vars_str = ",".join(WEATHER_VARIABLES)
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={vars_str}"
        "&timezone=Asia/Ho_Chi_Minh"
    )
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def downscale_temperature(temp_model, real_el, model_el):
    """
    Hiệu chỉnh nhiệt độ mô hình lưới thô về độ cao thực tế của xã/bản.
    Áp dụng công thức suy giảm nhiệt độ khí quyển theo độ cao (lapse rate).
    """
    if temp_model is None:
        return None
    el_diff = real_el - model_el
    temp_adjusted = temp_model - (LAPSE_RATE * el_diff)
    return round(temp_adjusted, 1)
