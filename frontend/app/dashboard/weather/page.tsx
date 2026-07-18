"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { DashboardTopbar } from "@/components/dashboard/DashboardTopbar";
import { LocationSelector } from "@/components/common/LocationSelector";
import { WeatherCharts } from "@/components/dashboard/WeatherCharts";
import { ErrorState, LoadingCards } from "@/components/common/States";

export default function WeatherPage() {
  const { data: locations } = useApi(api.locations);
  const [locId, setLocId] = useState("");

  useEffect(() => {
    if (!locId && locations?.length) setLocId(locations[0].id);
  }, [locations, locId]);

  const { data: days, loading, error } = useApi(
    () => (locId ? api.forecast(locId) : Promise.resolve([])),
    [locId]
  );

  return (
    <>
      <DashboardTopbar
        title="Dữ liệu thời tiết"
        right={
          locations?.length ? (
            <LocationSelector locations={locations} value={locId} onChange={setLocId} />
          ) : null
        }
      />
      <div className="p-5">
        {error ? (
          <ErrorState message={error} />
        ) : loading ? (
          <LoadingCards count={3} />
        ) : (
          <WeatherCharts days={days ?? []} />
        )}
      </div>
    </>
  );
}
