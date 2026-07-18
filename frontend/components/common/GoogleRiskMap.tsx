"use client";
import { useState } from "react";
import { GoogleMap, InfoWindowF, MarkerF, useJsApiLoader } from "@react-google-maps/api";
import { KeyRound } from "lucide-react";
import { levelStyle } from "@/lib/levels";
import type { DistrictSummary } from "@/lib/types";
import { RiskLegend } from "./RiskLegend";
import { LevelBadge } from "./LevelBadge";

const DIEN_BIEN_CENTER = { lat: 21.85, lng: 103.0 };
const API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || "";

export function GoogleRiskMap({
  districts,
  height = 420,
  onSelect,
}: {
  districts: DistrictSummary[];
  height?: number;
  onSelect?: (d: DistrictSummary) => void;
}) {
  const { isLoaded, loadError } = useJsApiLoader({
    id: "google-map-dienbien",
    googleMapsApiKey: API_KEY,
  });
  const [active, setActive] = useState<DistrictSummary | null>(null);

  if (!API_KEY || loadError) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-slate-500"
        style={{ height }}
      >
        <KeyRound className="h-8 w-8" />
        <p className="font-semibold">Bản đồ cần Google Maps API key</p>
        <p className="text-sm">
          Đặt <code className="rounded bg-slate-200 px-1">NEXT_PUBLIC_GOOGLE_MAPS_API_KEY</code> trong{" "}
          <code className="rounded bg-slate-200 px-1">.env.local</code> rồi khởi động lại.
        </p>
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div className="animate-pulse rounded-2xl bg-slate-200" style={{ height }} aria-label="Đang tải bản đồ" />
    );
  }

  return (
    <div className="space-y-2">
      <GoogleMap
        mapContainerStyle={{ width: "100%", height, borderRadius: "1rem" }}
        center={DIEN_BIEN_CENTER}
        zoom={9}
        options={{ streetViewControl: false, mapTypeControl: false, fullscreenControl: false }}
      >
        {districts.map((d) => {
          const s = levelStyle(d.highest_alert_level);
          return (
            <MarkerF
              key={d.location_id}
              position={{ lat: d.latitude, lng: d.longitude }}
              onClick={() => {
                setActive(d);
                onSelect?.(d);
              }}
              icon={{
                path: google.maps.SymbolPath.CIRCLE,
                scale: d.highest_alert_level === "Green" ? 9 : 13,
                fillColor: s.hex,
                fillOpacity: 0.9,
                strokeColor: "#ffffff",
                strokeWeight: 2,
              }}
            />
          );
        })}
        {active && (
          <InfoWindowF
            position={{ lat: active.latitude, lng: active.longitude }}
            onCloseClick={() => setActive(null)}
          >
            <div className="min-w-40 space-y-1">
              <p className="font-bold text-slate-900">{active.location}</p>
              <LevelBadge level={active.highest_alert_level} size="sm" />
              <p className="text-xs text-slate-500">Độ cao {active.elevation} m</p>
            </div>
          </InfoWindowF>
        )}
      </GoogleMap>
      <RiskLegend />
    </div>
  );
}
