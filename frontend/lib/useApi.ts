"use client";
import { useEffect, useState } from "react";

// Hook fetch tối giản: trả về { data, loading, error } + refetch.
export function useApi<T>(fetcher: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    setError(null);
    fetcher()
      .then((d) => alive && setData(d))
      .catch((e) => alive && setError(e.message ?? "Lỗi tải dữ liệu"))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  return { data, loading, error, refetch: () => setTick((t) => t + 1) };
}
