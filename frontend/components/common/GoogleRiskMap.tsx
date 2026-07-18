"use client";
import { useState, useEffect } from "react";
import { levelStyle } from "@/lib/levels";
import type { DistrictSummary } from "@/lib/types";
import { RiskLegend } from "./RiskLegend";
import { LevelBadge } from "./LevelBadge";

const DIEN_BIEN_CENTER: [number, number] = [21.85, 103.0];

export function GoogleRiskMap({
  districts,
  height = 420,
  onSelect,
}: {
  districts: DistrictSummary[];
  height?: number;
  onSelect?: (d: DistrictSummary) => void;
}) {
  const [mapReady, setMapReady] = useState(false);
  const [active, setActive] = useState<DistrictSummary | null>(null);

  useEffect(() => {
    // Dynamically load Leaflet CSS and JS (only once)
    if (typeof window === "undefined") return;
    if ((window as any).__leafletLoaded) {
      setMapReady(true);
      return;
    }

    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
    document.head.appendChild(link);

    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.onload = () => {
      (window as any).__leafletLoaded = true;
      setMapReady(true);
    };
    document.head.appendChild(script);
  }, []);

  useEffect(() => {
    if (!mapReady || typeof window === "undefined") return;
    const L = (window as any).L;
    if (!L) return;

    const container = document.getElementById("leaflet-risk-map");
    if (!container) return;

    // Clean up previous map instance
    if ((container as any)._leafletMap) {
      try {
        (container as any)._leafletMap.remove();
      } catch (err) {
        console.warn("Leaflet cleanup error:", err);
      }
      (container as any)._leafletMap = null;
    }

    // Force remove Leaflet container ID to prevent "Map container is being reused by another instance"
    if ((container as any)._leaflet_id) {
      delete (container as any)._leaflet_id;
      container.innerHTML = "";
    }

    const map = L.map(container, {
      zoomControl: true,
      attributionControl: true,
    }).setView(DIEN_BIEN_CENTER, 9);

    (container as any)._leafletMap = map;

    // OpenStreetMap tile layer (100% miễn phí)
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    // Add markers for each district
    districts.forEach((d) => {
      const s = levelStyle(d.highest_alert_level);
      const isGreen = d.highest_alert_level === "Green";
      const radius = isGreen ? 9 : 14;

      const marker = L.circleMarker([d.latitude, d.longitude], {
        radius,
        fillColor: s.hex,
        fillOpacity: 0.9,
        color: "#ffffff",
        weight: 2,
      }).addTo(map);

      // Pulse animation for non-green markers
      if (!isGreen) {
        const pulseMarker = L.circleMarker([d.latitude, d.longitude], {
          radius: radius + 6,
          fillColor: s.hex,
          fillOpacity: 0.3,
          color: s.hex,
          weight: 1,
        }).addTo(map);
      }

      // Popup with district info
      const popupContent = `
        <div style="min-width:160px;font-family:system-ui,sans-serif;">
          <p style="font-weight:700;font-size:14px;margin:0 0 4px;color:#1e293b">${d.location}</p>
          <span style="display:inline-block;padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:600;color:#fff;background:${s.hex}">
            ${s.hex === "#16a34a" ? "Bình thường" : s.hex === "#eab308" ? "Chú ý" : s.hex === "#f97316" ? "Nguy hiểm" : "Cực kỳ nguy hiểm"}
          </span>
          <p style="font-size:11px;color:#64748b;margin:4px 0 0">Độ cao ${d.elevation} m</p>
        </div>
      `;

      marker.bindPopup(popupContent);
      marker.on("click", () => {
        onSelect?.(d);
      });
    });

    return () => {
      map.remove();
    };
  }, [mapReady, districts, onSelect]);

  if (!mapReady) {
    return (
      <div className="animate-pulse rounded-2xl bg-slate-200" style={{ height }} aria-label="Đang tải bản đồ" />
    );
  }

  return (
    <div className="space-y-2">
      <div id="leaflet-risk-map" style={{ width: "100%", height, borderRadius: "1rem", overflow: "hidden" }} />
      <RiskLegend />
    </div>
  );
}
