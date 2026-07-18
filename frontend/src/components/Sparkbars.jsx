// Biểu đồ cột nhỏ (inline SVG, không cần thư viện). Dùng cho nhiệt độ / lượng mưa / gió theo ngày.
const VW = 100
const VH = 46
const GAP = 3

export default function Sparkbars({ title, unit, color, data, decimals = 0 }) {
  if (!data || data.length === 0) return null
  const values = data.map((d) => d.value)
  const max = Math.max(...values, 0.0001)
  const n = data.length
  const bw = (VW - GAP * (n - 1)) / n
  const fmt = (v) => v.toFixed(decimals)

  return (
    <div className="chart">
      <div className="chart-title">{title} <small>({unit})</small></div>
      <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" role="img" aria-label={`${title} theo ngày`} preserveAspectRatio="none">
        {data.map((d, i) => {
          const h = Math.max(1.5, (d.value / max) * (VH - 12))
          const x = i * (bw + GAP)
          const y = VH - h - 8
          return (
            <g key={i}>
              <rect x={x} y={y} width={bw} height={h} rx="1.5" fill={color} opacity={0.85} />
              <text x={x + bw / 2} y={y - 1.5} textAnchor="middle" fontSize="4.5" fill="#5b6472" fontWeight="700">
                {fmt(d.value)}
              </text>
              <text x={x + bw / 2} y={VH - 1.5} textAnchor="middle" fontSize="4" fill="#8794a5">
                {d.label}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
