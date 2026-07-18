"use client";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "@/components/ui/primitives";
import { dateSortKey } from "@/lib/utils";
import type { AlertRecord } from "@/lib/types";

function toSeries(days: AlertRecord[]) {
  return [...days]
    .sort((a, b) => dateSortKey(a.date).localeCompare(dateSortKey(b.date)))
    .map((d) => ({
      date: d.date.slice(0, 5), // dd/mm
      rain: Math.round(d.weather_summary.total_rain),
      wind: Math.round(d.weather_summary.max_wind_gust),
      tmin: Math.round(d.weather_summary.min_temp),
      tmax: Math.round(d.weather_summary.max_temp),
    }));
}

export function WeatherCharts({ days }: { days: AlertRecord[] }) {
  const data = toSeries(days);
  if (data.length === 0) {
    return <p className="text-sm text-slate-500">Chưa có dữ liệu cho huyện này.</p>;
  }

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <ChartCard title="Lượng mưa 24h (mm)">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip />
          <Bar dataKey="rain" name="Mưa (mm)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ChartCard>

      <ChartCard title="Gió giật mạnh nhất (km/h)">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip />
          <Line dataKey="wind" name="Gió (km/h)" stroke="#0891b2" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ChartCard>

      <ChartCard title="Nhiệt độ (°C)">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip />
          <Line dataKey="tmax" name="Cao nhất" stroke="#f97316" strokeWidth={2} dot={{ r: 3 }} />
          <Line dataKey="tmin" name="Thấp nhất" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ChartCard>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactElement }) {
  return (
    <Card className="p-4">
      <h3 className="mb-3 font-semibold text-slate-800">{title}</h3>
      <ResponsiveContainer width="100%" height={240}>
        {children}
      </ResponsiveContainer>
    </Card>
  );
}
