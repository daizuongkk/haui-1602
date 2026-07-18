"use client";
import { useEffect, useState } from "react";
import { Check, X, Send, MessageSquare, Radio, Loader2, CheckCircle2, Users } from "lucide-react";
import { Card, Button } from "@/components/ui/primitives";
import { useToast } from "@/components/ui/toast";
import { LevelBadge } from "@/components/common/LevelBadge";
import { BroadcastScript } from "./BroadcastScript";
import { api, getOfficerId } from "@/lib/api";
import type { AlertDetail, Channel } from "@/lib/types";

const CHANNELS: { id: Channel; label: string; icon: typeof Radio }[] = [
  { id: "sms", label: "SMS", icon: MessageSquare },
  { id: "zalo", label: "Zalo OA", icon: Send },
  { id: "loudspeaker", label: "Loa phát thanh", icon: Radio },
];

export function AlertOpsPanel({ alertId, onChanged }: { alertId: number; onChanged?: () => void }) {
  const toast = useToast();
  const [alert, setAlert] = useState<AlertDetail | null>(null);
  const [busy, setBusy] = useState(false);
  const [channels, setChannels] = useState<Channel[]>(["sms", "zalo", "loudspeaker"]);

  const load = () => api.alert(alertId).then(setAlert);
  useEffect(() => {
    setAlert(null);
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [alertId]);

  const guardOfficer = () => {
    if (!getOfficerId()) {
      toast("Hãy chọn cán bộ trước khi thao tác", "error");
      return false;
    }
    return true;
  };

  const act = async (fn: () => Promise<unknown>, ok: string) => {
    if (!guardOfficer()) return;
    setBusy(true);
    try {
      await fn();
      await load();
      onChanged?.();
      toast(ok);
    } catch (e) {
      toast(e instanceof Error ? e.message : "Thao tác thất bại", "error");
    } finally {
      setBusy(false);
    }
  };

  if (!alert) return <Card className="p-6 text-sm text-slate-400">Đang tải…</Card>;

  const isPending = alert.status === "pending_approval";
  const canDispatch = alert.status === "approved" || alert.status === "distributed";

  return (
    <div className="space-y-4">
      <Card className="space-y-4 p-5">
        <div className="flex flex-wrap items-center gap-3">
          <div>
            <p className="text-lg font-bold text-slate-900">{alert.commune_name}</p>
            <p className="text-sm text-slate-500">{alert.district_name} · {alert.date}</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <LevelBadge level={alert.highest_alert_level} />
            <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-700">
              {alert.status_label}
            </span>
          </div>
        </div>

        {alert.note && <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700">{alert.note}</p>}

        {/* Phê duyệt */}
        {isPending && (
          <div className="flex gap-2">
            <Button variant="primary" disabled={busy} onClick={() => act(() => api.approve(alert.id), "Đã duyệt cảnh báo")}>
              <Check className="h-4 w-4" /> Duyệt
            </Button>
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => {
                const reason = window.prompt("Lý do từ chối?");
                if (reason) act(() => api.reject(alert.id, reason), "Đã từ chối cảnh báo");
              }}
            >
              <X className="h-4 w-4" /> Từ chối
            </Button>
          </div>
        )}
        {alert.status === "rejected" && (
          <p className="text-sm text-red-600">Đã từ chối: {alert.rejected_reason}</p>
        )}

        {/* Phân phối */}
        {canDispatch && (
          <div className="space-y-2">
            <p className="text-sm font-semibold text-slate-600">Chọn kênh phát</p>
            <div className="flex flex-wrap gap-2">
              {CHANNELS.map((c) => {
                const on = channels.includes(c.id);
                return (
                  <button
                    key={c.id}
                    onClick={() => setChannels((s) => (on ? s.filter((x) => x !== c.id) : [...s, c.id]))}
                    className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-medium ${
                      on ? "border-slate-900 bg-slate-900 text-white" : "border-slate-300 text-slate-600 hover:bg-slate-50"
                    }`}
                  >
                    <c.icon className="h-4 w-4" /> {c.label}
                  </button>
                );
              })}
            </div>
            <div className="flex gap-2 pt-1">
              <Button
                variant="danger"
                disabled={busy || channels.length === 0}
                onClick={() => act(() => api.dispatch(alert.id, channels), `Đã phát qua ${channels.length} kênh (mô phỏng)`)}
              >
                {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />} Duyệt & phát
              </Button>
              {alert.status === "distributed" && (
                <Button variant="outline" disabled={busy} onClick={() => act(() => api.setStatus(alert.id, "closed"), "Đã đóng cảnh báo")}>
                  <CheckCircle2 className="h-4 w-4" /> Đóng
                </Button>
              )}
            </div>
            <p className="text-xs text-amber-600">⚠️ Chỉ mô phỏng — hệ thống không gửi tin thật.</p>
          </div>
        )}
      </Card>

      {/* Lịch sử phân phối */}
      {alert.dispatches.length > 0 && (
        <Card className="p-4">
          <p className="mb-2 text-sm font-bold text-slate-800">Lịch sử phân phối ({alert.dispatches.length})</p>
          <ul className="space-y-1 text-sm text-slate-600">
            {alert.dispatches.map((d) => (
              <li key={d.id} className="flex items-center gap-2">
                <span className="font-medium uppercase">{d.channel}</span>
                <span className={d.status === "sent_sim" ? "text-green-600" : "text-red-600"}>
                  {d.status === "sent_sim" ? "đã gửi (mô phỏng)" : `lỗi: ${d.error}`}
                </span>
                <span className="ml-auto text-xs text-slate-400">{d.created_at?.slice(11, 16)}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Nội dung loa */}
      <Card className="p-5">
        <BroadcastScript initial={alert.messages.vi ?? "Chưa có bản tin tiếng Việt."} />
      </Card>

      {/* Phản hồi người dân */}
      <Card className="p-4">
        <p className="mb-2 flex items-center gap-2 text-sm font-bold text-slate-800">
          <Users className="h-4 w-4" /> Phản hồi người dân
        </p>
        <div className="flex gap-4 text-sm">
          <span className="text-green-700">Đã nhận: {alert.feedback_counts.received}</span>
          <span className="text-slate-600">An toàn: {alert.feedback_counts.safe}</span>
          <span className="font-semibold text-red-700">Cần hỗ trợ: {alert.feedback_counts.need_help}</span>
        </div>
        {alert.feedback.filter((f) => f.kind === "need_help").length > 0 && (
          <ul className="mt-2 space-y-1 text-sm text-red-700">
            {alert.feedback.filter((f) => f.kind === "need_help").map((f) => (
              <li key={f.id}>• {f.note || "(không ghi chú)"} {f.contact ? `— ${f.contact}` : ""}</li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
