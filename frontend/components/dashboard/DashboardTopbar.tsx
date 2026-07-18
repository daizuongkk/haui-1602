"use client";
import { CircleUser, Radio } from "lucide-react";

export function DashboardTopbar({ title, right }: { title: string; right?: React.ReactNode }) {
  return (
    <header className="flex flex-wrap items-center gap-3 border-b border-slate-200 bg-white px-5 py-3">
      <div className="flex items-center gap-2 lg:hidden">
        <Radio className="h-6 w-6 text-red-600" />
        <span className="font-extrabold text-slate-900">Điều hành</span>
      </div>
      <h1 className="text-lg font-bold text-slate-900">{title}</h1>
      <div className="ml-auto flex items-center gap-3">
        {right}
        <span className="flex items-center gap-2 rounded-xl bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700">
          <CircleUser className="h-5 w-5 text-slate-500" />
          Cán bộ trực ban
        </span>
      </div>
    </header>
  );
}
