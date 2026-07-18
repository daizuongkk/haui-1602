import { useEffect, useRef, useState } from 'react'
import { level } from '../domain/levels'
import { hazardMeta } from '../domain/icons'

// Bản đồ nguy cơ dạng POLYGON (sơ đồ hoá, offline — không cần tile/GeoJSON ngoài).
// Mỗi huyện là một vùng được tô màu theo mức cảnh báo, ranh giới trắng mảnh.
// Toạ độ trong hệ viewBox 100×76; nhãn HTML đặt theo % nên trùng khớp với polygon.
const VB_W = 100
const VB_H = 76

// Hình học sơ đồ hoá cho 3 huyện có dữ liệu (vị trí tương đối theo địa lý).
const GEO = {
  muong_nhe: { path: 'M6,12 L40,8 L48,26 L34,44 L12,40 L4,24 Z', cx: 25, cy: 25 },
  muong_cha: { path: 'M54,9 L90,15 L86,38 L60,40 L50,24 Z', cx: 68, cy: 25 },
  tuan_giao: { path: 'M30,50 L70,47 L92,64 L60,73 L28,66 Z', cx: 55, cy: 60 },
}

// Xác suất định tính suy từ mức cảnh báo (backend không có trường xác suất số).
const LIKELIHOOD = { Red: 'Rất cao', Orange: 'Cao', Yellow: 'Trung bình', Green: 'Thấp' }

const num = (v, suffix = '') => (v === null || v === undefined ? '—' : `${v}${suffix}`)

export default function RiskMap({ districts, recordByLoc, selectedId, onSelect }) {
  const [hovered, setHovered] = useState(null)
  const [rising, setRising] = useState({})
  const prevRef = useRef(null)

  // Phát hiện huyện có mức cảnh báo TĂNG so với lần cập nhật trước → nhấp sáng + badge.
  useEffect(() => {
    const cur = {}
    districts.forEach((d) => { cur[d.location_id] = level(d.highest_alert_level).priority })
    const prev = prevRef.current
    prevRef.current = cur
    if (!prev) return
    const newly = {}
    for (const id in cur) if (prev[id] !== undefined && cur[id] > prev[id]) newly[id] = true
    if (Object.keys(newly).length) {
      setRising(newly)
      const t = setTimeout(() => setRising({}), 2500)
      return () => clearTimeout(t)
    }
  }, [districts])

  const geoDistricts = districts.filter((d) => GEO[d.location_id])

  return (
    <div className="map-card card">
      <h3 style={{ marginTop: 0 }}>Bản đồ nguy cơ — Điện Biên</h3>

      <div className="risk-map-canvas">
        <svg viewBox={`0 0 ${VB_W} ${VB_H}`} className="risk-map-svg" role="img" aria-label="Bản đồ nguy cơ theo huyện">
          {/* Nền địa hình cách điệu */}
          <rect x="0" y="0" width={VB_W} height={VB_H} fill="#e9f0ea" />
          {[16, 30, 46, 62].map((y) => (
            <path key={y} d={`M0,${y} Q25,${y - 5} 50,${y} T100,${y}`} fill="none" stroke="#d6e2d8" strokeWidth="0.6" />
          ))}

          {geoDistricts.map((d) => {
            const g = GEO[d.location_id]
            const l = level(d.highest_alert_level)
            const isHover = hovered === d.location_id
            const isSel = selectedId === d.location_id
            const cls = [
              'risk-region',
              isHover ? 'is-hover' : '',
              isSel ? 'is-selected' : '',
              rising[d.location_id] ? 'is-rising' : '',
            ].join(' ').trim()
            return (
              <path
                key={d.location_id}
                d={g.path}
                className={cls}
                fill={l.color}
                onMouseEnter={() => setHovered(d.location_id)}
                onMouseLeave={() => setHovered(null)}
                onClick={() => onSelect(d.location_id)}
                role="button"
                tabIndex={0}
                aria-label={`${d.location}: ${l.label}`}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(d.location_id) } }}
              />
            )
          })}
        </svg>

        {/* Nhãn nổi cho từng huyện */}
        {geoDistricts.map((d) => {
          const g = GEO[d.location_id]
          const l = level(d.highest_alert_level)
          return (
            <div
              key={d.location_id}
              className={`risk-label${rising[d.location_id] ? ' is-rising' : ''}`}
              style={{ left: `${g.cx}%`, top: `${(g.cy / VB_H) * 100}%` }}
            >
              <span className="risk-label-name"><span aria-hidden="true">📍</span> {d.location.replace('Huyện ', '')}</span>
              <span className="risk-label-level" style={{ color: l.color }}>{l.emoji} {l.label}</span>
              {rising[d.location_id] && <span className="risk-badge">▲ Tăng</span>}
            </div>
          )
        })}

        {/* Tooltip khi hover */}
        {hovered && (() => {
          const d = districts.find((x) => x.location_id === hovered)
          if (!d) return null
          const g = GEO[hovered]
          const l = level(d.highest_alert_level)
          const rec = recordByLoc?.[hovered]
          const ws = rec?.weather_summary
          const haz = rec?.alerts?.length ? rec.alerts.map((h) => hazardMeta(h.hazard).label).join(', ') : 'Không có'
          return (
            <div className="risk-tooltip" style={{ left: `${g.cx}%`, top: `${(g.cy / VB_H) * 100}%` }}>
              <div className="rt-head" style={{ color: l.color }}>{d.location}</div>
              <div className="rt-level">{l.emoji} {l.label}</div>
              <dl className="rt-grid">
                <dt>Thiên tai</dt><dd>{haz}</dd>
                <dt>Khả năng</dt><dd>{LIKELIHOOD[l.key]}</dd>
                <dt>Nhiệt độ</dt><dd>{ws ? `${Math.round(ws.min_temp)}–${Math.round(ws.max_temp)}°C` : '—'}</dd>
                <dt>Lượng mưa</dt><dd>{ws ? num(ws.total_rain, ' mm') : '—'}</dd>
                <dt>Gió giật</dt><dd>{ws ? num(ws.max_wind_gust, ' km/h') : '—'}</dd>
              </dl>
            </div>
          )
        })()}
      </div>

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
