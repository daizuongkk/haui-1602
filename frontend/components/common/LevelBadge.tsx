import { levelStyle } from "@/lib/levels";
import type { AlertLevel } from "@/lib/types";
import { cn } from "@/lib/utils";

// Badge mức cảnh báo — LUÔN kèm chữ + icon, không chỉ dùng màu (a11y).
export function LevelBadge({
  level,
  size = "md",
  className,
}: {
  level: AlertLevel;
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  const s = levelStyle(level);
  const Icon = s.icon;
  const sizes = {
    sm: "px-2 py-0.5 text-xs gap-1",
    md: "px-3 py-1 text-sm gap-1.5",
    lg: "px-4 py-1.5 text-base gap-2",
  };
  const iconSizes = { sm: "h-3 w-3", md: "h-4 w-4", lg: "h-5 w-5" };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full font-bold uppercase tracking-wide",
        s.solid,
        sizes[size],
        className
      )}
    >
      <Icon className={iconSizes[size]} />
      {s.label}
    </span>
  );
}
