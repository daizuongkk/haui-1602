"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { dateSortKey } from "@/lib/utils";
import type { AlertRecord } from "@/lib/types";
import { CitizenHeader } from "@/components/citizen/CitizenHeader";
import { HeroWarning } from "@/components/citizen/HeroWarning";
import { AIWarningBulletin } from "@/components/citizen/AIWarningBulletin";
import { ActionRecommendations } from "@/components/citizen/ActionRecommendations";
import { SimpleWeatherStats } from "@/components/citizen/SimpleWeatherStats";
import { SevenDayForecast } from "@/components/citizen/SevenDayForecast";
import { GoogleRiskMap } from "@/components/common/GoogleRiskMap";
import { ErrorState, LoadingCards } from "@/components/common/States";

export default function CitizenPage() {
  const { data: locations } = useApi(api.locations);
  const { data: summary } = useApi(api.summary);
  const [locId, setLocId] = useState("");

  useEffect(() => {
    if (!locId && locations?.length) setLocId(locations[0].id);
  }, [locations, locId]);

  const { data: days, loading, error } = useApi(
    () => (locId ? api.forecast(locId) : Promise.resolve([])),
    [locId]
  );

  const sorted = [...(days ?? [])].sort((a, b) => dateSortKey(a.date).localeCompare(dateSortKey(b.date)));
  const current: AlertRecord | null = sorted[0] ?? null;
  const locName = locations?.find((l) => l.id === locId)?.name ?? "Điện Biên";

  return (
    <div className="min-h-screen">
      <CitizenHeader locations={locations ?? []} locationId={locId} onLocationChange={setLocId} />

      <main className="mx-auto max-w-5xl space-y-6 px-4 py-6">
        {error ? (
          <ErrorState message={error} />
        ) : loading ? (
          <LoadingCards count={2} />
        ) : (
          <>
            <div className="grid gap-6 lg:grid-cols-2">
              <HeroWarning record={current} locationName={locName} />
              <AIWarningBulletin record={current} />
            </div>

            <ActionRecommendations record={current} />
            <SimpleWeatherStats record={current} />
            <SevenDayForecast days={sorted} />

            <section className="space-y-3">
              <h2 className="text-lg font-bold text-slate-900">Bản đồ nguy cơ toàn tỉnh</h2>
              <GoogleRiskMap districts={summary?.districts ?? []} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}
