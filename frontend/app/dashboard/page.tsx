"use client";
import { AlertTriangle, Siren, ShieldAlert, Bell } from "lucide-react";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { DashboardTopbar } from "@/components/dashboard/DashboardTopbar";
import { KPICard } from "@/components/dashboard/KPICard";
import { AIWarningCenter } from "@/components/dashboard/AIWarningCenter";
import { GoogleRiskMap } from "@/components/common/GoogleRiskMap";
import { ErrorState, LoadingCards } from "@/components/common/States";

export default function DashboardOverview() {
  const { data: summary, loading: sLoad, error: sErr } = useApi(api.summary);
  const { data: alerts } = useApi(api.activeAlerts);

  const counts = summary?.counts ?? { Green: 0, Yellow: 0, Orange: 0, Red: 0 };
  const warning = counts.Yellow + counts.Orange + counts.Red;

  return (
    <>
      <DashboardTopbar title="Tổng quan toàn tỉnh" />
      <div className="space-y-5 p-5">
        {sErr ? (
          <ErrorState message={sErr} />
        ) : sLoad ? (
          <LoadingCards count={4} />
        ) : (
          <>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <KPICard label="Huyện đang cảnh báo" value={warning} icon={AlertTriangle} accent="text-orange-500" />
              <KPICard label="Mức đỏ" value={counts.Red} icon={Siren} accent="text-red-600" />
              <KPICard label="Mức cam" value={counts.Orange} icon={ShieldAlert} accent="text-orange-600" />
              <KPICard label="Ngày có cảnh báo" value={alerts?.length ?? 0} icon={Bell} accent="text-indigo-500" />
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
