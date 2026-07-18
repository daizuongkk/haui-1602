"use client";
import { MapPin } from "lucide-react";
import type { Commune } from "@/lib/types";

export function LocationSelector({
  locations,
  value,
  onChange,
}: {
  locations: Commune[];
  value: string;
  onChange: (id: string) => void;
}) {
  return (
    <label className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm">
      <MapPin className="h-4 w-4 text-slate-500" />
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="cursor-pointer bg-transparent font-medium outline-none"
        aria-label="Chọn địa điểm"
      >
        {locations.map((l) => (
          <option key={l.id} value={l.id}>
            {l.name}
          </option>
        ))}
      </select>
    </label>
  );
}
