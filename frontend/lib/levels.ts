import { AlertTriangle, ShieldCheck, ShieldAlert, Siren, type LucideIcon } from "lucide-react";
import type { AlertLevel } from "./types";

// Nguồn chân lý duy nhất cho 4 mức cảnh báo ở frontend.
// Nhãn khớp backend (backend/shared/alert_levels.py). Class Tailwind viết đủ
// nguyên chuỗi để không bị purge.

export interface LevelStyle {
  level: AlertLevel;
  label: string; // nhãn khớp backend
  short: string; // nhãn ngắn cho người dân
  priority: number;
  icon: LucideIcon;
  solid: string; // nền đặc (badge, chip)
  soft: string; // nền nhạt + viền (card cảnh báo)
  text: string;
  dot: string; // màu chấm/marker
  hex: string; // dùng cho Google Maps / chart
}

export const LEVELS: Record<AlertLevel, LevelStyle> = {
  Green: {
    level: "Green",
    label: "Bình thường",
    short: "An toàn",
    priority: 0,
    icon: ShieldCheck,
    solid: "bg-green-600 text-white",
    soft: "bg-green-50 border-green-400 text-green-800",
    text: "text-green-700",
    dot: "bg-green-500",
    hex: "#16a34a",
  },
  Yellow: {
    level: "Yellow",
    label: "Chú ý",
    short: "Cần chú ý",
    priority: 1,
    icon: AlertTriangle,
    solid: "bg-yellow-400 text-yellow-950",
    soft: "bg-yellow-50 border-yellow-400 text-yellow-800",
    text: "text-yellow-700",
    dot: "bg-yellow-400",
    hex: "#eab308",
  },
  Orange: {
    level: "Orange",
    label: "Nguy hiểm",
    short: "Nguy hiểm",
    priority: 2,
    icon: ShieldAlert,
    solid: "bg-orange-500 text-white",
    soft: "bg-orange-50 border-orange-500 text-orange-800",
    text: "text-orange-700",
    dot: "bg-orange-500",
    hex: "#f97316",
  },
  Red: {
    level: "Red",
    label: "Cực kỳ nguy hiểm",
    short: "Rất nguy hiểm",
    priority: 3,
    icon: Siren,
    solid: "bg-red-600 text-white",
    soft: "bg-red-50 border-red-600 text-red-800",
    text: "text-red-700",
    dot: "bg-red-600",
    hex: "#dc2626",
  },
};

export const LEVEL_ORDER: AlertLevel[] = ["Red", "Orange", "Yellow", "Green"];

export function levelStyle(level: AlertLevel): LevelStyle {
  return LEVELS[level] ?? LEVELS.Green;
}
