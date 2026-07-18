// Mirror các DTO của backend (backend/presentation/api/schemas.py).
// Đơn vị vị trí là xã/cụm xã (commune). Giữ vài alias (location*/alerts) để các
// component cũ dùng lại mà không phải sửa nhiều — chuẩn hoá trong lib/api.ts.

export type AlertLevel = "Green" | "Yellow" | "Orange" | "Red";
export type Language = "vi" | "thai" | "hmong";
export type Channel = "sms" | "zalo" | "loudspeaker";
export type FeedbackKind = "received" | "safe" | "need_help";
export type AlertStatus =
  | "pending_approval"
  | "approved"
  | "rejected"
  | "distributed"
  | "closed";

export interface Commune {
  id: string;
  name: string;
  district_id: string;
  district_name: string;
  lat: number;
  lon: number;
  real_elevation: number;
  landslide_risk_factor: number;
}

export interface Officer {
  id: string;
  name: string;
  role: string;
}

export interface Hazard {
  hazard: string;
  level: AlertLevel;
  description: string;
}

export interface WeatherSummary {
  min_temp: number;
  max_temp: number;
  total_rain: number;
  max_rain_1h: number;
  max_wind_gust: number;
  max_cape: number;
  min_visibility: number;
  deep_soil_moisture: number;
}

// Bản ghi cảnh báo đã CHUẨN HOÁ (superset: field mới + alias tương thích).
export interface AlertRecord {
  id: number;
  commune_id: string;
  commune_name: string;
  district_id: string;
  district_name: string;
  location_id: string; // alias = commune_id
  location: string; // alias = commune_name
  latitude: number;
  longitude: number;
  elevation: number;
  date: string; // dd/mm/yyyy
  highest_alert_level: AlertLevel;
  status: AlertStatus;
  status_label: string;
  weather_summary: WeatherSummary;
  hazards: Hazard[];
  alerts: Hazard[]; // alias = hazards
  messages: Partial<Record<Language, string>>;
  audio: Partial<Record<Language, string>>;
  has_translation: boolean;
  approved_by?: string | null;
  approved_at?: string | null;
  rejected_reason?: string | null;
  note?: string | null;
  feedback_counts: Record<FeedbackKind, number>;
  dispatch_count: number;
}

export interface Dispatch {
  id: number;
  alert_id: number;
  channel: Channel;
  status: string; // sent_sim | failed
  payload: Record<string, unknown>;
  officer_id?: string | null;
  error?: string | null;
  created_at?: string | null;
}

export interface Feedback {
  id: number;
  alert_id: number;
  kind: FeedbackKind;
  kind_label: string;
  note?: string | null;
  contact?: string | null;
  created_at?: string | null;
}

export interface AlertDetail extends AlertRecord {
  dispatches: Dispatch[];
  feedback: Feedback[];
}

// Tổng quan bản đồ — giữ tên `districts` cho component cũ (thực chất là xã).
export interface DistrictSummary {
  location_id: string;
  location: string;
  district_name: string;
  latitude: number;
  longitude: number;
  elevation: number;
  highest_alert_level: AlertLevel;
  level_label: string;
}

export interface SummaryResponse {
  districts: DistrictSummary[];
  counts: Record<AlertLevel, number>;
}

export interface DashboardOverview {
  total_alerts: number;
  level_counts: Record<AlertLevel, number>;
  status_counts: Record<string, number>;
  pending_approval: number;
  distributed: number;
  communes_at_risk: number;
  need_help: number;
}
