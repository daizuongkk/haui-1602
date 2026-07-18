"use client";
import { useEffect, useState } from "react";
import { Copy, Maximize2, Megaphone, X, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/primitives";
import { useToast } from "@/components/ui/toast";

// Nội dung loa phát thanh do AI sinh sẵn — cán bộ chỉnh sửa & đọc.
export function BroadcastScript({ initial }: { initial: string }) {
  const toast = useToast();
  const [text, setText] = useState(initial);
  const [fullscreen, setFullscreen] = useState(false);
  const [played, setPlayed] = useState(false);

  useEffect(() => {
    setText(initial);
    setPlayed(false);
  }, [initial]);

  const copy = async () => {
    await navigator.clipboard.writeText(text);
    toast("Đã sao chép nội dung phát thanh");
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Megaphone className="h-5 w-5 text-slate-500" />
        <h3 className="font-bold text-slate-900">Nội dung loa phát thanh</h3>
        <div className="ml-auto flex gap-2">
          <Button variant="outline" onClick={copy}>
            <Copy className="h-4 w-4" /> Sao chép
          </Button>
          <Button variant="outline" onClick={() => setFullscreen(true)}>
            <Maximize2 className="h-4 w-4" /> Toàn màn hình
          </Button>
        </div>
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={8}
        className="w-full resize-y rounded-xl border border-slate-300 p-4 text-base leading-relaxed outline-none focus:border-slate-500"
      />

      <Button
        variant={played ? "outline" : "primary"}
        onClick={() => {
          setPlayed(true);
          toast("Đã đánh dấu phát loa tại xã");
        }}
      >
        <CheckCircle2 className="h-4 w-4" />
        {played ? "Đã phát loa" : "Đánh dấu đã phát loa"}
      </Button>

      {fullscreen && (
        <div className="fixed inset-0 z-[9998] flex flex-col bg-white p-6 sm:p-12">
          <button
            onClick={() => setFullscreen(false)}
            className="ml-auto rounded-full p-2 hover:bg-slate-100"
            aria-label="Đóng"
          >
            <X className="h-7 w-7" />
          </button>
          <p className="mx-auto max-w-3xl overflow-y-auto whitespace-pre-line text-2xl font-medium leading-relaxed text-slate-900 sm:text-3xl">
            {text}
          </p>
        </div>
      )}
    </div>
  );
}
