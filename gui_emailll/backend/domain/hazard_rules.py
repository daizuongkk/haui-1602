"""
Hazard rule engine — pure decision logic over an aggregated day.

Ranks seven natural-hazard categories on the Green/Yellow/Orange/Red scale.
All numeric thresholds live in `config.settings.THRESHOLDS`; this module holds
only the decision structure, never magic numbers.
"""
from typing import List

from backend.config import settings
from backend.domain.models import DailySummary, HazardAlert
from backend.shared import alert_levels as levels

_T = settings.THRESHOLDS
_W = settings.LANDSLIDE_SCORE_WEIGHTS


def evaluate_hazards(day: DailySummary, landslide_risk_factor: float) -> List[HazardAlert]:
    """Return every hazard alert triggered for `day`, most detailed first."""
    alerts: List[HazardAlert] = []
    _evaluate_rain(day, alerts)
    _evaluate_landslide(day, landslide_risk_factor, alerts)
    _evaluate_thunderstorm(day, alerts)
    _evaluate_hail(day, alerts)
    _evaluate_cold_and_frost(day, alerts)
    _evaluate_fog(day, alerts)
    _evaluate_wildfire(day, alerts)
    return alerts


def _evaluate_rain(day: DailySummary, alerts: List[HazardAlert]) -> None:
    rain_1h = day["max_precipitation_1h"]
    rain_24h = day["sum_precipitation_24h"]

    if rain_24h >= _T["rain_extreme_24h"] or rain_1h >= _T["rain_extreme_1h"]:
        alerts.append(HazardAlert(
            "Mưa lớn & Ngập úng", levels.RED,
            f"Mưa cực lớn (Cộng dồn: {rain_24h:.1f}mm, Cường độ: {rain_1h:.1f}mm/h). "
            f"Nguy cơ ngập úng sâu diện rộng."))
    elif rain_24h >= _T["rain_very_heavy_24h"] or rain_1h >= _T["rain_heavy_1h"]:
        alerts.append(HazardAlert(
            "Mưa lớn & Ngập úng", levels.ORANGE,
            f"Mưa rất to (Cộng dồn: {rain_24h:.1f}mm, Cường độ: {rain_1h:.1f}mm/h). "
            f"Đề phòng ngập lụt cục bộ vùng trũng."))
    elif rain_24h >= _T["rain_heavy_24h"]:
        alerts.append(HazardAlert(
            "Mưa lớn & Ngập úng", levels.YELLOW,
            f"Mưa lớn diện rộng (Cộng dồn: {rain_24h:.1f}mm)."))


def _evaluate_landslide(day: DailySummary, risk_factor: float, alerts: List[HazardAlert]) -> None:
    rain_24h = day["sum_precipitation_24h"]
    soil_moist_deep = day["avg_soil_moisture_27_to_81cm"]
    water_balance = rain_24h - day["sum_evapo_24h"]

    risk_score = (
        rain_24h * _W["rain_24h"]
        + soil_moist_deep * _W["soil_moisture_deep"]
        + water_balance * _W["water_balance"]
    ) * risk_factor

    if risk_score > _T["landslide_red_score"] and rain_24h >= _T["landslide_red_min_rain_24h"]:
        alerts.append(HazardAlert(
            "Lũ quét & Sạt lở", levels.RED,
            f"Đất ngậm nước bão hòa (Độ ẩm sâu: {soil_moist_deep:.2f} m3/m3) kết hợp mưa lớn. "
            f"Nguy cơ xảy ra lũ quét và sạt lở núi cực cao!"))
    elif risk_score > _T["landslide_orange_score"] and rain_24h >= _T["landslide_orange_min_rain_24h"]:
        alerts.append(HazardAlert(
            "Lũ quét & Sạt lở", levels.ORANGE,
            "Nền đất yếu, sườn dốc ngậm nhiều nước. Đề phòng sạt trượt đất đá taluy đường."))
    elif rain_24h >= _T["landslide_yellow_min_rain_24h"] or soil_moist_deep > _T["landslide_soil_moist_deep"]:
        alerts.append(HazardAlert(
            "Lũ quét & Sạt lở", levels.YELLOW,
            "Đất ẩm ướt, chú ý sạt lở đất cục bộ tại các vị trí dốc đứng khi có mưa tiếp diễn."))


def _evaluate_thunderstorm(day: DailySummary, alerts: List[HazardAlert]) -> None:
    cape = day["max_cape"]
    wind_gust = day["max_wind_gust"]
    pressure_drop = day["max_pressure_drop_3h"]

    if cape >= _T["cape_red"] and (wind_gust >= _T["wind_gust_red"] or pressure_drop >= _T["pressure_drop_3h_red"]):
        alerts.append(HazardAlert(
            "Dông, lốc, sét", levels.RED,
            f"Khí quyển cực đoan (CAPE: {cape:.0f} J/kg, Gió giật: {wind_gust:.1f} km/h). "
            f"Rủi ro rất cao về giông lốc xoáy tàn phá mái nhà và sét đánh mạnh."))
    elif cape >= _T["cape_orange"] or wind_gust >= _T["wind_gust_orange"] or pressure_drop >= _T["pressure_drop_3h_orange"]:
        alerts.append(HazardAlert(
            "Dông, lốc, sét", levels.ORANGE,
            f"Đối lưu nhiệt ẩm phát triển mạnh (CAPE: {cape:.0f} J/kg, Gió giật: {wind_gust:.1f} km/h). "
            f"Đề phòng dông lốc mạnh và sấm sét dữ dội."))
    elif cape >= _T["cape_yellow"]:
        alerts.append(HazardAlert(
            "Dông, lốc, sét", levels.YELLOW,
            f"Khí quyển không ổn định (CAPE: {cape:.0f} J/kg). "
            f"Chú ý mưa dông cục bộ kèm sấm sét vào chiều tối."))


