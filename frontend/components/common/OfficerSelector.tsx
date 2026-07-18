"use client";
import { useEffect, useState } from "react";
import { UserCog } from "lucide-react";
import { api, getOfficerId, setOfficerId } from "@/lib/api";
import type { Officer } from "@/lib/types";

// Chọn danh tính cán bộ (xác thực nhẹ) — lưu vào localStorage, gắn header X-Officer-Id.
export function OfficerSelector({ onChange }: { onChange?: (id: string) => void }) {
  const [officers, setOfficers] = useState<Officer[]>([]);
  const [current, setCurrent] = useState("");

  useEffect(() => {
    api.officers().then((list) => {
      setOfficers(list);
      const saved = getOfficerId() || list[0]?.id || "";
      setCurrent(saved);
      if (saved) setOfficerId(saved);
    });
  }, []);

  const pick = (id: string) => {
    setCurrent(id);
    setOfficerId(id);
    onChange?.(id);
  };

  return (
    <label className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm">
      <UserCog className="h-4 w-4 text-slate-500" />
      <select
        value={current}
        onChange={(e) => pick(e.target.value)}
        className="cursor-pointer bg-transparent font-medium outline-none"
        aria-label="Chọn cán bộ"
      >
        {officers.map((o) => (
          <option key={o.id} value={o.id}>
            {o.name} · {o.role}
          </option>
        ))}
      </select>
    </label>
  );
}
