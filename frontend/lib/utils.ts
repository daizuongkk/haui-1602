import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// dd/mm/yyyy -> key sắp xếp (yyyymmdd) để so sánh ngày.
export function dateSortKey(d: string): string {
  const [dd, mm, yyyy] = d.split("/");
  return `${yyyy}${mm}${dd}`;
}

// dd/mm/yyyy -> "Thứ ..., dd/mm" cho hiển thị.
const WEEKDAYS = ["Chủ nhật", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"];
export function dayLabel(d: string, todayIso?: string): string {
  const [dd, mm, yyyy] = d.split("/").map(Number);
  const date = new Date(yyyy, mm - 1, dd);
  const iso = `${yyyy}-${String(mm).padStart(2, "0")}-${String(dd).padStart(2, "0")}`;
  if (todayIso && iso === todayIso) return "Hôm nay";
  return `${WEEKDAYS[date.getDay()]}, ${String(dd).padStart(2, "0")}/${String(mm).padStart(2, "0")}`;
}
