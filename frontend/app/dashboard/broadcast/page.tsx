"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { dateSortKey } from "@/lib/utils";
import { LEVELS } from "@/lib/levels";
import { DashboardTopbar } from "@/components/dashboard/DashboardTopbar";
import { WarningListItem } from "@/components/dashboard/WarningListItem";
import { BroadcastCenter } from "@/components/dashboard/BroadcastCenter";
import { Card } from "@/components/ui/primitives";
import { EmptyState, ErrorState, LoadingCards } from "@/components/common/States";
import type { AlertRecord } from "@/lib/types";

function BroadcastInner() {
  const params = useSearchParams();
  const { data: alerts, loading, error } = useApi(api.activeAlerts);
  const [key, setKey] = useState<string | null>(null);

  const sorted = [...(alerts ?? [])].sort(
    (a, b) =>
      LEVELS[b.highest_alert_level].priority - LEVELS[a.highest_alert_level].priority ||
      dateSortKey(a.date).localeCompare(dateSortKey(b.date))
  );
  const recKey = (r: AlertRecord) => `${r.location_id}|${r.date}`;

  // Preselect từ query (?loc&date) hoặc mục đầu tiên.
  useEffect(() => {
    if (key || sorted.length === 0) return;
    const loc = params.get("loc");
    const date = params.get("date");
    const match = sorted.find((r) => r.location_id === loc && r.date === date);
    setKey(recKey(match ?? sorted[0]));
  }, [sorted, key, params]);

  const selected = sorted.find((r) => recKey(r) === key) ?? null;

  if (error) return <ErrorState message={error} />;
  if (loading) return <LoadingCards count={2} />;
  if (sorted.length === 0) return <EmptyState hint="Không có cảnh báo nào cần phát." />;

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card className="flex max-h-[75vh] flex-col p-3 lg:col-span-1">
        <p className="px-1 pb-2 text-sm font-semibold text-slate-600">Cảnh báo chờ xử lý</p>
        <div className="space-y-2 overflow-y-auto">
          {sorted.map((r) => (
            <WarningListItem
              key={recKey(r)}
              record={r}
              selected={recKey(r) === key}
              onClick={() => setKey(recKey(r))}
            />
          ))}
        </div>
      </Card>
      <div className="lg:col-span-2">{selected && <BroadcastCenter key={key} record={selected} />}</div>
    </div>
  );
}

export default function BroadcastPage() {
  return (
    <>
      <DashboardTopbar title="Trung tâm phát thông báo" />
      <div className="p-5">
        <Suspense fallback={<LoadingCards count={2} />}>
          <BroadcastInner />
        </Suspense>
      </div>
    </>
  );
}
