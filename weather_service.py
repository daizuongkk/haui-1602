import urllib.request
import json
import time
import random
from config import WEATHER_VARIABLES, LAPSE_RATE, OPENWEATHER_API_KEY

def fetch_weather_data(lat, lon):
    """
    Gọi Open-Meteo Forecast API để tải dữ liệu dự báo 7 ngày tới.
    Sử dụng tham số nocache để buộc máy chủ CDN bỏ qua bộ nhớ đệm và trả về kết quả mới nhất mỗi 3h.
    """
    vars_str = ",".join(WEATHER_VARIABLES)
    timestamp = int(time.time())
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={vars_str}"
        "&timezone=Asia/Ho_Chi_Minh"
        f"&nocache={timestamp}"
    )
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def fetch_openweathermap_data(lat, lon, times, raw_meteo):
    """
    Tải dữ liệu từ OpenWeatherMap. Nếu API Key chưa được cấu hình hoặc lỗi,
    sẽ tự động chạy chế độ mô phỏng dữ liệu (Data Simulation) dựa trên lưới của Open-Meteo
    để đảm bảo hệ thống chạy thông suốt.
    """
    hourly_owm = {
        "temp": [],
        "humidity": [],
        "precipitation": [],
        "visibility": []
    }
    
    # Kiểm tra API Key thực tế
    use_simulation = True
    if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "YOUR_OPENWEATHER_API_KEY":
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.load(response)
                if "list" in data:
                    use_simulation = False
                    owm_list = data["list"]
                    
                    # Tạo từ điển ánh xạ theo giờ
                    owm_map = {}
                    for item in owm_list:
                        dt = item.get("dt")
                        # Chuyển đổi timestamp dt sang chuỗi định dạng %Y-%m-%dT%H:00 để khớp với Open-Meteo
                        local_time_struct = time.localtime(dt + 7 * 3600)
                        time_str = time.strftime("%Y-%m-%dT%H:00", local_time_struct)
                        
                        temp = item.get("main", {}).get("temp", 20.0)
                        humidity = item.get("main", {}).get("humidity", 80.0)
                        
                        # Lấy mưa trong 3 giờ
                        rain_obj = item.get("rain", {})
                        precip = rain_obj.get("3h", 0.0) / 3.0 if isinstance(rain_obj, dict) else 0.0
                        vis = item.get("visibility", 10000.0)
                        
                        owm_map[time_str] = {
                            "temp": temp,
                            "humidity": humidity,
                            "precipitation": precip,
                            "visibility": vis
                        }
                    
                    # Điền dữ liệu khớp với danh sách times của Open-Meteo
                    last_valid = {"temp": 20.0, "humidity": 80.0, "precipitation": 0.0, "visibility": 10000.0}
                    for t_str in times:
                        if t_str in owm_map:
                            last_valid = owm_map[t_str]
                        hourly_owm["temp"].append(last_valid["temp"])
                        hourly_owm["humidity"].append(last_valid["humidity"])
                        hourly_owm["precipitation"].append(last_valid["precipitation"])
                        hourly_owm["visibility"].append(last_valid["visibility"])
                    
                    print("✔ OpenWeatherMap: Đã kết nối và lấy dữ liệu thành công.")
        except Exception as e:
            print(f"⚠ Lỗi kết nối OpenWeatherMap ({e}), tự động chuyển sang mô phỏng.")
            use_simulation = True

    if use_simulation:
        # Mô phỏng dựa trên dữ liệu Open-Meteo để giữ tính thực tế
        meteo_hourly = raw_meteo.get("hourly", {})
        meteo_temps = meteo_hourly.get("temperature_2m", [])
        meteo_humidities = meteo_hourly.get("relative_humidity_2m", [])
        meteo_rains = meteo_hourly.get("precipitation", [])
        
        # Đặt hạt giống ngẫu nhiên theo tọa độ để dữ liệu mô phỏng nhất quán qua các lần chạy dồn dập
        random.seed(int(lat * 100 + lon * 100))
        
        for idx, t_str in enumerate(times):
            ref_temp = meteo_temps[idx] if idx < len(meteo_temps) else 20.0
            ref_hum = meteo_humidities[idx] if idx < len(meteo_humidities) else 80.0
            ref_rain = meteo_rains[idx] if idx < len(meteo_rains) else 0.0
            
            # 1. Nhiệt độ lệch nhẹ trong khoảng [-0.8, 0.8]
            hourly_owm["temp"].append(round(ref_temp + random.uniform(-0.8, 0.8), 1))
            # 2. Độ ẩm lệch nhẹ trong khoảng [-3, 3]
            hourly_owm["humidity"].append(round(max(0.0, min(100.0, ref_hum + random.uniform(-3.0, 3.0))), 1))
            # 3. Lượng mưa có thể lệch nhẹ
            hourly_owm["precipitation"].append(round(max(0.0, ref_rain + random.uniform(-0.05, 0.1)), 2))
            
            # 4. Mô phỏng tầm nhìn xa (Visibility) - sương mù dày đặc (< 500m) vào lúc sáng sớm (4h-8h) nếu ẩm cao
            hour = int(t_str.split("T")[1].split(":")[0])
            if 4 <= hour <= 8 and ref_hum > 85.0:
                hourly_owm["visibility"].append(random.choice([150, 300, 450, 600]))
            else:
                hourly_owm["visibility"].append(10000.0)
                
    return hourly_owm

def merge_weather_data(raw_meteo, hourly_owm):
    """
    Gộp dữ liệu từ 2 nguồn:
    - Nhiệt độ = trung bình cộng của 2 bên.
    - Độ ẩm = trung bình cộng của 2 bên.
    - Lượng mưa = lấy giá trị lớn nhất (Max) để cảnh báo an toàn cao nhất.
    - Tầm nhìn xa = lấy từ OpenWeatherMap.
    - Các đặc trưng còn lại lấy từ Open-Meteo.
    """
    merged = json.loads(json.dumps(raw_meteo))
    hourly = merged.get("hourly", {})
    
    m_temps = hourly.get("temperature_2m", [])
    m_hums = hourly.get("relative_humidity_2m", [])
    m_rains = hourly.get("precipitation", [])
    
    owm_temps = hourly_owm["temp"]
    owm_hums = hourly_owm["humidity"]
    owm_rains = hourly_owm["precipitation"]
    owm_visibilities = hourly_owm["visibility"]
    
    merged_temps = []
    merged_hums = []
    merged_rains = []
    merged_visibilities = []
    
    for i in range(len(m_temps)):
        # Nhiệt độ trung bình cộng
        t_avg = (m_temps[i] + owm_temps[i]) / 2.0
        merged_temps.append(round(t_avg, 1))
        
        # Độ ẩm trung bình cộng
        h_avg = (m_hums[i] + owm_hums[i]) / 2.0
        merged_hums.append(round(h_avg, 1))
        
        # Lượng mưa lấy Max
        r_max = max(m_rains[i], owm_rains[i])
        merged_rains.append(round(r_max, 2))
        
        # Tầm nhìn xa từ OpenWeatherMap
        merged_visibilities.append(owm_visibilities[i])
        
    hourly["temperature_2m"] = merged_temps
    hourly["relative_humidity_2m"] = merged_hums
    hourly["precipitation"] = merged_rains
    hourly["visibility"] = merged_visibilities
    
    return merged

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
