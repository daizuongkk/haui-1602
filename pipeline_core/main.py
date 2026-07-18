import json
import sqlite3
import os
import sys
from datetime import datetime

# Đảm bảo import được các module cùng thư mục
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import WEATHER_VARIABLES
from weather_service import (
    fetch_weather_data,
    fetch_openweathermap_data,
    merge_weather_data,
    downscale_temperature
)
from rule_engine import evaluate_hazards, evaluate_hourly_hazard_level

# Kết nối đường dẫn trực tiếp với thư mục data/ của dự án lớn
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "voai_database.db"))
PENDING_ALERTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "pending_alerts.json"))

def init_db():
    """ Khởi tạo cơ sở dữ liệu SQLite đóng vai trò lớp lưu trữ (DB) """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Bảng lưu trữ thời tiết vi khí hậu thô đã gộp
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_forecast (
            location_id TEXT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            precipitation REAL,
            visibility REAL,
            soil_temp_0cm REAL,
            soil_temp_6cm REAL,
            soil_temp_18cm REAL,
            soil_temp_54cm REAL,
            soil_moist_0_to_1cm REAL,
            soil_moist_27_to_81cm REAL,
            cape REAL,
            evapotranspiration REAL,
            freezing_height REAL,
            pressure REAL,
            wind_speed REAL,
            wind_gust REAL,
            cloud_cover REAL,
            PRIMARY KEY (location_id, timestamp)
        )
    """)
    conn.commit()
    conn.close()

def save_forecast_to_db(location_id, merged_data):
    """ Lưu trữ dữ liệu thời tiết đã gộp (ETL) vào DB """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    hourly = merged_data.get("hourly", {})
    times = hourly.get("time", [])
    
    for idx, time_str in enumerate(times):
        cursor.execute("""
            INSERT OR REPLACE INTO weather_forecast (
                location_id, timestamp, temperature, humidity, precipitation, visibility,
                soil_temp_0cm, soil_temp_6cm, soil_temp_18cm, soil_temp_54cm,
                soil_moist_0_to_1cm, soil_moist_27_to_81cm, cape, evapotranspiration,
                freezing_height, pressure, wind_speed, wind_gust, cloud_cover
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            location_id,
            time_str,
            hourly.get("temperature_2m", [])[idx] if idx < len(hourly.get("temperature_2m", [])) else 20.0,
            hourly.get("relative_humidity_2m", [])[idx] if idx < len(hourly.get("relative_humidity_2m", [])) else 80.0,
            hourly.get("precipitation", [])[idx] if idx < len(hourly.get("precipitation", [])) else 0.0,
            hourly.get("visibility", [])[idx] if idx < len(hourly.get("visibility", [])) else 10000.0,
            hourly.get("soil_temperature_0cm", [])[idx] if idx < len(hourly.get("soil_temperature_0cm", [])) else 20.0,
            hourly.get("soil_temperature_6cm", [])[idx] if idx < len(hourly.get("soil_temperature_6cm", [])) else 20.0,
            hourly.get("soil_temperature_18cm", [])[idx] if idx < len(hourly.get("soil_temperature_18cm", [])) else 20.0,
            hourly.get("soil_temperature_54cm", [])[idx] if idx < len(hourly.get("soil_temperature_54cm", [])) else 20.0,
            hourly.get("soil_moisture_0_to_1cm", [])[idx] if idx < len(hourly.get("soil_moisture_0_to_1cm", [])) else 0.3,
            hourly.get("soil_moisture_27_to_81cm", [])[idx] if idx < len(hourly.get("soil_moisture_27_to_81cm", [])) else 0.3,
            hourly.get("cape", [])[idx] if idx < len(hourly.get("cape", [])) else 0.0,
            hourly.get("evapotranspiration", [])[idx] if idx < len(hourly.get("evapotranspiration", [])) else 0.1,
            hourly.get("freezing_level_height", [])[idx] if idx < len(hourly.get("freezing_level_height", [])) else 5000.0,
            hourly.get("surface_pressure", [])[idx] if idx < len(hourly.get("surface_pressure", [])) else 1013.0,
            hourly.get("wind_speed_10m", [])[idx] if idx < len(hourly.get("wind_speed_10m", [])) else 5.0,
            hourly.get("wind_gusts_10m", [])[idx] if idx < len(hourly.get("wind_gusts_10m", [])) else 10.0,
            hourly.get("cloud_cover", [])[idx] if idx < len(hourly.get("cloud_cover", [])) else 50.0
        ))
        
    conn.commit()
    conn.close()

