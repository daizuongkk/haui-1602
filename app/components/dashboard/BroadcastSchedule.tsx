"use client";

const schedules = [
  {
    id: "sched-1",
    title: "Bản tin 08h00 - 19/07/2026",
    tags: ["VI", "TH", "HM"],
    time: "08:00",
    status: "done",
  },
  {
    id: "sched-2",
    title: "Bản tin 17h00 - 18/07/2026",
    tags: ["VI", "TH", "HM"],
    time: "17:00",
    status: "done",
  },
  {
    id: "sched-3",
    title: "Bản tin 08h00 - 18/07/2026",
    tags: ["VI", "TH", "HM"],
    time: "08:00",
    status: "done",
  },
];

const tagColors: Record<string, string> = {
  VI: "bg-blue-500 text-white",
  TH: "bg-emerald-500 text-white",
  HM: "bg-red-500 text-white",
};

export default function BroadcastSchedule() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
        <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h2 className="font-semibold text-gray-800 text-sm">LỊCH PHÁT THANH GẦN NHẤT</h2>
      </div>

      {/* Schedule list */}
      <div className="p-3 flex flex-col gap-2">
        {schedules.map((item) => (
          <div
            key={item.id}
            id={`schedule-item-${item.id}`}
            className="flex items-center gap-2.5 p-2 rounded-lg bg-gray-50 hover:bg-blue-50 transition-colors cursor-pointer border border-transparent hover:border-blue-100"
          >
            {/* Play icon */}
            <div className="w-7 h-7 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
              <svg className="w-3.5 h-3.5 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-700 truncate">{item.title}</p>
              <div className="flex items-center gap-1 mt-1">
                {item.tags.map((tag) => (
                  <span
                    key={tag}
                    className={`text-[10px] font-bold px-1.5 py-0.5 rounded-sm ${tagColors[tag] || "bg-gray-400 text-white"}`}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Time */}
            <span className="text-xs font-semibold text-gray-500 shrink-0">{item.time}</span>
          </div>
        ))}
      </div>

      {/* View all */}
      <div className="px-4 pb-3">
        <button id="btn-view-all-schedule" className="w-full text-center text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center justify-center gap-1">
          Xem tất cả
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}
