"use client";
import { useState } from "react";
import { Check, ShieldCheck, LifeBuoy } from "lucide-react";
import { Card } from "@/components/ui/primitives";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api";
import type { FeedbackKind } from "@/lib/types";

const OPTIONS: { kind: FeedbackKind; label: string; icon: typeof Check; cls: string }[] = [
  { kind: "received", label: "Đã nhận tin", icon: Check, cls: "border-green-300 text-green-700 hover:bg-green-50" },
  { kind: "safe", label: "Tôi an toàn", icon: ShieldCheck, cls: "border-slate-300 text-slate-700 hover:bg-slate-50" },
  { kind: "need_help", label: "Cần hỗ trợ", icon: LifeBuoy, cls: "border-red-300 text-red-700 hover:bg-red-50" },
];

// Nút phản hồi cho người dân — gắn với cảnh báo đang xem.
export function FeedbackButtons({ alertId }: { alertId: number }) {
  const toast = useToast();
  const [sent, setSent] = useState<FeedbackKind | null>(null);

  const send = async (kind: FeedbackKind) => {
    try {
      const note = kind === "need_help" ? window.prompt("Mô tả ngắn tình huống (không bắt buộc):") || undefined : undefined;
      await api.feedback(alertId, { kind, note });
      setSent(kind);
      toast(kind === "need_help" ? "Đã gửi yêu cầu hỗ trợ tới cán bộ" : "Cảm ơn phản hồi của bạn");
    } catch (e) {
      toast(e instanceof Error ? e.message : "Gửi thất bại", "error");
    }
  };

  return (
    <Card className="p-4">
      <p className="mb-3 text-sm font-semibold text-slate-700">Phản hồi của bạn giúp chính quyền nắm tình hình:</p>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
        {OPTIONS.map((o) => (
          <button
            key={o.kind}
            onClick={() => send(o.kind)}
            className={`inline-flex items-center justify-center gap-2 rounded-xl border py-3 text-sm font-semibold transition-colors ${o.cls} ${
              sent === o.kind ? "ring-2 ring-offset-1" : ""
            }`}
          >
            <o.icon className="h-5 w-5" /> {o.label}
          </button>
        ))}
      </div>
    </Card>
  );
}
