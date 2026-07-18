import math
from config import THRESHOLDS

def normalize_to_100(raw_score, t_yellow, t_orange, t_red):
    """
    Chuẩn hóa điểm số thô phi tuyến về thang [0, 100] sao cho:
    - raw_score <= 0 -> 0.0
    - raw_score = t_yellow -> 35.0
    - raw_score = t_orange -> 65.0
    - raw_score = t_red -> 85.0
    - raw_score > t_red -> tiệm cận 100
    """
    if raw_score <= 0:
        return 0.0
        
    if raw_score < t_yellow:
        val = (raw_score / t_yellow) * 35.0
    elif raw_score < t_orange:
        val = 35.0 + (raw_score - t_yellow) / (t_orange - t_yellow) * (65.0 - 35.0)
    elif raw_score < t_red:
        val = 65.0 + (raw_score - t_orange) / (t_red - t_orange) * (85.0 - 65.0)
    else:
        k = 1.5 / t_red if t_red > 0 else 0.01
        normalized = 85.0 + 15.0 * (1.0 - math.exp(-k * (raw_score - t_red)))
        val = min(100.0, normalized)
        
    return round(val, 1)

def evaluate_hazards(daily_data, landslide_risk_factor):
    """
    Tính điểm rủi ro cho từng loại thiên tai (Scoring Formulas) đã chuẩn hóa về [0, 100]
    và Phân chia Rule theo thang chuẩn hóa:
    - Điểm >= 85.0 -> Red
    - Điểm >= 65.0 -> Orange
    - Điểm >= 35.0 -> Yellow
    - Điểm < 35.0 -> Green (không cảnh báo)
    """
    alerts = []
    
    # 1. CÔNG THỨC MƯA LỚN & NGẬP ÚNG CỤC BỘ
    max_rain_1h = daily_data.get("max_precipitation_1h", 0.0)
    sum_rain_24h = daily_data.get("sum_precipitation_24h", 0.0)
    avg_soil_moist_shallow = daily_data.get("avg_soil_moisture_0_to_1cm", 0.3)
    
    raw_flood = (max_rain_1h * 3.0 + sum_rain_24h * 0.5) * (1.0 + avg_soil_moist_shallow)
    flood_score = normalize_to_100(raw_flood, THRESHOLDS["flood_yellow"], THRESHOLDS["flood_orange"], THRESHOLDS["flood_red"])
    
    if flood_score >= 85.0:
        alerts.append((
            "Mưa lớn & Ngập úng", 
            "Red", 
            f"Nguy cơ ngập úng cục bộ cực cao (Điểm: {flood_score}). Lượng mưa cường độ mạnh dồn dập, đất mặt bão hòa nước."
        ))
    elif flood_score >= 65.0:
        alerts.append((
            "Mưa lớn & Ngập úng", 
            "Orange", 
            f"Mưa to gây nguy cơ ngập lụt vùng trũng thấp (Điểm: {flood_score})."
        ))
    elif flood_score >= 35.0:
        alerts.append((
            "Mưa lớn & Ngập úng", 
            "Yellow", 
            f"Chú ý mưa lớn tích lũy diện rộng gây trơn trượt (Điểm: {flood_score})."
        ))

    # 2. CÔNG THỨC LŨ QUẾT & SẠT LỞ ĐẤT
    avg_soil_moist_deep = daily_data.get("avg_soil_moisture_27_to_81cm", 0.3)
    sum_evapo_24h = daily_data.get("sum_evapo_24h", 0.5)
    water_balance = sum_rain_24h - sum_evapo_24h
    
    raw_landslide = (sum_rain_24h * 0.5 + avg_soil_moist_deep * 150 + water_balance * 0.3) * landslide_risk_factor
    landslide_score = normalize_to_100(raw_landslide, THRESHOLDS["landslide_yellow"], THRESHOLDS["landslide_orange"], THRESHOLDS["landslide_red"])
    
    if landslide_score >= 85.0 and sum_rain_24h >= 50:
        alerts.append((
            "Lũ quét & Sạt lở", 
            "Red", 
            f"Nền đất sườn núi cực kỳ mất ổn định (Điểm: {landslide_score}). Đất ngậm nước bão hòa sâu, nguy cơ sạt lở núi và lũ bùn đá cực kỳ khẩn cấp!"
        ))
    elif landslide_score >= 65.0 and sum_rain_24h >= 30:
        alerts.append((
            "Lũ quét & Sạt lở", 
            "Orange", 
            f"Đất đồi dốc ngậm nhiều nước, liên kết yếu (Điểm: {landslide_score}). Đề phòng sạt trượt đất taluy đường sườn núi."
        ))
    elif landslide_score >= 35.0:
        alerts.append((
            "Lũ quét & Sạt lở", 
            "Yellow", 
            f"Đất ẩm ướt nhão (Điểm: {landslide_score}). Đề phòng sạt lở cục bộ ở các vị trí dốc đứng khi mưa tiếp tục kéo dài."
        ))

    # 3. CÔNG THỨC DÔNG, LỐC, SÉT
    max_cape = daily_data.get("max_cape", 0.0)
    max_wind_gust = daily_data.get("max_wind_gust", 10.0)
    press_change_3h = daily_data.get("max_pressure_drop_3h", 0.0)
    
    raw_thunderstorm = (max_cape * 0.02 + max_wind_gust * 0.8 + press_change_3h * 15.0)
    thunderstorm_score = normalize_to_100(raw_thunderstorm, THRESHOLDS["thunderstorm_yellow"], THRESHOLDS["thunderstorm_orange"], THRESHOLDS["thunderstorm_red"])
    
    if thunderstorm_score >= 85.0:
        alerts.append((
            "Dông, lốc, sét", 
            "Red", 
            f"Khí quyển cực kỳ bất ổn định đối lưu mạnh (Điểm: {thunderstorm_score}). Nguy cơ cực cao xảy ra sét đánh dữ dội và gió lốc phá hoại mái nhà."
        ))
    elif thunderstorm_score >= 65.0:
        alerts.append((
            "Dông, lốc, sét", 
            "Orange", 
            f"Mây đối lưu dông phát triển mạnh kèm gió giật lớn (Điểm: {thunderstorm_score}). Đề phòng dông lốc mạnh đột ngột."
        ))
    elif thunderstorm_score >= 35.0:
        alerts.append((
            "Dông, lốc, sét", 
            "Yellow", 
            f"Chú ý mưa dông kèm sấm sét cục bộ vào chiều tối (Điểm: {thunderstorm_score})."
        ))

    # 4. CÔNG THỨC MƯA ĐÁ
    min_freezing_height = daily_data.get("min_freezing_height", 5000.0)
    raw_hail = (max_cape * 0.015 + max(0, 5000 - min_freezing_height) * 0.03 + max_rain_1h * 2.0)
    hail_score = normalize_to_100(raw_hail, THRESHOLDS["hail_yellow"], THRESHOLDS["hail_orange"], THRESHOLDS["hail_red"])
    
    if max_cape >= 1200 and min_freezing_height <= 4200:
        if hail_score >= 85.0:
            alerts.append((
                "Mưa đá", 
                "Red", 
                f"Nguy cơ rất cao xảy ra mưa đá rơi diện rộng (Điểm: {hail_score}). Mực đông lạnh thấp ({min_freezing_height:.0f}m) kèm đối lưu cực mạnh."
            ))
        elif hail_score >= 65.0:
            alerts.append((
                "Mưa đá", 
                "Orange", 
                f"Đề phòng mưa đá cục bộ trong các cơn dông mạnh (Điểm: {hail_score}, Mực 0°C: {min_freezing_height:.0f}m)."
            ))
        elif hail_score >= 35.0:
            alerts.append((
                "Mưa đá", 
                "Yellow", 
                f"Theo dõi khả năng xuất hiện mưa đá hạt nhỏ cục bộ (Điểm: {hail_score})."
            ))

    # 5. CÔNG THỨC RÉT ĐẬM, RÉT HẠI & SƯƠNG MUỐI
    min_temp = daily_data.get("min_temp_adjusted", 15.0)
    min_soil_temp = daily_data.get("min_soil_temp_adjusted", 15.0)
    min_cloud = daily_data.get("min_cloud", 50.0)
    avg_humidity = daily_data.get("avg_humidity", 80.0)
    
    raw_cold = max(0, 20 - min_temp) * 4.0 + max(0, 10 - min_soil_temp) * 2.0
    cold_score = normalize_to_100(raw_cold, THRESHOLDS["cold_yellow"], THRESHOLDS["cold_orange"], THRESHOLDS["cold_red"])
    
    # Đánh giá nguy cơ sương muối
    is_frost_possible = (min_temp < 5.0 or min_soil_temp <= 1.0) and min_cloud < 20.0 and avg_humidity >= 80.0
    
    if is_frost_possible and cold_score >= 85.0:
        alerts.append((
            "Sương muối & Băng giá", 
            "Red", 
            f"Bức xạ nhiệt ban đêm cực mạnh làm đóng băng sương muối (Điểm rét: {cold_score}, Nhiệt đất: {min_soil_temp:.1f}°C). Nguy cơ tàn phá rau màu diện rộng."
        ))
    elif min_temp < 13.0 or cold_score >= 65.0:
        alerts.append((
            "Rét đậm, rét hại", 
            "Orange", 
            f"Rét hại nghiêm trọng hại cho sức khỏe và đàn gia súc (Điểm rét: {cold_score}, Nhiệt độ thấp nhất: {min_temp:.1f}°C)."
        ))
    elif min_temp < 15.0 or cold_score >= 35.0:
        alerts.append((
            "Rét đậm, rét hại", 
            "Yellow", 
            f"Rét đậm vùng cao (Điểm rét: {cold_score}, Nhiệt độ: {min_temp:.1f}°C)."
        ))

    # 6. CÔNG THỨC SƯƠNG MÙ DÀY ĐẶC
    min_vis = daily_data.get("min_visibility", 10000.0)
    raw_fog = max(0, 2000 - min_vis) / 10.0
    fog_score = normalize_to_100(raw_fog, THRESHOLDS["fog_yellow"], THRESHOLDS["fog_orange"], THRESHOLDS["fog_red"])
    
    if fog_score >= 85.0:
        alerts.append((
            "Sương mù dày đặc", 
            "Red", 
            f"Sương mù đặc biệt dày đặc hạn chế tầm nhìn dưới 200m (Điểm sương mù: {fog_score}). Giao thông trên đèo cực kỳ nguy hiểm."
        ))
    elif fog_score >= 65.0:
        alerts.append((
            "Sương mù dày đặc", 
            "Orange", 
            f"Sương mù dày hạn chế tầm nhìn dưới 500m (Điểm sương mù: {fog_score}). Bật đèn sương mù và đi chậm trên các tuyến đèo."
        ))
    elif fog_score >= 35.0:
        alerts.append((
            "Sương mù dày đặc", 
            "Yellow", 
            f"Sương mù rải rác làm giảm tầm nhìn vào sáng sớm (Điểm: {fog_score})."
        ))

    # 7. CÔNG THỨC NGUY CƠ CHÁY RỪNG
    min_humidity = daily_data.get("min_humidity", 80.0)
    max_temp = daily_data.get("max_temp_adjusted", 25.0)
    max_wind_speed = daily_data.get("max_wind_speed", 5.0)
    
    raw_wildfire = (max_temp * 2.0 + (100 - min_humidity) * 1.5 + max_wind_speed * 0.8 - avg_soil_moist_shallow * 100)
    
    # Nếu có mưa trong ngày, dập tắt nguy cơ cháy rừng
    if sum_rain_24h > 2.0:
        raw_wildfire *= 0.1
        
    wildfire_score = normalize_to_100(raw_wildfire, THRESHOLDS["wildfire_yellow"], THRESHOLDS["wildfire_orange"], THRESHOLDS["wildfire_red"])
    
    if sum_rain_24h <= 2.0:
        if wildfire_score >= 85.0 and min_humidity < 45.0:
            alerts.append((
                "Cháy rừng", 
                "Red", 
                f"Hanh khô cực đoan, gió thổi lớn, rừng dễ bén lửa (Điểm cháy: {wildfire_score}, Ẩm khí: {min_humidity:.0f}%). Tuyệt đối cấm củi lửa trong rừng."
            ))
        elif wildfire_score >= 65.0 and min_humidity < 55.0:
            alerts.append((
                "Cháy rừng", 
                "Orange", 
                f"Độ ẩm không khí thấp hanh khô (Điểm cháy: {wildfire_score}). Đề phòng xảy ra cháy rừng."
            ))
        elif wildfire_score >= 35.0:
            alerts.append((
                "Cháy rừng", 
                "Yellow", 
                f"Chú ý thời tiết hanh khô cục bộ (Điểm cháy: {wildfire_score})."
            ))

    return alerts

