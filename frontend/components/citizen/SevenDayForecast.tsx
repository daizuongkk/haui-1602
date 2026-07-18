import { CloudRain, Wind } from "lucide-react";
import { levelStyle, LEVELS } from "@/lib/levels";
import { hazardIcon } from "@/lib/hazards";
import { cn, dayLabel } from "@/lib/utils";
import type { AlertRecord } from "@/lib/types";

// Dự báo thiên tai nhiều ngày — dạng card kéo ngang, không dùng bảng.
export function SevenDayForecast({ days, todayIso }: { days: AlertRecord[]; todayIso?: string }) {
  if (days.length === 0) return null;
  return (
    <section className="space-y-3">
      <h2 className="text-lg font-bold text-slate-900">Dự báo thiên tai các ngày tới</h2>
      <div className="no-scrollbar -mx-4 flex gap-3 overflow-x-auto px-4 pb-2">
        {days.map((d) => {
          const s = levelStyle(d.highest_alert_level);
          const top = d.alerts[0];
          const Icon = hazardIcon(top?.hazard ?? "");
          return (
            <div
              key={d.date}
              className={cn("w-48 shrink-0 rounded-2xl border-2 p-4", s.soft)}
            >
              <p className="text-sm font-semibold text-slate-600">{dayLabel(d.date, todayIso)}</p>
              <Icon className={cn("my-2 h-9 w-9", s.text)} />
              <p
                className={cn(
                  "inline-block rounded-full px-2 py-0.5 text-xs font-bold",
                  LEVELS[d.highest_alert_level].solid
                )}
              >
                {s.label}
              </p>
              <p className="mt-2 line-clamp-2 text-sm font-medium text-slate-800">
                {top?.hazard ?? "Thời tiết xấu"}
              </p>
              <div className="mt-3 space-y-1 text-sm text-slate-600">
                <p className="flex items-center gap-1.5">
                  <CloudRain className="h-4 w-4" /> {d.weather_summary.total_rain.toFixed(0)} mm
                </p>
                <p className="flex items-center gap-1.5">
                  <Wind className="h-4 w-4" /> {d.weather_summary.max_wind_gust.toFixed(0)} km/h
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
