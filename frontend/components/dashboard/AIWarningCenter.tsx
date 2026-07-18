"use client";
import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";
import { Card } from "@/components/ui/primitives";
import { EmptyState } from "@/components/common/States";
import { dateSortKey } from "@/lib/utils";
import { LEVELS } from "@/lib/levels";
import { WarningListItem } from "./WarningListItem";
import type { AlertRecord } from "@/lib/types";

// Danh sách cảnh báo AI phát hiện. Bấm một mục → sang trang phát cảnh báo.
export function AIWarningCenter({ alerts }: { alerts: AlertRecord[] }) {
  const router = useRouter();
  const sorted = [...alerts].sort(
    (a, b) =>
      LEVELS[b.highest_alert_level].priority - LEVELS[a.highest_alert_level].priority ||
      dateSortKey(a.date).localeCompare(dateSortKey(b.date))
  );

  return (
    <Card className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3">
        <Sparkles className="h-5 w-5 text-indigo-500" />
        <h2 className="font-bold text-slate-900">Cảnh báo AI</h2>
        <span className="ml-auto rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600">
          {sorted.length}
        </span>
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto p-3">
        {sorted.length === 0 ? (
          <EmptyState hint="Không có huyện nào đang ở mức cảnh báo." />
        ) : (
          sorted.map((r) => (
            <WarningListItem
              key={`${r.location_id}-${r.date}`}
              record={r}
              onClick={() => router.push(`/dashboard/broadcast?id=${r.id}`)}
            />
          ))
        )}
      </div>
    </Card>
  );
}
