"use client";
import { Volume2, VolumeX } from "lucide-react";

// Trình phát audio bản tin (mp3 do backend sinh, phục vụ tại /audio/...).
export function AudioPlayer({ src }: { src?: string }) {
  if (!src) {
    return (
      <div className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-400">
        <VolumeX className="h-4 w-4" />
        Chưa có bản audio cho ngôn ngữ này
      </div>
    );
  }
  return (
    <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
      <Volume2 className="h-4 w-4 shrink-0 text-slate-500" />
      {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
      <audio controls preload="none" src={src} className="h-9 w-full max-w-md">
        Trình duyệt không hỗ trợ phát audio.
      </audio>
    </div>
  );
}
