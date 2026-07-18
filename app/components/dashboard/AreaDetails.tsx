"use client";

const areas = [
  {
    id: "muong-cha",
    name: "Huyện Mường Chà",
    level: 1,
    levelLabel: "Cấp 1",
    levelColor: "bg-yellow-400 text-yellow-900",
    description: "Sương mù dày",
    icon: "⚠️",
    iconBg: "bg-yellow-100",
    stats: {
      temp: "24°C",
      humidity: "96%",
      rain: "0.2 mm",
    },
  },
  {
    id: "tuan-giao",
    name: "Huyện Tuấn Giáo",
    level: 3,
    levelLabel: "Cấp 3",
    levelColor: "bg-red-500 text-white",
    description: "Lũ quét, sạt lở đất",
    icon: "⚠️",
    iconBg: "bg-red-100",
    stats: {
      temp: "26°C",
      humidity: "92%",
      rain: "45.6 mm",
    },
  },
  {
    id: "dien-bien-phu",
    name: "TP. Điện Biên Phủ",
    level: 2,
    levelLabel: "Cấp 2",
    levelColor: "bg-orange-500 text-white",
    description: "Dông lốc, sét",
    icon: "⚠️",
    iconBg: "bg-orange-100",
    stats: {
      temp: "27°C",
      humidity: "88%",
      rain: "18.3 mm",
    },
  },
];

const levelBorderColor: Record<number, string> = {
  1: "border-yellow-300",
  2: "border-orange-400",
  3: "border-red-400",
};

const levelIconColor: Record<number, string> = {
  1: "text-yellow-500",
  2: "text-orange-500",
  3: "text-red-500",
};

export default function AreaDetails() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
        <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <h2 className="font-semibold text-gray-800 text-sm">CHI TIẾT KHU VỰC</h2>
      </div>

      {/* Area Cards */}
      <div className="p-4 grid grid-cols-3 gap-3">
        {areas.map((area) => (
          <div
            key={area.id}
            id={`area-card-${area.id}`}
            className={`border-2 ${levelBorderColor[area.level]} rounded-xl p-3 hover:shadow-md transition-shadow cursor-pointer`}
          >
            {/* Top row */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className={`w-7 h-7 ${area.iconBg} rounded-full flex items-center justify-center shrink-0`}>
                  <svg className={`w-4 h-4 ${levelIconColor[area.level]}`} fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L1 21h22L12 2zm0 3.5L20.5 19h-17L12 5.5zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z" />
                  </svg>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-800 leading-tight">{area.name}</p>
                  <p className="text-[11px] text-gray-500 mt-0.5">{area.description}</p>
                </div>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0 ml-1 ${area.levelColor}`}>
                {area.levelLabel}
              </span>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-1 mb-2.5">
              <div className="text-center">
                <p className="text-[10px] text-gray-400">Nhiệt độ</p>
                <p className="text-xs font-semibold text-gray-700">{area.stats.temp}</p>
              </div>
              <div className="text-center border-x border-gray-100">
                <p className="text-[10px] text-gray-400">Độ ẩm</p>
                <p className="text-xs font-semibold text-gray-700">{area.stats.humidity}</p>
              </div>
              <div className="text-center">
                <p className="text-[10px] text-gray-400">Mưa</p>
                <p className="text-xs font-semibold text-gray-700">{area.stats.rain}</p>
              </div>
            </div>

            {/* View detail link */}
            <button
              id={`btn-detail-${area.id}`}
              className="text-[11px] text-blue-600 hover:text-blue-700 flex items-center gap-1 font-medium"
            >
              Xem chi tiết
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
