import { Card } from "@/components/ui/primitives";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

export function KPICard({
  label,
  value,
  icon: Icon,
  accent = "text-slate-500",
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  accent?: string;
}) {
  return (
    <Card className="flex items-center gap-4 p-4">
      <span className={cn("flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100", accent)}>
        <Icon className="h-6 w-6" />
      </span>
      <div>
        <p className="text-2xl font-extrabold leading-none text-slate-900">{value}</p>
        <p className="mt-1 text-sm text-slate-500">{label}</p>
      </div>
    </Card>
  );
}
