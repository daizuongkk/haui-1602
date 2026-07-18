import { level } from '../domain/levels'

// Bản đồ sơ đồ hoá (schematic) tỉnh Điện Biên — không phụ thuộc tile ngoài,
// hoạt động offline. Các huyện được định vị theo lat/lon và tô màu theo mức cảnh báo.
const W = 460
const H = 360
const PAD = 60

export default function DistrictMap({ districts, selectedId, onSelect }) {
  if (!districts || districts.length === 0) return null

  const lats = districts.map((d) => d.latitude)
  const lons = districts.map((d) => d.longitude)
  const minLat = Math.min(...lats), maxLat = Math.max(...lats)
  const minLon = Math.min(...lons), maxLon = Math.max(...lons)
  const spanLat = maxLat - minLat || 1
  const spanLon = maxLon - minLon || 1

  const project = (lat, lon) => {
    const x = PAD + ((lon - minLon) / spanLon) * (W - 2 * PAD)
    const y = PAD + ((maxLat - lat) / spanLat) * (H - 2 * PAD) // lat cao -> y nhỏ (lên trên)
    return [x, y]
  }

  return (
    <div className="map-card card">
      <h3 style={{ marginTop: 0 }}>Bản đồ cảnh báo — Tỉnh Điện Biên</h3>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label="Bản đồ mức cảnh báo các huyện">
        {/* Nền tỉnh cách điệu */}
        <rect x="10" y="10" width={W - 20} height={H - 20} rx="20"
              fill="#eaf1f8" stroke="#d3deea" />
        <text x="24" y="34" fontSize="12" fill="#8fa3b8" fontWeight="700">ĐIỆN BIÊN</text>

        {/* Đường nối các huyện (cho cảm giác lưới địa lý) */}
        {districts.map((d, i) =>
          districts.slice(i + 1).map((d2, j) => {
            const [x1, y1] = project(d.latitude, d.longitude)
            const [x2, y2] = project(d2.latitude, d2.longitude)
            return <line key={`${i}-${j}`} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#cdd9e6" strokeDasharray="4 4" />
          })
        )}

        {/* Điểm huyện */}
        {districts.map((d) => {
          const [x, y] = project(d.latitude, d.longitude)
          const l = level(d.highest_alert_level)
          const selected = d.location_id === selectedId
          return (
            <g key={d.location_id} className="map-district" onClick={() => onSelect?.(d.location_id)}>
              {selected && <circle cx={x} cy={y} r="26" fill="none" stroke={l.color} strokeWidth="3" opacity="0.5" />}
              <circle cx={x} cy={y} r="18" fill={l.color} stroke="#fff" strokeWidth="3" />
              <text className="map-label" x={x} y={y + 38} textAnchor="middle">
                {d.location.replace('Huyện ', '')}
              </text>
            </g>
          )
        })}
      </svg>

      <div className="map-legend">
        {['Red', 'Orange', 'Yellow', 'Green'].map((k) => {
          const l = level(k)
          return (
            <span className="item" key={k}>
              <span className="dot" style={{ background: l.color }} /> {l.label}
            </span>
          )
        })}
      </div>
    </div>
  )
}
