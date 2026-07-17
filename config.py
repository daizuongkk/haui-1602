# ==============================================================================
# CONFIGURATION MODULE: CẤU HÌNH THAM SỐ VÀ NGƯỠNG CẢNH BÁO THIÊN TAI
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

# Các ngưỡng cảnh báo thiên tai (Thresholds)
THRESHOLDS = {
    "rain_heavy_24h": 50,       # Ngưỡng mưa to diện rộng (Yellow)
    "rain_very_heavy_24h": 100,  # Ngưỡng mưa rất to (Orange)
    "rain_extreme_24h": 150,     # Ngưỡng mưa cực lớn (Red)
    "rain_extreme_1h": 40,       # Mưa giông cực lớn trong 1h (Red)
    "rain_heavy_1h": 25,         # Mưa giông lớn trong 1h (Orange)
    
    "landslide_red_score": 120,   # Điểm số kích hoạt sạt lở mức báo động Đỏ
    "landslide_orange_score": 80, # Điểm báo động Cam
    "landslide_soil_moist_deep": 0.35, # Ngưỡng độ ẩm đất tầng sâu bắt đầu nguy hiểm
    
    "cape_red": 2500,            # CAPE đối lưu mạnh dông lốc cực đoan (Red)
    "cape_orange": 1500,         # CAPE dông sét (Orange)
    "cape_yellow": 800,          # CAPE dông nhẹ (Yellow)
    
    "wind_gust_red": 70,         # Tốc độ gió giật lốc xoáy (Red - km/h)
    "wind_gust_orange": 50,      # Gió giật dông sét (Orange - km/h)
    "pressure_drop_3h_red": 3.0, # Áp suất giảm sút nhanh trong dông bão
    "pressure_drop_3h_orange": 2.0,
    
    "freezing_height_red": 3800, # Độ cao mực đông lạnh thấp có nguy cơ mưa đá (Red - mét)
    "freezing_height_orange": 4200,
    
    "cold_severe_temp": 13,      # Nhiệt độ rét hại (Orange - độ C)
    "cold_moderate_temp": 15,    # Nhiệt độ rét đậm (Yellow - độ C)
    "frost_temp_threshold": 5,   # Nhiệt độ 2m có nguy cơ sương muối
    "frost_soil_temp": 0,        # Nhiệt độ mặt đất tạo sương muối (độ C)
    
    "fog_red_visibility": 200,    # Tầm nhìn cực hạn sương mù đặc (Red - mét)
    "fog_orange_visibility": 500, # Sương mù cản trở giao thông (Orange - mét)
    "fog_yellow_visibility": 1000,
    
    "wildfire_humidity": 45,     # Độ ẩm không khí rất khô (Cháy rừng)
    "wildfire_temp": 35,         # Nhiệt độ không khí cao (Cháy rừng)
    "wildfire_wind_speed": 15,   # Tốc độ gió mạnh (Cháy rừng - km/h)
    "wildfire_soil_moist": 0.15  # Độ ẩm đất mặt kiệt quệ
}
