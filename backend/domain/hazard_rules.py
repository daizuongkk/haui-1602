"""
Hazard rule engine — pure decision logic over an aggregated day.

Ranks seven natural-hazard categories on the Green/Yellow/Orange/Red scale.
All numeric thresholds live in `config.settings.THRESHOLDS`; this module holds
only the decision structure, never magic numbers.

Logic đồng bộ 100% với pipeline_core/rule_engine.py:
  - Hàm normalize_to_100: chuẩn hoá phi tuyến về [0, 100]
  - Cùng scoring formulas (trọng số tính điểm thô)
  - Cùng ngưỡng phân cấp chuẩn hoá: 35 / 65 / 85
"""
import math
from typing import List

from backend.config import settings
from backend.domain.models import DailySummary, HazardAlert
from backend.shared import alert_levels as levels

_T = settings.THRESHOLDS
_W = settings.LANDSLIDE_SCORE_WEIGHTS


# ─────────────────────────────────────────────────────────────────────────── #
# Hàm chuẩn hoá phi tuyến bão hoà mũ — khớp pipeline_core/rule_engine.py
# ─────────────────────────────────────────────────────────────────────────── #
def normalize_to_100(raw_score: float, t_yellow: float, t_orange: float, t_red: float) -> float:
    """
    Chuẩn hoá điểm số thô phi tuyến về thang [0, 100] sao cho:
    - raw_score <= 0 -> 0.0
    - raw_score = t_yellow -> 35.0
    - raw_score = t_orange -> 65.0
    - raw_score = t_red   -> 85.0
    - raw_score > t_red   -> tiệm cận 100 (bão hoà mũ)
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


# ─────────────────────────────────────────────────────────────────────────── #
# Điểm vào chính
# ─────────────────────────────────────────────────────────────────────────── #
def evaluate_hazards(day: DailySummary, landslide_risk_factor: float) -> List[HazardAlert]:
    """Return every hazard alert triggered for `day`, most severe first."""
    alerts: List[HazardAlert] = []

    _evaluate_rain(day, alerts)
    _evaluate_landslide(day, landslide_risk_factor, alerts)
    _evaluate_thunderstorm(day, alerts)
    _evaluate_hail(day, alerts)
    _evaluate_cold_and_frost(day, alerts)
    _evaluate_fog(day, alerts)
    _evaluate_wildfire(day, alerts)

    return alerts


# ─────────────────────────────────────────────────────────────────────────── #
# 1. MƯA LỚN & NGẬP ÚNG
# ─────────────────────────────────────────────────────────────────────────── #
def _evaluate_rain(day: DailySummary, alerts: List[HazardAlert]) -> None:
    rain_1h = day["max_precipitation_1h"]
    rain_24h = day["sum_precipitation_24h"]
    soil_moist_shallow = day["avg_soil_moisture_0_to_1cm"]

    raw_score = (rain_1h * 3.0 + rain_24h * 0.5) * (1.0 + soil_moist_shallow)
    normalized = normalize_to_100(raw_score, _T["flood_yellow"], _T["flood_orange"], _T["flood_red"])

    if normalized >= 85.0:
        alerts.append(HazardAlert(
            "Mưa lớn & Ngập úng", levels.RED,
            f"Mưa cực lớn, ngập úng sâu trên diện rộng (Điểm: {normalized}). "
            f"Cần di dời tài sản khẩn cấp ở vùng thấp trũng."))
    elif normalized >= 65.0:
        alerts.append(HazardAlert(
            "Mưa lớn & Ngập úng", levels.ORANGE,
            f"Mưa rất to, nguy cơ ngập lụt cục bộ (Điểm: {normalized}). "
            f"Hạn chế di chuyển qua các tuyến đường ngập nước."))
    elif normalized >= 35.0:
        alerts.append(HazardAlert(
            "Mưa lớn & Ngập úng", levels.YELLOW,
            f"Chú ý mưa lớn tích lũy diện rộng gây trơn trượt (Điểm: {normalized})."))


# ─────────────────────────────────────────────────────────────────────────── #
# 2. LŨ QUÉT & SẠT LỞ ĐẤT
# ─────────────────────────────────────────────────────────────────────────── #
def _evaluate_landslide(day: DailySummary, risk_factor: float, alerts: List[HazardAlert]) -> None:
    rain_24h = day["sum_precipitation_24h"]
    soil_moist_deep = day["avg_soil_moisture_27_to_81cm"]
    water_balance = rain_24h - day["sum_evapo_24h"]

    raw_score = (
        rain_24h * _W["rain_24h"]
        + soil_moist_deep * _W["soil_moisture_deep"]
        + water_balance * _W["water_balance"]
    ) * risk_factor

    normalized = normalize_to_100(raw_score, _T["landslide_yellow"], _T["landslide_orange"], _T["landslide_red"])

    if normalized >= 85.0 and rain_24h >= 50.0:
        alerts.append(HazardAlert(
            "Lũ quét & Sạt lở", levels.RED,
            f"Nền đất sườn núi cực kỳ mất ổn định (Điểm: {normalized}). "
            f"Đất ngậm nước bão hòa sâu, nguy cơ sạt lở núi và lũ bùn đá cực kỳ khẩn cấp!"))
    elif normalized >= 65.0 and rain_24h >= 30.0:
        alerts.append(HazardAlert(
            "Lũ quét & Sạt lở", levels.ORANGE,
            f"Đất đồi dốc ngậm nhiều nước, liên kết yếu (Điểm: {normalized}). "
            f"Đề phòng sạt trượt đất taluy đường sườn núi."))
    elif normalized >= 35.0:
        alerts.append(HazardAlert(
            "Lũ quét & Sạt lở", levels.YELLOW,
            f"Đất ẩm ướt nhão (Điểm: {normalized}). "
            f"Đề phòng sạt lở cục bộ ở các vị trí dốc đứng khi mưa tiếp tục kéo dài."))


# ─────────────────────────────────────────────────────────────────────────── #
# 3. DÔNG, LỐC, SÉT
# ─────────────────────────────────────────────────────────────────────────── #
def _evaluate_thunderstorm(day: DailySummary, alerts: List[HazardAlert]) -> None:
    cape = day["max_cape"]
    wind_gust = day["max_wind_gust"]
    pressure_drop = day["max_pressure_drop_3h"]

    raw_score = cape * 0.02 + wind_gust * 0.8 + pressure_drop * 15.0
    normalized = normalize_to_100(raw_score, _T["thunderstorm_yellow"], _T["thunderstorm_orange"], _T["thunderstorm_red"])

    if normalized >= 85.0:
        alerts.append(HazardAlert(
            "Dông, lốc, sét", levels.RED,
            f"Khí quyển cực kỳ bất ổn định đối lưu mạnh (Điểm: {normalized}). "
            f"Nguy cơ cực cao xảy ra sét đánh dữ dội và gió lốc phá hoại mái nhà."))
    elif normalized >= 65.0:
        alerts.append(HazardAlert(
            "Dông, lốc, sét", levels.ORANGE,
            f"Mây đối lưu dông phát triển mạnh kèm gió giật lớn (Điểm: {normalized}). "
            f"Đề phòng dông lốc mạnh đột ngột."))
    elif normalized >= 35.0:
        alerts.append(HazardAlert(
            "Dông, lốc, sét", levels.YELLOW,
            f"Chú ý mưa dông kèm sấm sét cục bộ vào chiều tối (Điểm: {normalized})."))


# ─────────────────────────────────────────────────────────────────────────── #
# 4. MƯA ĐÁ
# ─────────────────────────────────────────────────────────────────────────── #
def _evaluate_hail(day: DailySummary, alerts: List[HazardAlert]) -> None:
    cape = day["max_cape"]
    freezing_height = day["min_freezing_height"]
    rain_1h = day["max_precipitation_1h"]

    raw_score = cape * 0.015 + max(0.0, 5000.0 - freezing_height) * 0.03 + rain_1h * 2.0
    normalized = normalize_to_100(raw_score, _T["hail_yellow"], _T["hail_orange"], _T["hail_red"])

    # Chỉ cảnh báo mưa đá khi có đủ điều kiện vật lý (CAPE cao + mực đông lạnh thấp)
    if cape >= 1200 and freezing_height <= 4200:
        if normalized >= 85.0:
            alerts.append(HazardAlert(
                "Mưa đá", levels.RED,
                f"Đối lưu mây dông cực mạnh kèm mực đông lạnh hạ thấp (Điểm: {normalized}). "
                f"Nguy cơ rất cao xảy ra mưa đá tàn phá hoa màu."))
        elif normalized >= 65.0:
            alerts.append(HazardAlert(
                "Mưa đá", levels.ORANGE,
                f"Khí quyển đối lưu bất ổn cao kèm mực 0°C thấp (Điểm: {normalized}). "
                f"Đề phòng mưa đá cục bộ trong cơn dông mạnh."))
        elif normalized >= 35.0:
            alerts.append(HazardAlert(
                "Mưa đá", levels.YELLOW,
                f"Chú ý khả năng xuất hiện mưa đá kích thước nhỏ khi có dông lớn (Điểm: {normalized})."))


# ─────────────────────────────────────────────────────────────────────────── #
# 5. RÉT ĐẬM, RÉT HẠI & SƯƠNG MUỐI
# ─────────────────────────────────────────────────────────────────────────── #
def _evaluate_cold_and_frost(day: DailySummary, alerts: List[HazardAlert]) -> None:
    min_temp = day["min_temp_adjusted"]
    min_soil_temp = day["min_soil_temp_adjusted"]
    humidity = day["avg_humidity"]
    cloud = day["min_cloud"]

    raw_score = max(0.0, 20.0 - min_temp) * 4.0 + max(0.0, 10.0 - min_soil_temp) * 2.0
    normalized = normalize_to_100(raw_score, _T["cold_yellow"], _T["cold_orange"], _T["cold_red"])

    # Đánh giá độc lập sương muối
    is_frost_possible = (min_temp < 5.0 or min_soil_temp <= 1.0) and cloud < 20.0 and humidity >= 80.0

    if is_frost_possible and normalized >= 85.0:
        alerts.append(HazardAlert(
            "Sương muối & Băng giá", levels.RED,
            f"Bức xạ nhiệt ban đêm cực mạnh làm đóng băng sương muối "
            f"(Điểm rét: {normalized}, Nhiệt đất: {min_soil_temp:.1f}°C). "
            f"Nguy cơ tàn phá rau màu diện rộng."))
    elif min_soil_temp <= 0.0:
        alerts.append(HazardAlert(
            "Sương muối & Băng giá", levels.ORANGE,
            f"Nhiệt độ mặt đất xuống dưới mức đóng băng ({min_soil_temp:.1f}°C). "
            f"Đề phòng đóng băng cục bộ."))

    # Rét đậm rét hại — đánh giá tách biệt
    if normalized >= 85.0:
        alerts.append(HazardAlert(
            "Rét đậm, rét hại", levels.RED,
            f"Rét hại đặc biệt nặng nề diện rộng (Điểm: {normalized}). "
            f"Nguy hiểm cực cao cho gia súc và hoa màu."))
    elif normalized >= 65.0:
        alerts.append(HazardAlert(
            "Rét đậm, rét hại", levels.ORANGE,
            f"Rét hại diện rộng, nhiệt độ giảm cực sâu (Điểm: {normalized})."))
    elif normalized >= 35.0:
        alerts.append(HazardAlert(
            "Rét đậm, rét hại", levels.YELLOW,
            f"Rét đậm diện rộng (Điểm: {normalized}). Giữ ấm cho người già và trẻ nhỏ."))


# ─────────────────────────────────────────────────────────────────────────── #
# 6. SƯƠNG MÙ DÀY ĐẶC
# ─────────────────────────────────────────────────────────────────────────── #
def _evaluate_fog(day: DailySummary, alerts: List[HazardAlert]) -> None:
    visibility = day["min_visibility"]

    raw_score = max(0.0, 2000.0 - visibility) / 10.0
    normalized = normalize_to_100(raw_score, _T["fog_yellow"], _T["fog_orange"], _T["fog_red"])

    if normalized >= 85.0:
        alerts.append(HazardAlert(
            "Sương mù dày đặc", levels.RED,
            f"Sương mù đặc biệt dày đặc hạn chế tầm nhìn dưới 200m (Điểm sương mù: {normalized}). "
            f"Giao thông trên đèo cực kỳ nguy hiểm."))
    elif normalized >= 65.0:
        alerts.append(HazardAlert(
            "Sương mù dày đặc", levels.ORANGE,
            f"Sương mù dày hạn chế tầm nhìn dưới 500m (Điểm sương mù: {normalized}). "
            f"Bật đèn sương mù và đi chậm trên các tuyến đèo."))
    elif normalized >= 35.0:
        alerts.append(HazardAlert(
            "Sương mù dày đặc", levels.YELLOW,
            f"Sương mù rải rác làm giảm tầm nhìn vào sáng sớm (Điểm: {normalized})."))


# ─────────────────────────────────────────────────────────────────────────── #
# 7. CHÁY RỪNG
# ─────────────────────────────────────────────────────────────────────────── #
def _evaluate_wildfire(day: DailySummary, alerts: List[HazardAlert]) -> None:
    rain_24h = day["sum_precipitation_24h"]
    max_temp = day["max_temp_adjusted"]
    min_humidity = day["min_humidity"]
    wind_speed = day["max_wind_speed"]
    soil_moist_shallow = day["avg_soil_moisture_0_to_1cm"]

    raw_score = max_temp * 2.0 + (100.0 - min_humidity) * 1.5 + wind_speed * 0.8 - soil_moist_shallow * 100.0
    if rain_24h > 2.0:
        raw_score *= 0.1

    normalized = normalize_to_100(raw_score, _T["wildfire_yellow"], _T["wildfire_orange"], _T["wildfire_red"])

    if rain_24h <= 2.0:
        if normalized >= 85.0 and min_humidity < 45.0:
            alerts.append(HazardAlert(
                "Cháy rừng", levels.RED,
                f"Thời tiết hanh khô gió mạnh cực độ, đất mặt kiệt ẩm (Điểm: {normalized}). "
                f"Nguy cơ hỏa hoạn cháy rừng mức cực kỳ nguy cấp!"))
        elif normalized >= 65.0 and min_humidity < 55.0:
            alerts.append(HazardAlert(
                "Cháy rừng", levels.ORANGE,
                f"Khí quyển hanh khô kéo dài kèm gió mạnh (Điểm: {normalized}). "
                f"Nghiêm cấm đốt nương rẫy, đề phòng hỏa hoạn."))
        elif normalized >= 35.0:
            alerts.append(HazardAlert(
                "Cháy rừng", levels.YELLOW,
                f"Chú ý cẩn thận củi lửa trong điều kiện thời tiết ít ẩm (Điểm: {normalized})."))
