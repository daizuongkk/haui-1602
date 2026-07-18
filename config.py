# ==============================================================================
# CONFIGURATION MODULE: CẤU HÌNH THAM SỐ VÀ NGƯỠNG CẢNH BÁO THIÊN TAI (VOAI)
# ==============================================================================

# Danh sách 29 đặc trưng thời tiết cần gọi từ Open-Meteo
WEATHER_VARIABLES = [
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "dew_point_2m",
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "snow_depth",
    "precipitation_probability",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "surface_pressure",
    "pressure_msl",
    "cloud_cover",
    "visibility",
    "soil_temperature_0cm",
    "soil_temperature_6cm",
    "soil_temperature_18cm",
    "soil_temperature_54cm",
    "soil_moisture_0_to_1cm",
    "soil_moisture_1_to_3cm",
    "soil_moisture_3_to_9cm",
    "soil_moisture_9_to_27cm",
    "soil_moisture_27_to_81cm",
    "cape",
    "evapotranspiration",
    "et0_fao_evapotranspiration",
    "freezing_level_height",
    "weather_code",
    "is_day"
]

# Hằng số vật lý: Hệ số giảm nhiệt độ theo độ cao (0.65 độ C / 100m)
LAPSE_RATE = 0.0065

# Các ngưỡng điểm số cảnh báo rủi ro thiên tai (Risk Score Thresholds)
# Đã được hiệu chuẩn học máy để giảm tỷ lệ báo động giả (FAR)
THRESHOLDS = {
    # 1. Điểm rủi ro Mưa lớn & Ngập úng
    "flood_yellow": 40.0,
    "flood_orange": 70.0,
    "flood_red": 90.0,
    
    # 2. Điểm rủi ro Lũ quét & Sạt lở đất
    "landslide_yellow": 65.0,
    "landslide_orange": 90.0,
    "landslide_red": 115.0,
    
    # 3. Điểm rủi ro Dông, lốc, sét
    "thunderstorm_yellow": 45.0,
    "thunderstorm_orange": 70.0,
    "thunderstorm_red": 95.0,
    
    # 4. Điểm rủi ro Mưa đá
    "hail_yellow": 45.0,
    "hail_orange": 70.0,
    "hail_red": 90.0,
    
    # 5. Điểm rủi ro Rét đậm, rét hại & Sương muối
    "cold_yellow": 30.0,
    "cold_orange": 55.0,
    "cold_red": 80.0,
    
    # 6. Điểm rủi ro Sương mù dày đặc (Quy đổi theo tầm nhìn xa)
    "fog_yellow": 120.0,  # Tầm nhìn < 800m
    "fog_orange": 160.0, # Tầm nhìn < 400m
    "fog_red": 180.0,    # Tầm nhìn < 200m
    
    # 7. Điểm rủi ro Cháy rừng
    "wildfire_yellow": 110.0,
    "wildfire_orange": 145.0,
    "wildfire_red": 180.0
}

# Cấu hình API Keys các nguồn dữ liệu bổ trợ
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
