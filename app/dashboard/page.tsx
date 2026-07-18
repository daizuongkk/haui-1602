"use client";

import { useState, useEffect } from "react";
import Sidebar from "../components/dashboard/Sidebar";
import Header from "../components/dashboard/Header";
import MapSection from "../components/dashboard/MapSection";
import AreaDetails from "../components/dashboard/AreaDetails";
import ForecastSection from "../components/dashboard/ForecastSection";
import CurrentAlerts from "../components/dashboard/CurrentAlerts";
import QuickActions from "../components/dashboard/QuickActions";
import BroadcastSchedule from "../components/dashboard/BroadcastSchedule";

export default function DashboardPage() {
  const [activeMenu, setActiveMenu] = useState("tong-quan");

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden font-sans">
      {/* Sidebar */}
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />

        {/* Page Content */}
        <div className="flex-1 overflow-auto bg-slate-100">
          <div className="flex gap-4 p-4 h-full">
            {/* Left & Center Content */}
            <div className="flex-1 flex flex-col gap-4 min-w-0">
              {/* Map Section */}
              <MapSection />
              {/* Area Details */}
              <AreaDetails />
              {/* Forecast */}
              <ForecastSection />
            </div>

            {/* Right Panel */}
            <div className="w-72 flex flex-col gap-4 shrink-0">
              <CurrentAlerts />
              <QuickActions />
              <BroadcastSchedule />
            </div>
          </div>

          {/* Footer */}
          <div className="px-4 pb-3 flex items-center gap-2 text-xs text-gray-400">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Dữ liệu được cập nhật lần cuối: 19/07/2026 08:30</span>
          </div>
        </div>
      </div>
    </div>
  );
}
