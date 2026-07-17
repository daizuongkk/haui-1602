from config import THRESHOLDS

def evaluate_hazards(daily_data, landslide_risk_factor):
    """
    Phân tích dữ liệu thời tiết đã hiệu chỉnh để xếp hạng mức độ nguy hiểm của thiên tai.
    Trả về: danh sách các cảnh báo dạng (Tên thiên tai, Mức độ màu, Mô tả chi tiết).
    Mức độ màu: Green (Bình thường), Yellow (Chú ý), Orange (Nguy hiểm), Red (Cực kỳ nguy hiểm)
    """
    alerts = []
    
    # 1. CẢNH BÁO MƯA LỚN & NGẬP ÚNG CỤC BỘ
    max_rain_1h = daily_data["max_precipitation_1h"]
    sum_rain_24h = daily_data["sum_precipitation_24h"]
    
    if sum_rain_24h >= THRESHOLDS["rain_extreme_24h"] or max_rain_1h >= THRESHOLDS["rain_extreme_1h"]:
        alerts.append((
            "Mưa lớn & Ngập úng", 
            "Red", 
            f"Mưa cực lớn (Cộng dồn: {sum_rain_24h:.1f}mm, Cường độ: {max_rain_1h:.1f}mm/h). Nguy cơ ngập úng sâu diện rộng."
        ))
    elif sum_rain_24h >= THRESHOLDS["rain_very_heavy_24h"] or max_rain_1h >= THRESHOLDS["rain_heavy_1h"]:
        alerts.append((
            "Mưa lớn & Ngập úng", 
            "Orange", 
            f"Mưa rất to (Cộng dồn: {sum_rain_24h:.1f}mm, Cường độ: {max_rain_1h:.1f}mm/h). Đề phòng ngập lụt cục bộ vùng trũng."
        ))
    elif sum_rain_24h >= THRESHOLDS["rain_heavy_24h"]:
        alerts.append((
            "Mưa lớn & Ngập úng", 
            "Yellow", 
            f"Mưa lớn diện rộng (Cộng dồn: {sum_rain_24h:.1f}mm)."
        ))

    # 2. CẢNH BÁO LŨ QUẾT & SẠT LỞ ĐẤT
    avg_soil_moist_deep = daily_data["avg_soil_moisture_27_to_81cm"]
    water_balance = sum_rain_24h - daily_data["sum_evapo_24h"]
    
    # Tính điểm nguy cơ sạt lở kết hợp mưa hiện tại, độ ngậm nước đất sâu và hiệu số nước
    risk_score = (sum_rain_24h * 0.5 + avg_soil_moist_deep * 150 + water_balance * 0.3) * landslide_risk_factor
    
    if risk_score > THRESHOLDS["landslide_red_score"] and sum_rain_24h >= 50:
        alerts.append((
            "Lũ quét & Sạt lở", 
            "Red", 
            f"Đất ngậm nước bão hòa (Độ ẩm sâu: {avg_soil_moist_deep:.2f} m3/m3) kết hợp mưa lớn. Nguy cơ xảy ra lũ quét và sạt lở núi cực cao!"
        ))
    elif risk_score > THRESHOLDS["landslide_orange_score"] and sum_rain_24h >= 30:
        alerts.append((
            "Lũ quét & Sạt lở", 
            "Orange", 
            f"Nền đất yếu, sườn dốc ngậm nhiều nước. Đề phòng sạt trượt đất đá taluy đường."
        ))
    elif sum_rain_24h >= 30 or avg_soil_moist_deep > THRESHOLDS["landslide_soil_moist_deep"]:
        alerts.append((
            "Lũ quét & Sạt lở", 
            "Yellow", 
            "Đất ẩm ướt, chú ý sạt lở đất cục bộ tại các vị trí dốc đứng khi có mưa tiếp diễn."
        ))

    # 3. CẢNH BÁO DÔNG, LỐC, SÉT
    max_cape = daily_data["max_cape"]
    max_wind_gust = daily_data["max_wind_gust"]
    press_change_3h = daily_data["max_pressure_drop_3h"]
    
    if max_cape >= THRESHOLDS["cape_red"] and (max_wind_gust >= THRESHOLDS["wind_gust_red"] or press_change_3h >= THRESHOLDS["pressure_drop_3h_red"]):
        alerts.append((
            "Dông, lốc, sét", 
            "Red", 
            f"Khí quyển cực đoan (CAPE: {max_cape:.0f} J/kg, Gió giật: {max_wind_gust:.1f} km/h). Rủi ro rất cao về giông lốc xoáy tàn phá mái nhà và sét đánh mạnh."
        ))
    elif max_cape >= THRESHOLDS["cape_orange"] or max_wind_gust >= THRESHOLDS["wind_gust_orange"] or press_change_3h >= THRESHOLDS["pressure_drop_3h_orange"]:
        alerts.append((
            "Dông, lốc, sét", 
            "Orange", 
            f"Đối lưu nhiệt ẩm phát triển mạnh (CAPE: {max_cape:.0f} J/kg, Gió giật: {max_wind_gust:.1f} km/h). Đề phòng dông lốc mạnh và sấm sét dữ dội."
        ))
    elif max_cape >= THRESHOLDS["cape_yellow"]:
        alerts.append((
            "Dông, lốc, sét", 
            "Yellow", 
            f"Khí quyển không ổn định (CAPE: {max_cape:.0f} J/kg). Chú ý mưa dông cục bộ kèm sấm sét vào chiều tối."
        ))

    # 4. CẢNH BÁO MƯA ĐÁ
    min_freezing_height = daily_data["min_freezing_height"]
    if max_cape >= 2000 and min_freezing_height <= THRESHOLDS["freezing_height_red"] and max_rain_1h > 10:
        alerts.append((
            "Mưa đá", 
            "Red", 
            f"Mực đông lạnh hạ thấp xuống {min_freezing_height:.0f}m kèm đối lưu cực mạnh. Nguy cơ rất cao xảy ra mưa đá rơi phá hoại mùa màng."
        ))
    elif max_cape >= 1200 and min_freezing_height <= THRESHOLDS["freezing_height_orange"]:
        alerts.append((
            "Mưa đá", 
            "Orange", 
            f"Mực 0°C thấp ({min_freezing_height:.0f}m) + CAPE: {max_cape:.0f} J/kg. Cần đề phòng có mưa đá cục bộ trong các cơn dông."
        ))

    # 5. CẢNH BÁO RÉT ĐẬM, RÉT HẠI & SƯƠNG MUỐI
    min_temp = daily_data["min_temp_adjusted"]
    min_soil_temp = daily_data["min_soil_temp_adjusted"]
    avg_humidity = daily_data["avg_humidity"]
    min_cloud = daily_data["min_cloud"]
    
    if min_temp < THRESHOLDS["frost_temp_threshold"] or min_soil_temp <= THRESHOLDS["frost_soil_temp"]:
        if min_cloud < 20 and avg_humidity >= 80:
            alerts.append((
                "Sương muối & Băng giá", 
                "Red", 
                f"Nhiệt độ đất xuống {min_soil_temp:.1f}°C kèm đêm quang mây. Nguy cơ sương muối đóng băng diện rộng tàn phá hoa màu."
            ))
        else:
            alerts.append((
                "Sương muối & Băng giá", 
                "Orange", 
                f"Nhiệt độ mặt đất rất thấp ({min_soil_temp:.1f}°C). Đề phòng hiện tượng sương giá và đóng băng cục bộ."
            ))
    # Đánh giá rét đậm, rét hại độc lập để tránh bỏ sót khi có sương muối
    if min_temp < THRESHOLDS["cold_severe_temp"]:
        alerts.append((
            "Rét đậm, rét hại", 
            "Orange", 
            f"Rét hại diện rộng (Nhiệt độ thấp nhất: {min_temp:.1f}°C). Nguy hiểm cho sức khỏe gia súc và cây trồng."
        ))
    elif min_temp < THRESHOLDS["cold_moderate_temp"]:
        alerts.append((
            "Rét đậm, rét hại", 
            "Yellow", 
            f"Rét đậm (Nhiệt độ thấp nhất: {min_temp:.1f}°C)."
        ))

    # 6. CẢNH BÁO SƯƠNG MÙ
    min_vis = daily_data["min_visibility"]
    if min_vis <= THRESHOLDS["fog_red_visibility"]:
        alerts.append((
            "Sương mù dày đặc", 
            "Red", 
            f"Sương mù đặc biệt dày đặc (Tầm nhìn: {min_vis:.0f}m). Tầm nhìn cực hạn, cản trở di chuyển trên các cung đèo dốc."
        ))
    elif min_vis <= THRESHOLDS["fog_orange_visibility"]:
        alerts.append((
            "Sương mù dày đặc", 
            "Orange", 
            f"Sương mù dày hạn chế tầm nhìn ({min_vis:.0f}m). Chú ý bật đèn sương mù khi lưu thông."
        ))
    elif min_vis <= THRESHOLDS["fog_yellow_visibility"]:
        alerts.append((
            "Sương mù dày đặc", 
            "Yellow", 
            "Sương mù rải rác làm giảm tầm nhìn vào sáng sớm."
        ))

    # 7. CẢNH BÁO CHÁY RỪNG (Điều kiện hanh khô gió lớn)
    min_humidity = daily_data["min_humidity"]
    max_temp = daily_data.get("max_temp_adjusted", 25.0)
    max_wind_speed = daily_data["max_wind_speed"]
    avg_soil_moist_shallow = daily_data["avg_soil_moisture_0_to_1cm"]
    
    if sum_rain_24h == 0 and min_humidity < THRESHOLDS["wildfire_humidity"] and max_temp >= THRESHOLDS["wildfire_temp"]:
        if max_wind_speed >= THRESHOLDS["wildfire_wind_speed"] and avg_soil_moist_shallow < THRESHOLDS["wildfire_soil_moist"]:
            alerts.append((
                "Cháy rừng", 
                "Red", 
                f"Thời tiết hanh khô cực độ (Ẩm: {min_humidity:.0f}%, Gió mạnh: {max_wind_speed:.1f} km/h, Nhiệt độ: {max_temp:.1f}°C). Rủi ro cháy rừng cấp độ cực kỳ nguy hiểm."
            ))
        else:
            alerts.append((
                "Cháy rừng", 
                "Orange", 
                f"Không khí hanh khô kéo dài (Độ ẩm: {min_humidity:.0f}%, Nhiệt độ: {max_temp:.1f}°C). Đề phòng cẩn thận củi lửa."
            ))
            
    return alerts
