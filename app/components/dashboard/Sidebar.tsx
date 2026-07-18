"use client";

import { useState } from "react";

const menuGroups = [
  {
    label: "CẢNH BÁO",
    items: [
      { id: "canh-bao-hien-tai", icon: "bell", label: "Cảnh báo hiện tại" },
      { id: "du-bao-3-ngay", icon: "calendar", label: "Dự báo 3 ngày" },
      { id: "lich-su-canh-bao", icon: "clock", label: "Lịch sử cảnh báo" },
    ],
  },
  {
    label: "KHU VỰC",
    items: [
      { id: "ban-do-khu-vuc", icon: "map", label: "Bản đồ khu vực" },
      { id: "danh-sach-dia-phuong", icon: "list", label: "Danh sách địa phương" },
    ],
  },
  {
    label: "PHÁT THANH",
    items: [
      { id: "phat-thanh-tu-dong", icon: "radio", label: "Phát thanh tự động" },
      { id: "quan-ly-noi-dung", icon: "file-text", label: "Quản lý nội dung" },
    ],
  },
  {
    label: "HỆ THỐNG",
    items: [
      { id: "cai-dat", icon: "settings", label: "Cài đặt" },
      { id: "nguoi-dung", icon: "users", label: "Người dùng" },
      { id: "nhat-ky", icon: "activity", label: "Nhật ký hệ thống" },
    ],
  },
];

const iconMap: Record<string, React.ReactNode> = {
  bell: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    </svg>
  ),
  calendar: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  ),
  clock: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  map: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
    </svg>
  ),
  list: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
    </svg>
  ),
  radio: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
    </svg>
  ),
  "file-text": (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  settings: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  ),
  users: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  ),
  activity: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
  home: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  ),
};

interface SidebarProps {
  activeMenu: string;
  setActiveMenu: (id: string) => void;
}

export default function Sidebar({ activeMenu, setActiveMenu }: SidebarProps) {
  return (
    <aside className="w-56 bg-slate-800 text-white flex flex-col shrink-0 h-screen">
      {/* Logo */}
      <div className="px-4 py-4 border-b border-slate-700">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 bg-blue-500 rounded-lg flex items-center justify-center shrink-0">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <p className="text-xs font-bold leading-tight text-white">CẢNH BÁO THỜI TIẾT</p>
            <p className="text-xs text-blue-300 leading-tight">TỈNH ĐIỆN BIÊN</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        {/* Tổng quan */}
        <button
          id="menu-tong-quan"
          onClick={() => setActiveMenu("tong-quan")}
          className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg mb-3 text-sm font-medium transition-all ${
            activeMenu === "tong-quan"
              ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
              : "text-slate-300 hover:bg-slate-700 hover:text-white"
          }`}
        >
          {iconMap.home}
          <span>Tổng quan</span>
        </button>

        {menuGroups.map((group) => (
          <div key={group.label} className="mb-4">
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider px-3 mb-1.5">
              {group.label}
            </p>
            {group.items.map((item) => (
              <button
                key={item.id}
                id={`menu-${item.id}`}
                onClick={() => setActiveMenu(item.id)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg mb-0.5 text-sm transition-all ${
                  activeMenu === item.id
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
                    : "text-slate-400 hover:bg-slate-700 hover:text-white"
                }`}
              >
                {iconMap[item.icon]}
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>

      {/* Bottom user badges */}
      <div className="px-4 py-3 border-t border-slate-700 flex items-center gap-2">
        <div className="w-7 h-7 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold text-white">VI</div>
        <div className="w-7 h-7 rounded-full bg-slate-600 flex items-center justify-center text-xs font-bold text-slate-300">TH</div>
        <div className="w-7 h-7 rounded-full bg-slate-600 flex items-center justify-center text-xs font-bold text-slate-300">HM</div>
      </div>
    </aside>
  );
}
