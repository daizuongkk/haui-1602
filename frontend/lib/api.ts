// Lớp gọi API — đường dẫn tương đối, Next.js rewrite sang backend FastAPI (:8000).
import type {
  AlertRecord,
  BroadcastChannel,
  BroadcastResponse,
  LocationOut,
  SummaryResponse,
} from "./types";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  locations: () => get<LocationOut[]>("/api/locations"),
  summary: () => get<SummaryResponse>("/api/summary"),
  activeAlerts: () => get<AlertRecord[]>("/api/alerts/active"),
  forecast: (locationId: string) => get<AlertRecord[]>(`/api/forecast/${locationId}`),
  broadcast: async (body: {
    location_id: string;
    date: string;
    channels: BroadcastChannel[];
  }): Promise<BroadcastResponse> => {
    const res = await fetch("/api/alerts/broadcast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`broadcast → ${res.status}`);
    return res.json();
  },
};
