"use client";

const alerts = [
  {
    id: "alert-1",
    area: "Huyện Tuấn Giáo",
    description: "Nguy cơ lũ quét, sạt lở đất",
    time: "19/07/2026 08:15",
    level: 3,
    levelLabel: "Cấp 3",
    levelColor: "bg-red-500",
  },
  {
    id: "alert-2",
    area: "Thành phố Điện Biên Phủ",
    description: "Nguy cơ dông lốc, sét",
    time: "19/07/2026 08:10",
    level: 2,
    levelLabel: "Cấp 2",
    levelColor: "bg-orange-400",
  },
  {
    id: "alert-3",
    area: "Huyện Mường Chà",
    description: "Sương mù dày",
    time: "19/07/2026 07:50",
    level: 1,
    levelLabel: "Cấp 1",
    levelColor: "bg-yellow-400",
  },
];

const levelIconColor: Record<number, string> = {
  1: "text-yellow-500",
  2: "text-orange-500",
  3: "text-red-500",
};

const levelBgLight: Record<number, string> = {
  1: "bg-yellow-50 border-yellow-100",
  2: "bg-orange-50 border-orange-100",
  3: "bg-red-50 border-red-100",
};

export default function CurrentAlerts() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg className={`w-4 h-4 text-red-500`} fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L1 21h22L12 2zm0 3.5L20.5 19h-17L12 5.5zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z" />
          </svg>
          <h2 className="font-semibold text-gray-800 text-sm">CẢNH BÁO HIỆN TẠI</h2>
        </div>
        <span className="w-5 h-5 bg-red-500 rounded-full text-white text-xs flex items-center justify-center font-bold">3</span>
      </div>

      {/* Alert list */}
      <div className="p-3 flex flex-col gap-2">
        {alerts.map((alert) => (
          <button
            key={alert.id}
            id={`alert-item-${alert.id}`}
            className={`w-full text-left flex items-start gap-2.5 p-2.5 rounded-lg border ${levelBgLight[alert.level]} hover:shadow-sm transition-shadow`}
          >
            {/* Icon */}
            <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${
              alert.level === 3 ? "bg-red-100" : alert.level === 2 ? "bg-orange-100" : "bg-yellow-100"
            }`}>
              <svg className={`w-4 h-4 ${levelIconColor[alert.level]}`} fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L1 21h22L12 2zm0 3.5L20.5 19h-17L12 5.5zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z" />
              </svg>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-1 mb-0.5">
                <span className="text-xs font-semibold text-gray-800 truncate">{alert.area}</span>
                <span className={`text-[10px] font-bold text-white px-1.5 py-0.5 rounded-full shrink-0 ${alert.levelColor}`}>
                  {alert.levelLabel}
                </span>
              </div>
              <p className="text-[11px] text-gray-600">{alert.description}</p>
              <p className="text-[10px] text-gray-400 mt-0.5">{alert.time}</p>
            </div>

            {/* Arrow */}
            <svg className="w-3.5 h-3.5 text-gray-300 shrink-0 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        ))}
      </div>

      {/* View all */}
      <div className="px-4 pb-3">
        <button id="btn-view-all-alerts" className="w-full text-center text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center justify-center gap-1">
          Xem tất cả cảnh báo
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}
