"use client";
import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { DashboardTopbar } from "@/components/dashboard/DashboardTopbar";
import { WarningListItem } from "@/components/dashboard/WarningListItem";
import { AlertOpsPanel } from "@/components/dashboard/AlertOpsPanel";
import { OfficerSelector } from "@/components/common/OfficerSelector";
import { Card } from "@/components/ui/primitives";
import { EmptyState, ErrorState, LoadingCards } from "@/components/common/States";
import type { AlertRecord } from "@/lib/types";

function BroadcastInner() {
  const params = useSearchParams();
  const [alerts, setAlerts] = useState<AlertRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);

  const refresh = useCallback(() => {
    api.alerts()
      .then((list) => {
        const actionable = list.filter((a) => a.status !== "closed");
        setAlerts(actionable);
        setSelected((cur) => cur ?? (Number(params.get("id")) || actionable[0]?.id || null));
      })
      .catch((e) => setError(e.message));
  }, [params]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (error) return <ErrorState message={error} />;
  if (!alerts) return <LoadingCards count={2} />;
  if (alerts.length === 0) return <EmptyState hint="Không có cảnh báo nào cần xử lý." />;

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card className="flex max-h-[78vh] flex-col p-3 lg:col-span-1">
        <p className="px-1 pb-2 text-sm font-semibold text-slate-600">Cảnh báo ({alerts.length})</p>
        <div className="space-y-2 overflow-y-auto">
          {alerts.map((r) => (
            <WarningListItem key={r.id} record={r} selected={r.id === selected} onClick={() => setSelected(r.id)} />
          ))}
        </div>
      </Card>
      <div className="lg:col-span-2">
        {selected != null && <AlertOpsPanel key={selected} alertId={selected} onChanged={refresh} />}
      </div>
    </div>
  );
}

export default function BroadcastPage() {
  return (
    <>
      <DashboardTopbar title="Trung tâm phê duyệt & phát cảnh báo" right={<OfficerSelector />} />
      <div className="p-5">
        <Suspense fallback={<LoadingCards count={2} />}>
          <BroadcastInner />
        </Suspense>
      </div>
    </>
  );
}