def _evaluate_hail(day: DailySummary, alerts: List[HazardAlert]) -> None:
    cape = day["max_cape"]
    freezing_height = day["min_freezing_height"]
    rain_1h = day["max_precipitation_1h"]

    if cape >= _T["cape_hail_red"] and freezing_height <= _T["freezing_height_red"] and rain_1h > _T["hail_red_min_rain_1h"]:
        alerts.append(HazardAlert(
            "Mưa đá", levels.RED,
            f"Mực đông lạnh hạ thấp xuống {freezing_height:.0f}m kèm đối lưu cực mạnh. "
            f"Nguy cơ rất cao xảy ra mưa đá rơi phá hoại mùa màng."))
    elif cape >= _T["cape_hail_orange"] and freezing_height <= _T["freezing_height_orange"]:
        alerts.append(HazardAlert(
            "Mưa đá", levels.ORANGE,
            f"Mực 0°C thấp ({freezing_height:.0f}m) + CAPE: {cape:.0f} J/kg. "
            f"Cần đề phòng có mưa đá cục bộ trong các cơn dông."))


def _evaluate_cold_and_frost(day: DailySummary, alerts: List[HazardAlert]) -> None:
    min_temp = day["min_temp_adjusted"]
    min_soil_temp = day["min_soil_temp_adjusted"]

    if min_temp < _T["frost_temp_threshold"] or min_soil_temp <= _T["frost_soil_temp"]:
        if day["min_cloud"] < _T["frost_red_max_cloud"] and day["avg_humidity"] >= _T["frost_red_min_humidity"]:
            alerts.append(HazardAlert(
                "Sương muối & Băng giá", levels.RED,
                f"Nhiệt độ đất xuống {min_soil_temp:.1f}°C kèm đêm quang mây. "
                f"Nguy cơ sương muối đóng băng diện rộng tàn phá hoa màu."))
        else:
            alerts.append(HazardAlert(
                "Sương muối & Băng giá", levels.ORANGE,
                f"Nhiệt độ mặt đất rất thấp ({min_soil_temp:.1f}°C). "
                f"Đề phòng hiện tượng sương giá và đóng băng cục bộ."))

    # Rated independently so a cold night is never masked by a frost alert.
    if min_temp < _T["cold_severe_temp"]:
        alerts.append(HazardAlert(
            "Rét đậm, rét hại", levels.ORANGE,
            f"Rét hại diện rộng (Nhiệt độ thấp nhất: {min_temp:.1f}°C). "
            f"Nguy hiểm cho sức khỏe gia súc và cây trồng."))
    elif min_temp < _T["cold_moderate_temp"]:
        alerts.append(HazardAlert(
            "Rét đậm, rét hại", levels.YELLOW,
            f"Rét đậm (Nhiệt độ thấp nhất: {min_temp:.1f}°C)."))


def _evaluate_fog(day: DailySummary, alerts: List[HazardAlert]) -> None:
    visibility = day["min_visibility"]

    if visibility <= _T["fog_red_visibility"]:
        alerts.append(HazardAlert(
            "Sương mù dày đặc", levels.RED,
            f"Sương mù đặc biệt dày đặc (Tầm nhìn: {visibility:.0f}m). "
            f"Tầm nhìn cực hạn, cản trở di chuyển trên các cung đèo dốc."))
    elif visibility <= _T["fog_orange_visibility"]:
        alerts.append(HazardAlert(
            "Sương mù dày đặc", levels.ORANGE,
            f"Sương mù dày hạn chế tầm nhìn ({visibility:.0f}m). "
            f"Chú ý bật đèn sương mù khi lưu thông."))
    elif visibility <= _T["fog_yellow_visibility"]:
        alerts.append(HazardAlert(
            "Sương mù dày đặc", levels.YELLOW,
            "Sương mù rải rác làm giảm tầm nhìn vào sáng sớm."))


def _evaluate_wildfire(day: DailySummary, alerts: List[HazardAlert]) -> None:
    if day["sum_precipitation_24h"] != 0:
        return
    min_humidity = day["min_humidity"]
    max_temp = day.get("max_temp_adjusted", 25.0)
    if not (min_humidity < _T["wildfire_humidity"] and max_temp >= _T["wildfire_temp"]):
        return

    if day["max_wind_speed"] >= _T["wildfire_wind_speed"] and day["avg_soil_moisture_0_to_1cm"] < _T["wildfire_soil_moist"]:
        alerts.append(HazardAlert(
            "Cháy rừng", levels.RED,
            f"Thời tiết hanh khô cực độ (Ẩm: {min_humidity:.0f}%, Gió mạnh: {day['max_wind_speed']:.1f} km/h, "
            f"Nhiệt độ: {max_temp:.1f}°C). Rủi ro cháy rừng cấp độ cực kỳ nguy hiểm."))
    else:
        alerts.append(HazardAlert(
            "Cháy rừng", levels.ORANGE,
            f"Không khí hanh khô kéo dài (Độ ẩm: {min_humidity:.0f}%, Nhiệt độ: {max_temp:.1f}°C). "
            f"Đề phòng cẩn thận củi lửa."))
