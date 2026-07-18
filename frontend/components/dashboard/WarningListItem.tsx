"use client";
import { ChevronRight, Clock } from "lucide-react";
import { levelStyle } from "@/lib/levels";
import { hazardIcon } from "@/lib/hazards";
import { cn } from "@/lib/utils";
import { LevelBadge } from "@/components/common/LevelBadge";
import type { AlertRecord } from "@/lib/types";

export function WarningListItem({
  record,
  selected,
  onClick,
}: {
  record: AlertRecord;
  selected?: boolean;
  onClick?: () => void;
}) {
  const s = levelStyle(record.highest_alert_level);
  const top = record.alerts[0];
  const Icon = hazardIcon(top?.hazard ?? "");
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex w-full items-start gap-3 rounded-xl border p-3 text-left transition-colors",
        selected ? "border-slate-900 bg-slate-50 ring-1 ring-slate-900" : "border-slate-200 hover:bg-slate-50"
      )}
    >
      <span className={cn("mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg", s.soft)}>
        <Icon className={cn("h-5 w-5", s.text)} />
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-bold text-slate-900">{record.location}</span>
          <LevelBadge level={record.highest_alert_level} size="sm" />
        </div>
        <p className="mt-0.5 truncate text-sm font-medium text-slate-700">{top?.hazard}</p>
        <p className="mt-0.5 flex items-center gap-1 text-xs text-slate-400">
          <Clock className="h-3 w-3" /> {record.date}
          {!record.has_translation && <span className="ml-1 text-amber-600">• chưa có bản dịch</span>}
        </p>
      </div>
      {onClick && <ChevronRight className="mt-3 h-4 w-4 shrink-0 text-slate-400" />}
    </button>
  );
}
