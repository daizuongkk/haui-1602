"use client";
import Link from "next/link";
import { ShieldAlert, LayoutDashboard } from "lucide-react";
import { LanguageSelector } from "@/components/common/LanguageSelector";
import { LocationSelector } from "@/components/common/LocationSelector";
import type { LocationOut } from "@/lib/types";

export function CitizenHeader({
  locations,
  locationId,
  onLocationChange,
}: {
  locations: LocationOut[];
  locationId: string;
  onLocationChange: (id: string) => void;
}) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-3 px-4 py-3">
        <Link href="/" className="flex items-center gap-2 font-extrabold text-slate-900">
          <ShieldAlert className="h-7 w-7 text-red-600" />
          <span className="leading-tight">
            Cảnh báo thiên tai
            <span className="block text-xs font-medium text-slate-500">Tỉnh Điện Biên</span>
          </span>
        </Link>
        <div className="ml-auto flex flex-wrap items-center gap-2">
          {locations.length > 0 && (
            <LocationSelector locations={locations} value={locationId} onChange={onLocationChange} />
          )}
          <LanguageSelector />
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
          >
            <LayoutDashboard className="h-4 w-4" />
            <span className="hidden sm:inline">Cán bộ</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
