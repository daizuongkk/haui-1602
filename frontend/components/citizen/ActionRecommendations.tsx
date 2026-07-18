import { Check, X } from "lucide-react";
import { Card } from "@/components/ui/primitives";
import { safetyAdvice } from "@/lib/hazards";
import type { AlertRecord } from "@/lib/types";

// Khối "cần làm ngay" — luôn hiển thị, không cần bấm.
export function ActionRecommendations({ record }: { record: AlertRecord | null }) {
  if (!record || record.alerts.length === 0) return null;
  const advice = safetyAdvice(record.alerts.map((a) => a.hazard));

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card className="border-green-200 p-5">
        <h3 className="mb-3 flex items-center gap-2 text-lg font-bold text-green-800">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-green-600 text-white">
            <Check className="h-4 w-4" />
          </span>
          Nên làm
        </h3>
        <ul className="space-y-2.5">
          {advice.do.map((a) => (
            <li key={a} className="flex items-start gap-2 text-slate-700">
              <Check className="mt-0.5 h-5 w-5 shrink-0 text-green-600" />
              <span>{a}</span>
            </li>
          ))}
        </ul>
      </Card>

      <Card className="border-red-200 p-5">
        <h3 className="mb-3 flex items-center gap-2 text-lg font-bold text-red-800">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-red-600 text-white">
            <X className="h-4 w-4" />
          </span>
          Không nên làm
        </h3>
        <ul className="space-y-2.5">
          {advice.dont.map((a) => (
            <li key={a} className="flex items-start gap-2 text-slate-700">
              <X className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
              <span>{a}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
