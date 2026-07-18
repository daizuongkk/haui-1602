"use client";

const actions = [
  {
    id: "action-view-map",
    label: "Xem chi tiết khu vực",
    icon: "map",
    color: "from-blue-500 to-blue-600",
    lightBg: "bg-blue-50 hover:bg-blue-100",
    textColor: "text-blue-700",
    iconColor: "text-blue-500",
  },
  {
    id: "action-broadcast",
    label: "Phát thanh ngay",
    icon: "radio",
    color: "from-green-500 to-green-600",
    lightBg: "bg-green-50 hover:bg-green-100",
    textColor: "text-green-700",
    iconColor: "text-green-500",
  },
  {
    id: "action-new-bulletin",
    label: "Tạo bản tin mới",
    icon: "file-plus",
    color: "from-purple-500 to-purple-600",
    lightBg: "bg-purple-50 hover:bg-purple-100",
    textColor: "text-purple-700",
    iconColor: "text-purple-500",
  },
  {
    id: "action-quick-report",
    label: "Báo cáo nhanh",
    icon: "bar-chart",
    color: "from-orange-500 to-orange-600",
    lightBg: "bg-orange-50 hover:bg-orange-100",
    textColor: "text-orange-700",
    iconColor: "text-orange-500",
  },
];

const icons: Record<string, React.ReactNode> = {
  map: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
    </svg>
  ),
  radio: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
    </svg>
  ),
  "file-plus": (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  "bar-chart": (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
};

export default function QuickActions() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
        <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <h2 className="font-semibold text-gray-800 text-sm">THAO TÁC NHANH</h2>
      </div>

      {/* Action buttons */}
      <div className="p-3 grid grid-cols-2 gap-2">
        {actions.map((action) => (
          <button
            key={action.id}
            id={action.id}
            className={`flex items-center gap-2 p-2.5 rounded-lg ${action.lightBg} border border-transparent hover:border-current transition-all group`}
          >
            <div className={`${action.iconColor} shrink-0`}>
              {icons[action.icon]}
            </div>
            <span className={`text-xs font-medium ${action.textColor} text-left leading-tight`}>
              {action.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
