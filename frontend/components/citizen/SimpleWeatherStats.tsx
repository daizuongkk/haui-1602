import { Thermometer, CloudRain, Wind, Droplets } from "lucide-react";
import { Card } from "@/components/ui/primitives";
import type { AlertRecord } from "@/lib/types";

// Chỉ hiển thị tối đa 4 chỉ số quan trọng, dễ đọc.
export function SimpleWeatherStats({ record }: { record: AlertRecord | null }) {
  if (!record) return null;
  const w = record.weather_summary;
  const stats = [
    { icon: Thermometer, label: "Nhiệt độ", value: `${w.min_temp.toFixed(0)}–${w.max_temp.toFixed(0)}°C`, color: "text-orange-500" },
    { icon: CloudRain, label: "Lượng mưa 24h", value: `${w.total_rain.toFixed(0)} mm`, color: "text-blue-500" },
    { icon: Wind, label: "Gió giật", value: `${w.max_wind_gust.toFixed(0)} km/h`, color: "text-cyan-600" },
    { icon: Droplets, label: "Độ ẩm đất", value: `${(w.deep_soil_moisture * 100).toFixed(0)}%`, color: "text-emerald-600" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map((s) => (
        <Card key={s.label} className="flex flex-col items-center gap-1 p-4 text-center">
          <s.icon className={`h-7 w-7 ${s.color}`} />
          <p className="text-xl font-extrabold text-slate-900">{s.value}</p>
          <p className="text-xs text-slate-500">{s.label}</p>
        </Card>
      ))}
    </div>
  );
}
