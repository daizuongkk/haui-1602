"use client";
import { useState } from "react";
import { MessageSquare, Send, Radio, Loader2 } from "lucide-react";
import { Card, Button } from "@/components/ui/primitives";
import { useToast } from "@/components/ui/toast";
import { LevelBadge } from "@/components/common/LevelBadge";
import { AudioPlayer } from "@/components/common/AudioPlayer";
import { BroadcastScript } from "./BroadcastScript";
import { api } from "@/lib/api";
import type { AlertRecord, BroadcastChannel, BroadcastResponse } from "@/lib/types";

const CHANNELS: { id: BroadcastChannel; label: string; icon: typeof Radio }[] = [
  { id: "sms", label: "SMS", icon: MessageSquare },
  { id: "zalo", label: "Zalo OA", icon: Send },
  { id: "loudspeaker", label: "Loa phát thanh", icon: Radio },
];

export function BroadcastCenter({ record }: { record: AlertRecord }) {
  const toast = useToast();
  const [selected, setSelected] = useState<BroadcastChannel[]>(["sms", "zalo", "loudspeaker"]);
  const [result, setResult] = useState<BroadcastResponse | null>(null);
  const [sending, setSending] = useState(false);

  const toggle = (c: BroadcastChannel) =>
    setSelected((s) => (s.includes(c) ? s.filter((x) => x !== c) : [...s, c]));

  const send = async () => {
    if (selected.length === 0) return toast("Chọn ít nhất một kênh", "error");
    setSending(true);
    try {
      const res = await api.broadcast({
        location_id: record.location_id,
        date: record.date,
        channels: selected,
      });
      setResult(res);
      toast(`Đã mô phỏng gửi qua ${selected.length} kênh (không gửi thật)`);
    } catch (e) {
      toast(e instanceof Error ? e.message : "Gửi thất bại", "error");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card className="space-y-4 p-5">
        <div className="flex flex-wrap items-center gap-3">
          <div>
            <p className="text-lg font-bold text-slate-900">{record.location}</p>
            <p className="text-sm text-slate-500">Cảnh báo ngày {record.date}</p>
          </div>
          <LevelBadge level={record.highest_alert_level} className="ml-auto" />
        </div>

        <div>
          <p className="mb-2 text-sm font-semibold text-slate-600">Chọn kênh phát</p>
          <div className="flex flex-wrap gap-2">
            {CHANNELS.map((c) => {
              const on = selected.includes(c.id);
              return (
                <button
                  key={c.id}
                  onClick={() => toggle(c.id)}
                  className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-medium transition-colors ${
                    on ? "border-slate-900 bg-slate-900 text-white" : "border-slate-300 text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  <c.icon className="h-4 w-4" />
                  {c.label}
                </button>
              );
            })}
          </div>
        </div>

        <Button variant="danger" onClick={send} disabled={sending}>
          {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          Duyệt & phát cảnh báo
        </Button>
        <p className="text-xs text-amber-600">⚠️ Chỉ mô phỏng — hệ thống không gửi tin thật.</p>
      </Card>

      {result && (
        <>
          <div className="grid gap-3 md:grid-cols-2">
            {result.channels.sms && (
              <Card className="space-y-1 p-4">
                <p className="flex items-center gap-2 text-sm font-bold text-slate-800">
                  <MessageSquare className="h-4 w-4" /> SMS · {result.channels.sms.length} ký tự
                </p>
                <p className="text-sm text-slate-600">{result.channels.sms.text}</p>
              </Card>
            )}
            {result.channels.zalo && (
              <Card className="space-y-1 p-4">
                <p className="flex items-center gap-2 text-sm font-bold text-slate-800">
                  <Send className="h-4 w-4" /> {result.channels.zalo.title}
                </p>
                <p className="text-xs font-medium text-slate-500">{result.channels.zalo.subtitle}</p>
                <p className="text-sm text-slate-600">{result.channels.zalo.body}</p>
              </Card>
            )}
          </div>

          {result.channels.loudspeaker && (
            <Card className="space-y-3 p-5">
              <p className="text-xs text-slate-500">{result.channels.loudspeaker.instructions}</p>
              <div className="flex flex-wrap gap-2">
                {(["vi", "thai", "hmong"] as const).map((l) => (
                  <AudioPlayer key={l} src={result.channels.loudspeaker!.audio[l] ?? undefined} />
                ))}
              </div>
            </Card>
          )}
        </>
      )}

      <Card className="p-5">
        <BroadcastScript initial={record.messages.vi ?? "Chưa có bản tin tiếng Việt cho cảnh báo này."} />
      </Card>
    </div>
  );
}
