"""CLI entry point for the forecasting pipeline (console report + active_alerts.json)."""
from itertools import groupby

from backend.application.forecast_pipeline import ForecastPipeline, ForecastRun
from backend.config import settings
from backend.infrastructure import json_store
from backend.infrastructure.openmeteo import OpenMeteoWeatherProvider
from backend.shared import alert_levels

_HEADER = "=" * 72
_LEVEL_ICON = {alert_levels.RED: "🔴", alert_levels.ORANGE: "🟠", alert_levels.YELLOW: "🟡"}


def main() -> None:
    print(_HEADER)
    print("   HỆ THỐNG AI DỰ BÁO THỜI TIẾT VI MÔ & CẢNH BÁO THIÊN TAI ĐIỆN BIÊN")
    print(_HEADER + "\n")

    run = ForecastPipeline(OpenMeteoWeatherProvider()).run()
    _print_report(run)

    json_store.save_active_alerts(run.alert_records)
    print(f"✔ Đã xuất kết quả JSON cảnh báo tại: {settings.ACTIVE_ALERTS_FILE}")
    print(_HEADER)
    print("Hệ thống phân tích hoàn thành.")
    print(_HEADER)


def _print_report(run: ForecastRun) -> None:
    for _, day_group in groupby(run.days, key=lambda d: d.location.id):
        days = list(day_group)
        location = days[0].location
        print(f"--- ĐANG XỬ LÝ DỮ LIỆU DỰ BÁO: {location.name.upper()} ---")
        print(f"Toạ độ: Lat {location.lat}, Lon {location.lon} | Độ cao thực tế: {location.real_elevation}m")
        print(f"Độ cao lưới của mô hình: {days[0].model_elevation:.0f}m | Dự báo {len(days)} ngày.\n")

        for day in days:
            summary = day.summary
            print(
                f"  > Ngày {day.date} (Nhiệt độ: {summary['min_temp_adjusted']}°C - "
                f"{summary['max_temp_adjusted']}°C | Mưa: {summary['sum_precipitation_24h']:.1f}mm):"
            )
            if not day.alerts:
                print("    🟢 Mức độ an toàn: BÌNH THƯỜNG (Không phát hiện thiên tai)")
            for alert in day.alerts:
                icon = _LEVEL_ICON.get(alert.level, "🟡")
                print(f"    {icon} CẢNH BÁO {alert.level.upper()}: {alert.hazard} - {alert.description}")
        print("-" * 72 + "\n")

    for error in run.errors:
        print(f"❌ Lỗi khi xử lý dữ liệu của {error.location.name}: {error.message}\n")


if __name__ == "__main__":
    main()
