import json
from datetime import datetime
from weather_service import fetch_weather_data, downscale_temperature
from rule_engine import evaluate_hazards

def run_main_pipeline():
    print("========================================================================")
    print("   HỆ THỐNG AI DỰ BÁO THỜI TIẾT VI MÔ & CẢNH BÁO THIÊN TAI ĐIỆN BIÊN     ")
    print("========================================================================\n")
    
    # 1. Đọc danh sách địa điểm từ locations.json
    try:
        with open("locations.json", "r", encoding="utf-8") as f:
            locations = json.load(f)
    except Exception as e:
        print(f"❌ Lỗi khi đọc file locations.json: {e}")
        return
        
    all_active_alerts = []
    
    # 2. Chạy luồng xử lý cho từng địa điểm
    for loc in locations:
        print(f"--- ĐANG XỬ LÝ DỮ LIỆU DỰ BÁO: {loc['name'].upper()} ---")
        print(f"Toạ độ: Lat {loc['lat']}, Lon {loc['lon']} | Độ cao thực tế: {loc['real_elevation']}m")
        
        try:
            # Gọi API tải dữ liệu thời tiết
            raw_data = fetch_weather_data(loc["lat"], loc["lon"])
            model_elevation = raw_data.get("elevation", 0)
            print(f"Độ cao lưới của mô hình thời tiết: {model_elevation:.0f}m")
            
            hourly = raw_data.get("hourly", {})
            times = hourly.get("time", [])
            
            # Trích xuất dữ liệu thô
            temps = hourly.get("temperature_2m", [])
            rains = hourly.get("precipitation", [])
            winds = hourly.get("wind_gusts_10m", [])
            wind_speeds = hourly.get("wind_speed_10m", [])
            humidities = hourly.get("relative_humidity_2m", [])
            capes = hourly.get("cape", [])
            evapos = hourly.get("evapotranspiration", [])
            freezings = hourly.get("freezing_level_height", [])
            visibilities = hourly.get("visibility", [])
            pressures = hourly.get("surface_pressure", [])
            soil_temps = hourly.get("soil_temperature_0cm", [])
            soil_moistures_deep = hourly.get("soil_moisture_27_to_81cm", [])
            soil_moistures_shallow = hourly.get("soil_moisture_0_to_1cm", [])
            clouds = hourly.get("cloud_cover", [])
            
            num_hours = len(times)
            num_days = num_hours // 24
            
            print(f"Nhận được dự báo trong {num_days} ngày tới. Tiến hành tính toán và hiệu chỉnh địa hình...\n")
            
            for day_idx in range(num_days):
                start_h = day_idx * 24
                end_h = start_h + 24
                
                # Trích xuất dữ liệu của ngày cụ thể
                day_times = times[start_h:end_h]
                day_temps = temps[start_h:end_h]
                day_rains = rains[start_h:end_h]
                day_winds = winds[start_h:end_h]
                day_wind_speeds = wind_speeds[start_h:end_h]
                day_humidities = humidities[start_h:end_h]
                day_capes = capes[start_h:end_h]
                day_evapos = evapos[start_h:end_h]
                day_freezings = freezings[start_h:end_h]
                day_visibilities = visibilities[start_h:end_h]
                day_pressures = pressures[start_h:end_h]
                day_soil_temps = soil_temps[start_h:end_h]
                day_soil_moistures_deep = soil_moistures_deep[start_h:end_h]
                day_soil_moistures_shallow = soil_moistures_shallow[start_h:end_h]
                day_clouds = clouds[start_h:end_h]
                
                # Chuyển đổi ngày hiển thị
                day_date_str = day_times[0].split("T")[0]
                day_date = datetime.strptime(day_date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                
                # Hiệu chỉnh địa hình cho nhiệt độ
                adjusted_temps = [downscale_temperature(t, loc["real_elevation"], model_elevation) for t in day_temps]
                adjusted_soil_temps = [downscale_temperature(t, loc["real_elevation"], model_elevation) for t in day_soil_temps]
                
                # Loại bỏ giá trị None để tính toán hợp lệ
                valid_temps = [t for t in adjusted_temps if t is not None]
                valid_soil_temps = [t for t in adjusted_soil_temps if t is not None]
                valid_winds = [w for w in day_winds if w is not None]
                valid_wind_speeds = [w for w in day_wind_speeds if w is not None]
                valid_capes = [c for c in day_capes if c is not None]
                valid_evapos = [e for e in day_evapos if e is not None]
                valid_freezings = [f for f in day_freezings if f is not None]
                valid_vis = [v for v in day_visibilities if v is not None]
                valid_humidities = [h for h in day_humidities if h is not None]
                valid_soil_m_deep = [m for m in day_soil_moistures_deep if m is not None]
                valid_soil_m_shall = [m for m in day_soil_moistures_shallow if m is not None]
                valid_clouds = [c for c in day_clouds if c is not None]
                
                # Tính độ giảm áp suất trong 3 giờ lớn nhất
                max_pressure_drop = 0
                for i in range(len(day_pressures) - 3):
                    if day_pressures[i] is not None and day_pressures[i+3] is not None:
                        drop = day_pressures[i] - day_pressures[i+3]
                        if drop > max_pressure_drop:
                            max_pressure_drop = drop
                            
                daily_summary = {
                    "max_temp_adjusted": max(valid_temps) if valid_temps else 25.0,
                    "min_temp_adjusted": min(valid_temps) if valid_temps else 15.0,
                    "min_soil_temp_adjusted": min(valid_soil_temps) if valid_soil_temps else 15.0,
                    "max_precipitation_1h": max([r for r in day_rains if r is not None]) if day_rains else 0.0,
                    "sum_precipitation_24h": sum([r for r in day_rains if r is not None]) if day_rains else 0.0,
                    "max_wind_gust": max(valid_winds) if valid_winds else 10.0,
                    "max_wind_speed": max(valid_wind_speeds) if valid_wind_speeds else 5.0,
                    "max_cape": max(valid_capes) if valid_capes else 0.0,
                    "sum_evapo_24h": sum(valid_evapos) if valid_evapos else 0.5,
                    "min_freezing_height": min(valid_freezings) if valid_freezings else 5000.0,
                    "min_visibility": min(valid_vis) if valid_vis else 10000.0,
                    "max_pressure_drop_3h": max_pressure_drop,
                    "avg_humidity": sum(valid_humidities)/len(valid_humidities) if valid_humidities else 80.0,
                    "min_humidity": min(valid_humidities) if valid_humidities else 60.0,
                    "avg_soil_moisture_27_to_81cm": sum(valid_soil_m_deep)/len(valid_soil_m_deep) if valid_soil_m_deep else 0.3,
                    "avg_soil_moisture_0_to_1cm": sum(valid_soil_m_shall)/len(valid_soil_m_shall) if valid_soil_m_shall else 0.3,
                    "min_cloud": min(valid_clouds) if valid_clouds else 50.0
                }
                
                # Gọi bộ xử lý cảnh báo thiên tai
                day_alerts = evaluate_hazards(daily_summary, loc["landslide_risk_factor"])
                
                # In thông tin bảng điều khiển
                print(f"  > Ngày {day_date} (Nhiệt độ: {daily_summary['min_temp_adjusted']}°C - {daily_summary['max_temp_adjusted']}°C | Mưa: {daily_summary['sum_precipitation_24h']:.1f}mm):")
                if not day_alerts:
                    print("    🟢 Mức độ an toàn: BÌNH THƯỜNG (Không phát hiện thiên tai)")
                else:
                    for hazard_name, color, desc in day_alerts:
                        color_icon = "🔴" if color == "Red" else "🟠" if color == "Orange" else "🟡"
                        print(f"    {color_icon} CẢNH BÁO {color.upper()}: {hazard_name} - {desc}")
                        
                    # Tích hợp Payload để xuất file JSON cảnh báo cho NLP & Frontend
                    all_active_alerts.append({
                        "location": loc["name"],
                        "location_id": loc["id"],
                        "latitude": loc["lat"],
                        "longitude": loc["lon"],
                        "elevation": loc["real_elevation"],
                        "date": day_date,
                        "weather_summary": {
                            "min_temp": daily_summary["min_temp_adjusted"],
                            "max_temp": daily_summary["max_temp_adjusted"],
                            "total_rain": round(daily_summary["sum_precipitation_24h"], 1),
                            "max_rain_1h": round(daily_summary["max_precipitation_1h"], 1),
                            "max_wind_gust": round(daily_summary["max_wind_gust"], 1),
                            "max_cape": round(daily_summary["max_cape"], 1),
                            "min_visibility": round(daily_summary["min_visibility"], 1),
                            "deep_soil_moisture": round(daily_summary["avg_soil_moisture_27_to_81cm"], 2)
                        },
                        "alerts": [
                            {
                                "hazard": alert[0],
                                "level": alert[1],
                                "description": alert[2]
                            } for alert in day_alerts
                        ]
                    })
            print("-" * 72 + "\n")
            
        except Exception as e:
            print(f"❌ Lỗi khi xử lý dữ liệu của {loc['name']}: {e}\n")
            
    # Ghi xuất kết quả JSON
    output_path = "active_alerts.json"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_active_alerts, f, ensure_ascii=False, indent=2)
        print(f"✔ Đã xuất kết quả JSON cảnh báo tại: {output_path}")
    except Exception as e:
        print(f"❌ Lỗi khi ghi file active_alerts.json: {e}")
        
    print("========================================================================")
    print("Hệ thống phân tích hoàn thành.")
    print("========================================================================")

if __name__ == "__main__":
    run_main_pipeline()
