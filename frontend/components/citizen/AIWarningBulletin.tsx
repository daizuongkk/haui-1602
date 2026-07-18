"use client";
import { Sparkles } from "lucide-react";
import { Card } from "@/components/ui/primitives";
import { AudioPlayer } from "@/components/common/AudioPlayer";
import { useLanguage } from "@/lib/i18n";
import type { AlertRecord } from "@/lib/types";

// Bản tin AI — luôn hiển thị sẵn, không cần bấm mở. Đổi theo ngôn ngữ.
export function AIWarningBulletin({ record }: { record: AlertRecord | null }) {
  const { lang } = useLanguage();
  if (!record) return null;

  const message = record.messages[lang];

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-5 py-3">
        <Sparkles className="h-5 w-5 text-indigo-500" />
        <h2 className="font-bold text-slate-900">AI cảnh báo</h2>
      </div>
      <div className="space-y-4 p-5">
        {message ? (
          <p className="whitespace-pre-line text-base leading-relaxed text-slate-800">{message}</p>
        ) : (
          <p className="text-sm italic text-slate-400">
            Chưa có bản tin cho ngôn ngữ này. Hãy thử ngôn ngữ khác.
          </p>
        )}
        <AudioPlayer src={record.audio[lang]} />
      </div>
    </Card>
  );
}
