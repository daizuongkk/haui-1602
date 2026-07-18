import { CloudOff, ShieldCheck } from "lucide-react";
import { Skeleton } from "@/components/ui/primitives";

export function LoadingCards({ count = 3 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} className="h-32 w-full rounded-2xl" />
      ))}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-2xl border border-red-200 bg-red-50 p-8 text-center text-red-700">
      <CloudOff className="h-8 w-8" />
      <p className="font-semibold">Không kết nối được dữ liệu</p>
      <p className="text-sm text-red-600">{message}</p>
      <p className="text-xs text-red-500">Kiểm tra backend đang chạy tại cổng 8000.</p>
    </div>
  );
}

export function EmptyState({
  title = "Không có cảnh báo",
  hint,
}: {
  title?: string;
  hint?: string;
}) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-2xl border border-green-200 bg-green-50 p-8 text-center text-green-800">
      <ShieldCheck className="h-8 w-8" />
      <p className="font-semibold">{title}</p>
      {hint && <p className="text-sm text-green-600">{hint}</p>}
    </div>
  );
}
