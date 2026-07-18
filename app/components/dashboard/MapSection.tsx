"use client";

import { useState } from "react";

const areas = [
  { id: "muong-cha", name: "Huyện Mường Chà", x: "28%", y: "35%", level: 1, color: "#f59e0b" },
  { id: "tuan-giao", name: "Huyện Tuấn Giáo", x: "62%", y: "42%", level: 3, color: "#ef4444" },
  { id: "dien-bien-phu", name: "TP. Điện Biên Phủ", x: "48%", y: "68%", level: 2, color: "#f97316" },
];

const levelColors: Record<number, string> = {
  0: "#22c55e",
  1: "#eab308",
  2: "#f97316",
  3: "#ef4444",
  4: "#a855f7",
};

const levelLabels: Record<number, string> = {
  0: "Không có nguy cơ",
  1: "Cấp 1 – Thấp",
  2: "Cấp 2 – Trung bình",
  3: "Cấp 3 – Cao",
  4: "Cấp 4 – Rất cao",
};

export default function MapSection() {
  const [hoveredArea, setHoveredArea] = useState<string | null>(null);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Title bar */}
      <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
        <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        <h2 className="font-semibold text-gray-800 text-sm">BẢN ĐỒ CẢNH BÁO ĐIỆN BIÊN</h2>
      </div>

      {/* Map body */}
      <div className="relative bg-gradient-to-br from-slate-100 to-blue-50" style={{ height: "220px" }}>
        {/* Terrain background */}
        <div className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Cpath d='M0 30 Q15 10 30 30 Q45 50 60 30' stroke='%2394a3b8' fill='none' stroke-width='1'/%3E%3C/svg%3E")`,
          }}
        />

        {/* Province shape SVG */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 600 260" preserveAspectRatio="xMidYMid meet">
          {/* Tuần Giáo - Red level 3 */}
          <ellipse cx="380" cy="110" rx="130" ry="75" fill="#ef444488" stroke="#ef4444" strokeWidth="1.5" />
          {/* TP. Điện Biên Phủ - Orange level 2 */}
          <ellipse cx="290" cy="175" rx="100" ry="60" fill="#f9731688" stroke="#f97316" strokeWidth="1.5" />
          {/* Mường Chà - Yellow level 1 */}
          <ellipse cx="165" cy="95" rx="110" ry="70" fill="#eab30888" stroke="#eab308" strokeWidth="1.5" />
          {/* Border label */}
          <text x="38" y="200" fontSize="11" fill="#94a3b8" fontFamily="sans-serif">LÀO</text>
        </svg>

        {/* Map controls */}
        <div className="absolute top-3 left-3 flex flex-col gap-1 z-10">
          <button id="map-zoom-in" className="w-7 h-7 bg-white rounded shadow text-gray-600 flex items-center justify-center hover:bg-gray-50 font-bold text-lg leading-none">+</button>
          <button id="map-zoom-out" className="w-7 h-7 bg-white rounded shadow text-gray-600 flex items-center justify-center hover:bg-gray-50 font-bold text-lg leading-none">−</button>
          <button id="map-layers" className="w-7 h-7 bg-white rounded shadow text-gray-600 flex items-center justify-center hover:bg-gray-50">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
            </svg>
          </button>
        </div>

        {/* Area pins */}
        {areas.map((area) => (
          <button
            key={area.id}
            id={`map-pin-${area.id}`}
            className="absolute transform -translate-x-1/2 -translate-y-1/2 group z-10"
            style={{ left: area.x, top: area.y }}
            onMouseEnter={() => setHoveredArea(area.id)}
            onMouseLeave={() => setHoveredArea(null)}
          >
            <div
              className="flex items-center gap-1.5 bg-white/90 backdrop-blur-sm border rounded-full px-2.5 py-1 shadow-lg cursor-pointer transition-all group-hover:scale-105"
              style={{ borderColor: area.color }}
            >
              <svg className="w-3.5 h-3.5" fill={area.color} viewBox="0 0 24 24">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" />
              </svg>
              <span className="text-xs font-medium text-gray-700 whitespace-nowrap">{area.name}</span>
            </div>
          </button>
        ))}

        {/* Legend */}
        <div className="absolute bottom-3 right-3 bg-white/90 backdrop-blur-sm rounded-lg p-2 shadow border border-gray-100 z-10">
          <p className="text-[10px] font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">Chú thích mức cảnh báo</p>
          {Object.entries(levelLabels).map(([level, label]) => (
            <div key={level} className="flex items-center gap-1.5 mb-1">
              <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: levelColors[Number(level)] }} />
              <span className="text-[10px] text-gray-600">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
