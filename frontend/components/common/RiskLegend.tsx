import { LEVEL_ORDER, LEVELS } from "@/lib/levels";
import { cn } from "@/lib/utils";

export function RiskLegend({ className }: { className?: string }) {
  return (
    <div className={cn("flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs", className)}>
      {LEVEL_ORDER.map((lv) => {
        const s = LEVELS[lv];
        return (
          <span key={lv} className="inline-flex items-center gap-1.5 text-slate-600">
            <span className={cn("h-3 w-3 rounded-full", s.dot)} />
            {s.label}
          </span>
        );
      })}
    </div>
  );
}
