import { level } from '../domain/levels'

// Nhãn mức cảnh báo: luôn kèm màu + emoji + chữ (không chỉ dựa vào màu).
export default function LevelBadge({ levelKey, short = false }) {
  const l = level(levelKey)
  return (
    <span className="level-badge" style={{ background: l.color }}>
      <span>{l.emoji}</span>
      {short ? l.short : l.label}
    </span>
  )
}