def load_daily_summary_from_db(location_id, date_str):
    """ Đọc từ DB và tính toán các tổng hợp/đặc trưng cho ngày cụ thể """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Lọc các dòng dự báo thuộc ngày cần phân tích (định dạng YYYY-MM-DD)
    cursor.execute("""
        SELECT * FROM weather_forecast 
        WHERE location_id = ? AND timestamp LIKE ?
    """, (location_id, f"{date_str}%"))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return None
        
    temps = [r["temperature"] for r in rows]
    soil_temps = [r["soil_temp_0cm"] for r in rows]
    rains = [r["precipitation"] for r in rows]
    visibilities = [r["visibility"] for r in rows]
    capes = [r["cape"] for r in rows]
    wind_gusts = [r["wind_gust"] for r in rows]
    freezing_heights = [r["freezing_height"] for r in rows]
    humidities = [r["humidity"] for r in rows]
    clouds = [r["cloud_cover"] for r in rows]
    soil_moist_shallow = [r["soil_moist_0_to_1cm"] for r in rows]
    soil_moist_deep = [r["soil_moist_27_to_81cm"] for r in rows]
    evapos = [r["evapotranspiration"] for r in rows]
    pressures = [r["pressure"] for r in rows]
    wind_speeds = [r["wind_speed"] for r in rows]
    
    # Tính biến thiên áp suất lớn nhất trong 3 giờ liên tiếp
    max_press_drop_3h = 0.0
    for idx in range(len(pressures) - 3):
        drop = pressures[idx] - pressures[idx + 3]
        if drop > max_press_drop_3h:
            max_press_drop_3h = drop

    return {
        "min_temp_raw": min(temps),
        "max_temp_raw": max(temps),
        "min_soil_temp_raw": min(soil_temps),
        "sum_precipitation_24h": sum(rains),
        "max_precipitation_1h": max(rains),
        "min_visibility": min(visibilities),
        "max_cape": max(capes),
        "max_wind_gust": max(wind_gusts),
        "min_freezing_height": min(freezing_heights),
        "min_humidity": min(humidities),
        "avg_humidity": sum(humidities) / len(humidities),
        "min_cloud": min(clouds),
        "avg_soil_moisture_0_to_1cm": sum(soil_moist_shallow) / len(soil_moist_shallow),
        "avg_soil_moisture_27_to_81cm": sum(soil_moist_deep) / len(soil_moist_deep),
        "sum_evapo_24h": sum(evapos),
        "max_pressure_drop_3h": max_press_drop_3h,
        "max_wind_speed": max(wind_speeds)
    }

