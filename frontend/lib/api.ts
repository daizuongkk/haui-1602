// Lớp gọi API — đường dẫn tương đối, Next.js rewrite sang backend FastAPI (:8000).
// Chuẩn hoá dữ liệu cảnh báo về AlertRecord (thêm alias location*/alerts) để các
// component sẵn có dùng lại. Thao tác của cán bộ gắn header X-Officer-Id.
import type {
  AlertDetail,
  AlertRecord,
  AlertStatus,
  Channel,
  Commune,
  DashboardOverview,
  Dispatch,
  Feedback,
  FeedbackKind,
  Officer,
  SummaryResponse,
} from "./types";

const OFFICER_KEY = "dienbien.officerId";

export function getOfficerId(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(OFFICER_KEY) || "";
}
export function setOfficerId(id: string): void {
  if (typeof window !== "undefined") window.localStorage.setItem(OFFICER_KEY, id);
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const officer = getOfficerId();
  if (officer) headers["X-Officer-Id"] = officer;
  const res = await fetch(path, { cache: "no-store", ...init, headers: { ...headers, ...(init?.headers || {}) } });
  if (!res.ok) {
    let detail = `${res.status}`;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* giữ mã lỗi */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

/* eslint-disable @typescript-eslint/no-explicit-any */
function normalizeAlert(a: any): AlertRecord {
  return {
    ...a,
    location_id: a.commune_id,
    location: a.commune_name,
    alerts: a.hazards ?? [],
  };
}

export const api = {
  communes: () => req<Commune[]>("/api/communes"),
  locations: () => req<Commune[]>("/api/communes"),
  officers: () => req<Officer[]>("/api/officers"),

  summary: async (): Promise<SummaryResponse> => {
    const s = await req<any>("/api/summary");
    return {
      counts: s.counts,
      districts: s.communes.map((c: any) => ({
        location_id: c.commune_id,
        location: c.commune_name,
        district_name: c.district_name,
        latitude: c.latitude,
        longitude: c.longitude,
        elevation: c.elevation,
        highest_alert_level: c.highest_alert_level,
        level_label: c.level_label,
      })),
    };
  },

  overview: () => req<DashboardOverview>("/api/dashboard/overview"),

  alerts: async (params: { status?: AlertStatus; commune_id?: string } = {}): Promise<AlertRecord[]> => {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    const list = await req<any[]>(`/api/alerts${qs ? `?${qs}` : ""}`);
    return list.map(normalizeAlert);
  },
  // Tương thích: dashboard cũ dùng activeAlerts() cho danh sách cảnh báo.
  activeAlerts: () => api.alerts(),

  alert: async (id: number): Promise<AlertDetail> => {
    const a = await req<any>(`/api/alerts/${id}`);
    return { ...normalizeAlert(a), dispatches: a.dispatches, feedback: a.feedback };
  },

  forecast: async (communeId: string): Promise<AlertRecord[]> => {
    const list = await req<any[]>(`/api/forecast/${communeId}`);
    return list.map(normalizeAlert);
  },

  approve: (id: number) => req<AlertRecord>(`/api/alerts/${id}/approve`, { method: "POST" }).then(normalizeAlert),
  reject: (id: number, reason: string) =>
    req<AlertRecord>(`/api/alerts/${id}/reject`, { method: "POST", body: JSON.stringify({ reason }) }).then(normalizeAlert),
  setStatus: (id: number, status: AlertStatus) =>
    req<AlertRecord>(`/api/alerts/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }).then(normalizeAlert),

  dispatch: (id: number, channels: Channel[]) =>
    req<{ alert: any; dispatches: Dispatch[] }>(`/api/alerts/${id}/dispatch`, {
      method: "POST",
      body: JSON.stringify({ channels }),
    }).then((r) => ({ alert: normalizeAlert(r.alert), dispatches: r.dispatches })),

  feedback: (id: number, body: { kind: FeedbackKind; note?: string; contact?: string }) =>
    req<Feedback>(`/api/alerts/${id}/feedback`, { method: "POST", body: JSON.stringify(body) }),
  listFeedback: (id: number) => req<Feedback[]>(`/api/alerts/${id}/feedback`),

  runPipeline: (body: { do_translate?: boolean; do_tts?: boolean } = {}) =>
    req<Record<string, number>>("/api/pipeline/run", { method: "POST", body: JSON.stringify(body) }),
};
