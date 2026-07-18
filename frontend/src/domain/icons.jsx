// Bộ biểu tượng trực quan — ưu tiên dễ hiểu cho người không đọc chữ.
// Mỗi hiểm họa gắn: glyph (biểu tượng lớn), nhãn ngắn, và pictogram hành động khuyến nghị.

// Khoá theo đúng tên hiểm họa do rule_engine.py sinh ra.
export const HAZARD_META = {
  'Mưa lớn & Ngập úng': {
    glyph: '🌧️', label: 'Mưa lớn / Ngập',
    action: { icon: '🌊', text: 'Không qua ngầm tràn, vùng trũng' },
    severity: 2,
  },
  'Lũ quét & Sạt lở': {
    glyph: '⛰️', label: 'Lũ quét / Sạt lở',
    action: { icon: '🚷', text: 'Tránh xa sườn dốc, ven suối' },
    severity: 4,
  },
  'Dông, lốc, sét': {
    glyph: '⛈️', label: 'Dông, lốc, sét',
    action: { icon: '🏠', text: 'Trú ẩn, tránh cây to & cột điện' },
    severity: 3,
  },
  'Mưa đá': {
    glyph: '🧊', label: 'Mưa đá',
    action: { icon: '🌾', text: 'Che chắn mùa màng, gia súc' },
    severity: 3,
  },
  'Sương muối & Băng giá': {
    glyph: '❄️', label: 'Sương muối',
    action: { icon: '🧥', text: 'Chống rét cho cây trồng, vật nuôi' },
    severity: 3,
  },
  'Rét đậm, rét hại': {
    glyph: '🥶', label: 'Rét đậm/hại',
    action: { icon: '🔥', text: 'Giữ ấm người & gia súc' },
    severity: 2,
  },
  'Sương mù dày đặc': {
    glyph: '🌫️', label: 'Sương mù',
    action: { icon: '🚗', text: 'Bật đèn, đi chậm trên đèo dốc' },
    severity: 2,
  },
  'Cháy rừng': {
    glyph: '🔥', label: 'Cháy rừng',
    action: { icon: '🚭', text: 'Cẩn thận củi lửa, không đốt nương' },
    severity: 3,
  },
}

const DEFAULT_META = {
  glyph: '⚠️', label: 'Cảnh báo',
  action: { icon: '📢', text: 'Theo dõi bản tin, chủ động phòng tránh' },
  severity: 1,
}

export function hazardMeta(name) {
  return HAZARD_META[name] || DEFAULT_META
}

// Biểu tượng thời tiết đại diện cho một ngày: chọn hiểm họa nghiêm trọng nhất,
// nếu không có hiểm họa thì hiện trời quang.
export function dayGlyph(alerts) {
  if (!alerts || alerts.length === 0) return '☀️'
  let best = null
  for (const a of alerts) {
    const m = hazardMeta(a.hazard)
    if (!best || m.severity > best.severity) best = m
  }
  return best.glyph
}

// Danh sách pictogram hành động (không trùng) cho một ngày.
export function actionPictos(alerts) {
  const seen = new Set()
  const out = []
  for (const a of alerts || []) {
    const m = hazardMeta(a.hazard)
    if (!seen.has(m.action.text)) {
      seen.add(m.action.text)
      out.push(m.action)
    }
  }
  return out
}

export function PlayIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M8 5v14l11-7z" />
    </svg>
  )
}

export function SpeakerIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
         strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M3 10v4h4l5 4V6L7 10H3z" fill="currentColor" stroke="none" />
      <path d="M16 9a3 3 0 0 1 0 6" />
      <path d="M18.5 6.5a6.5 6.5 0 0 1 0 11" />
    </svg>
  )
}
