"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Radio, LineChart, ShieldAlert, Users } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Tổng quan", icon: LayoutDashboard },
  { href: "/dashboard/broadcast", label: "Phát cảnh báo", icon: Radio },
  { href: "/dashboard/weather", label: "Dữ liệu thời tiết", icon: LineChart },
];

export function DashboardSidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-slate-800 bg-slate-900 text-slate-300 lg:flex">
      <Link href="/" className="flex items-center gap-2 border-b border-slate-800 px-5 py-4 font-extrabold text-white">
        <ShieldAlert className="h-7 w-7 text-red-500" />
        <span className="leading-tight text-sm">
          Trung tâm điều hành
          <span className="block text-xs font-medium text-slate-400">Cảnh báo thiên tai Điện Biên</span>
        </span>
      </Link>
      <nav className="flex flex-1 flex-col gap-1 p-3">
        {NAV.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                active ? "bg-slate-700 text-white" : "hover:bg-slate-800 hover:text-white"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <Link
        href="/citizen"
        className="flex items-center gap-2 border-t border-slate-800 px-5 py-4 text-sm text-slate-400 hover:text-white"
      >
        <Users className="h-4 w-4" />
        Giao diện người dân
      </Link>
    </aside>
  );
}
