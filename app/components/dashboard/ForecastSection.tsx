"use client";

const forecasts = [
  {
    id: "day-1",
    date: "19/07/2026",
    dayLabel: "Hôm nay",
    dayOfWeek: "",
    weatherIcon: "rainy",
    tempLow: "24°",
    tempHigh: "30°",
    description: "Mưa vừa, có nơi mưa to",
    level: 3,
    levelLabel: "Cấp 3",
    levelColor: "bg-red-500 text-white",
  },
  {
    id: "day-2",
    date: "20/07/2026",
    dayLabel: "Ngày mai",
    dayOfWeek: "",
    weatherIcon: "rainy-light",
    tempLow: "24°",
    tempHigh: "29°",
    description: "Mưa rào và dông",
    level: 2,
    levelLabel: "Cấp 2",
    levelColor: "bg-orange-500 text-white",
  },
  {
    id: "day-3",
    date: "21/07/2026",
    dayLabel: "Thứ 3",
    dayOfWeek: "",
    weatherIcon: "cloudy",
    tempLow: "23°",
    tempHigh: "31°",
    description: "Mây thay đổi",
    level: 1,
    levelLabel: "Cấp 1",
    levelColor: "bg-yellow-400 text-yellow-900",
  },
];

const WeatherIcon = ({ type }: { type: string }) => {
  if (type === "rainy") {
    return (
      <div className="relative w-10 h-10">
        <svg viewBox="0 0 48 48" className="w-full h-full">
          <ellipse cx="28" cy="20" rx="14" ry="11" fill="#64748b" />
          <ellipse cx="18" cy="24" rx="12" ry="10" fill="#94a3b8" />
          <ellipse cx="32" cy="26" rx="10" ry="8" fill="#94a3b8" />
          <line x1="14" y1="34" x2="11" y2="42" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" />
          <line x1="20" y1="34" x2="17" y2="42" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" />
          <line x1="26" y1="34" x2="23" y2="42" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" />
          <line x1="32" y1="34" x2="29" y2="42" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </div>
    );
  }
  if (type === "rainy-light") {
    return (
      <div className="relative w-10 h-10">
        <svg viewBox="0 0 48 48" className="w-full h-full">
          <ellipse cx="28" cy="22" rx="14" ry="11" fill="#94a3b8" />
          <ellipse cx="18" cy="26" rx="12" ry="10" fill="#cbd5e1" />
          <ellipse cx="32" cy="28" rx="10" ry="8" fill="#cbd5e1" />
          <line x1="17" y1="36" x2="15" y2="42" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" />
          <line x1="23" y1="36" x2="21" y2="42" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" />
          <line x1="29" y1="36" x2="27" y2="42" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </div>
    );
  }
  return (
    <div className="relative w-10 h-10">
      <svg viewBox="0 0 48 48" className="w-full h-full">
        <circle cx="28" cy="18" r="9" fill="#fbbf24" />
        <ellipse cx="22" cy="28" rx="14" ry="10" fill="#e2e8f0" />
        <ellipse cx="32" cy="30" rx="12" ry="9" fill="#f1f5f9" />
      </svg>
    </div>
  );
};

export default function ForecastSection() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
          </svg>
          <h2 className="font-semibold text-gray-800 text-sm">DỰ BÁO 3 NGÀY TỚI (TOÀN TỈNH)</h2>
        </div>
        <button id="btn-forecast-detail" className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1 font-medium">
          Xem chi tiết dự báo
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Forecast Cards */}
      <div className="p-4 grid grid-cols-3 gap-3">
        {forecasts.map((day) => (
          <div
            key={day.id}
            id={`forecast-${day.id}`}
            className="rounded-xl bg-gradient-to-br from-sky-50 to-blue-50 border border-sky-100 p-3 hover:shadow-md transition-shadow cursor-pointer"
          >
            {/* Date */}
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-xs text-gray-400">{day.date}</p>
                <p className="text-sm font-semibold text-gray-700">{day.dayLabel}</p>
              </div>
              <WeatherIcon type={day.weatherIcon} />
            </div>

            {/* Temperature */}
            <div className="flex items-baseline gap-1 mb-1">
              <span className="text-xl font-bold text-gray-800">{day.tempLow}</span>
              <span className="text-gray-400 text-sm">/</span>
              <span className="text-base font-semibold text-orange-500">{day.tempHigh}</span>
            </div>

            {/* Description + level */}
            <p className="text-xs text-gray-500 mb-2">{day.description}</p>
            <div className="flex items-center gap-1.5">
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${day.levelColor}`}>
                {day.levelLabel}
              </span>
              <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