def main():
    print("=== VOAI WEATHER WARNING PIPELINE START ===")
    init_db()
    
    # Đọc danh sách địa điểm hành chính
    locations_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locations.json")
    with open(locations_file, "r", encoding="utf-8") as f:
        locations = json.load(f)
        
    pending_alerts = []
    
    for loc in locations:
        loc_id = loc["id"]
        loc_name = loc["name"]
        lat = loc["lat"]
        lon = loc["lon"]
        real_elevation = loc["real_elevation"]
        landslide_factor = loc["landslide_risk_factor"]
        
        print(f"\n🔍 Đang xử lý: {loc_name} (Tọa độ: {lat}, {lon})")
        
        try:
            # 1. Gọi Open-Meteo lấy dữ liệu thô
            raw_meteo = fetch_weather_data(lat, lon)
            hourly = raw_meteo.get("hourly", {})
            times = hourly.get("time", [])
            model_elevation = raw_meteo.get("elevation", 0)
            
            # 2. Gọi OpenWeatherMap để đồng bộ
            hourly_owm = fetch_openweathermap_data(lat, lon, times, raw_meteo)
            
            # 3. Gộp dữ liệu (Data Fusion & Geo-Mapping)
            merged_data = merge_weather_data(raw_meteo, hourly_owm)
            
            # 4. Ghi nhận dữ liệu đã trộn vào DB
            save_forecast_to_db(loc_id, merged_data)
            print(f"   ✔ Đã lưu dữ liệu dự báo đã gộp vào Database (DB).")
            
            # 5. Đọc ngược dữ liệu từ DB cho tất cả các ngày dự báo (7 ngày)
            unique_dates = sorted(list(set(t.split("T")[0] for t in times)))
            print(f"   📊 Tiến hành phân tích chuỗi dự báo {len(unique_dates)} ngày...")
            
            for date_str in unique_dates:
                summary = load_daily_summary_from_db(loc_id, date_str)
                if not summary:
                    continue
                    
                # 6. Chạy Statistical Downscaling (Hiệu chỉnh nhiệt độ theo cao độ thực địa)
                summary["min_temp_adjusted"] = downscale_temperature(summary["min_temp_raw"], real_elevation, model_elevation)
                summary["max_temp_adjusted"] = downscale_temperature(summary["max_temp_raw"], real_elevation, model_elevation)
                summary["min_soil_temp_adjusted"] = downscale_temperature(summary["min_soil_temp_raw"], real_elevation, model_elevation)
                
                # 7. Tính điểm rủi ro và chia Rule
                detected_alerts = evaluate_hazards(summary, landslide_factor)
                
                # Tạo bản tin ghi nhận chờ phê duyệt
                alert_items = []
                for hazard_name, color_level, desc in detected_alerts:
                    alert_items.append({
                        "hazard": hazard_name,
                        "level": color_level,
                        "description": desc
                    })
                    
                loc_alert = {
                    "location": loc_name,
                    "location_id": loc_id,
                    "latitude": lat,
                    "longitude": lon,
                    "elevation": real_elevation,
                    "date": date_str,
                    "expert_status": "Pending",
                    "weather_summary": {
                        "min_temp": summary["min_temp_adjusted"],
                        "max_temp": summary["max_temp_adjusted"],
                        "total_rain": round(summary["sum_precipitation_24h"], 1),
                        "max_rain_1h": round(summary["max_precipitation_1h"], 1),
                        "max_wind_gust": round(summary["max_wind_gust"], 1),
                        "max_cape": round(summary["max_cape"], 1),
                        "min_visibility": round(summary["min_visibility"], 0),
                        "deep_soil_moisture": round(summary["avg_soil_moisture_27_to_81cm"], 2)
                    },
                    "alerts": alert_items
                }
                
                pending_alerts.append(loc_alert)
                
            print(f"   ✔ Đã hoàn tất phân tích chuỗi 7 ngày cho {loc_name}.")
                
        except Exception as e:
            print(f"   ❌ Lỗi xử lý tại {loc_name}: {e}")
            
    # Ghi đè vào tệp danh sách chờ duyệt
    with open(PENDING_ALERTS_PATH, "w", encoding="utf-8") as f:
        json.dump(pending_alerts, f, indent=2, ensure_ascii=False)
        
    print(f"\n✔ Đã xuất tệp cảnh báo chờ chuyên gia duyệt ra: {PENDING_ALERTS_PATH}")
    print("=== VOAI WEATHER WARNING PIPELINE FINISHED ===")

if __name__ == "__main__":
    main()