def evaluate_hourly_hazard_level(r, real_elevation, model_elevation):
    """
    Đánh giá mức độ cảnh báo tích hợp cho một giờ cụ thể.
    Trả về: (nhiệt_độ_hiệu_chỉnh, mức_độ_cảnh_báo)
    Mức độ: Red > Orange > Yellow > Green
    """
    el_diff = real_elevation - model_elevation
    temp_adj = r["temperature"] - (0.0065 * el_diff)
    soil_temp_adj = r["soil_temp_0cm"] - (0.0065 * el_diff)
    
    level = "Green"
    
    # 1. Mưa
    precip = r["precipitation"]
    if precip >= 40.0:
        level = "Red"
    elif precip >= 25.0:
        level = "Orange"
    elif precip >= 10.0:
        level = "Yellow"
        
    # 2. Dông lốc sét
    cape = r["cape"]
    wind_gust = r["wind_gust"]
    if level != "Red":
        if cape >= 2500.0 or wind_gust >= 70.0:
            level = "Red"
        elif (cape >= 1500.0 or wind_gust >= 50.0) and level != "Orange":
            level = "Orange"
        elif (cape >= 800.0 or wind_gust >= 30.0) and level == "Green":
            level = "Yellow"
            
    # 3. Sương mù
    vis = r["visibility"]
    if level != "Red":
        if vis <= 200.0:
            level = "Red"
        elif vis <= 500.0 and level != "Orange":
            level = "Orange"
        elif vis <= 1000.0 and level == "Green":
            level = "Yellow"
            
    # 4. Rét / Sương muối
    hum = r["humidity"]
    try:
        cloud = r["cloud_cover"]
    except Exception:
        cloud = 100.0
    is_frost = (temp_adj < 5.0 or soil_temp_adj <= 1.0) and cloud < 20.0 and hum >= 80.0
    if level != "Red":
        if is_frost:
            level = "Red"
        elif temp_adj < 13.0 and level != "Orange":
            level = "Orange"
        elif temp_adj < 15.0 and level == "Green":
            level = "Yellow"
            
    # 5. Cháy rừng
    wind_speed = r["wind_speed"]
    if level == "Green" and precip <= 0.1:
        if temp_adj >= 35.0 and hum < 45.0 and wind_speed >= 15.0:
            level = "Red"
        elif temp_adj >= 30.0 and hum < 55.0 and wind_speed >= 10.0:
            level = "Orange"
        elif hum < 60.0:
            level = "Yellow"
            
    return round(temp_adj, 1), level
