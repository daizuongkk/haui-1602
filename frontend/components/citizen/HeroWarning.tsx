import { Clock, MapPin } from "lucide-react";
import { levelStyle } from "@/lib/levels";
import { hazardIcon } from "@/lib/hazards";
import { cn } from "@/lib/utils";
import { LevelBadge } from "@/components/common/LevelBadge";
import type { AlertRecord } from "@/lib/types";

// Khối cảnh báo chính — chiếm phần lớn màn hình đầu tiên.
export function HeroWarning({ record, locationName }: { record: AlertRecord | null; locationName: string }) {
  if (!record) {
    const s = levelStyle("Green");
    const Icon = s.icon;
    return (
      <section className={cn("rounded-3xl border-2 p-6 sm:p-8", s.soft)}>
        <div className="flex items-center gap-2 text-slate-600">
          <MapPin className="h-5 w-5" />
          <span className="text-lg font-bold uppercase tracking-wide">{locationName}</span>
        </div>
        <div className="mt-4 flex items-center gap-4">
          <Icon className="h-14 w-14 text-green-600" />
          <div>
            <p className="text-2xl font-extrabold text-green-800">Không có cảnh báo</p>
            <p className="text-green-700">Thời tiết trong ngưỡng an toàn. Sinh hoạt bình thường.</p>
          </div>
        </div>
      </section>
    );
  }

  const s = levelStyle(record.highest_alert_level);
  const top = record.alerts[0];
  const HazardIcon = hazardIcon(top?.hazard ?? "");
  const isRed = record.highest_alert_level === "Red";

  return (
    <section
      className={cn(
        "rounded-3xl border-2 p-6 sm:p-8",
        s.soft,
        isRed && "animate-pulse-glow"
      )}
    >
      <div className="flex items-center gap-2 text-slate-600">
        <MapPin className="h-5 w-5" />
        <span className="text-lg font-bold uppercase tracking-wide">{record.location}</span>
      </div>

      <div className="mt-4 flex items-start gap-4 sm:gap-6">
        <HazardIcon className={cn("h-16 w-16 shrink-0 sm:h-20 sm:w-20", s.text)} />
        <div className="space-y-2">
          <h1 className="text-2xl font-extrabold uppercase leading-tight text-slate-900 sm:text-3xl">
            Cảnh báo {top?.hazard ?? "thiên tai"}
          </h1>
          <LevelBadge level={record.highest_alert_level} size="lg" />
          <p className="flex items-center gap-1.5 text-sm text-slate-600">
            <Clock className="h-4 w-4" /> Ngày {record.date}
          </p>
        </div>
      </div>

      {top?.description && (
        <p className="mt-5 text-lg font-medium leading-relaxed text-slate-800">{top.description}</p>
      )}
    </section>
  );
}
