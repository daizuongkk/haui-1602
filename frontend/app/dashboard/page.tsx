"use client";
import { AlertTriangle, Siren, ClipboardCheck, LifeBuoy } from "lucide-react";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { DashboardTopbar } from "@/components/dashboard/DashboardTopbar";
import { KPICard } from "@/components/dashboard/KPICard";
import { AIWarningCenter } from "@/components/dashboard/AIWarningCenter";
import { GoogleRiskMap } from "@/components/common/GoogleRiskMap";
import { OfficerSelector } from "@/components/common/OfficerSelector";
import { ErrorState, LoadingCards } from "@/components/common/States";

export default function DashboardOverview() {
  const { data: summary, loading: sLoad, error: sErr } = useApi(api.summary);
  const { data: alerts } = useApi(api.activeAlerts);
  const { data: overview } = useApi(api.overview);

  return (
    <>
      <DashboardTopbar title="Tổng quan toàn tỉnh" right={<OfficerSelector />} />
      <div className="space-y-5 p-5">
        {sErr ? (
          <ErrorState message={sErr} />
        ) : sLoad ? (
          <LoadingCards count={4} />
        ) : (
          <>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <KPICard label="Xã đang cảnh báo" value={overview?.communes_at_risk ?? 0} icon={AlertTriangle} accent="text-orange-500" />
              <KPICard label="Mức đỏ" value={overview?.level_counts?.Red ?? 0} icon={Siren} accent="text-red-600" />
              <KPICard label="Chờ phê duyệt" value={overview?.pending_approval ?? 0} icon={ClipboardCheck} accent="text-indigo-500" />
              <KPICard label="Cần hỗ trợ" value={overview?.need_help ?? 0} icon={LifeBuoy} accent="text-red-700" />
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <div className="rounded-2xl border border-slate-200 bg-white p-4">
                  <h2 className="mb-3 font-bold text-slate-900">Bản đồ nguy cơ</h2>
                  <GoogleRiskMap districts={summary?.districts ?? []} height={460} />
                </div>
              </div>
              <div className="lg:col-span-1 lg:max-h-[560px]">
                <AIWarningCenter alerts={alerts ?? []} />
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
