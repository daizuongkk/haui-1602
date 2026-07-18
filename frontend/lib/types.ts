// Mirror các DTO của backend (backend/presentation/api/schemas.py).
// Giữ đồng bộ với API — đây là hợp đồng dữ liệu.

export type AlertLevel = "Green" | "Yellow" | "Orange" | "Red";
export type Language = "vi" | "thai" | "hmong";
export type BroadcastChannel = "sms" | "zalo" | "loudspeaker";

export interface LocationOut {
  id: string;
  name: string;
  lat: number;
  lon: number;
  real_elevation: number;
  landslide_risk_factor: number;
}

export interface DistrictSummary {
  location_id: string;
  location: string;
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

export interface HazardAlertOut {
  hazard: string;
  level: AlertLevel;
  description: string;
}

export interface AlertRecord {
  location: string;
  location_id: string;
  latitude: number;
  longitude: number;
  elevation: number;
  date: string; // dd/mm/yyyy
  highest_alert_level: AlertLevel;
  weather_summary: WeatherSummary;
  alerts: HazardAlertOut[];
  messages: Partial<Record<Language, string>>;
  audio: Partial<Record<Language, string>>;
  has_translation: boolean;
}

export interface BroadcastResponse {
  location: string;
  date: string;
  highest_alert_level: AlertLevel;
  level_label: string;
  channels: {
    sms?: { to: string; text: string; length: number };
    zalo?: {
      type: string;
      to: string;
      title: string;
      subtitle: string;
      body: string;
      audio?: string | null;
    };
    loudspeaker?: {
      type: string;
      to: string;
      instructions: string;
      audio: Partial<Record<Language, string | null>>;
      has_translation: boolean;
    };
  };
  simulated: boolean;
}
