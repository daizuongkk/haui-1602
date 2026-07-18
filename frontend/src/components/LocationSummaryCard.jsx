import { level } from '../domain/levels'
import { hazardMeta } from '../domain/icons'
import LevelBadge from './LevelBadge'

const dash = (v, suffix = '') => (v === null || v === undefined ? '—' : `${v}${suffix}`)

// Card tóm tắt nhanh của một khu vực: mức cảnh báo, hiện tượng và 3 chỉ số thời tiết thật.
export default function LocationSummaryCard({ district, record, active, onSelect }) {
  const l = level(district.highest_alert_level)
  const ws = record?.weather_summary
  const condition = record?.alerts?.length
    ? record.alerts.map((h) => hazardMeta(h.hazard).label).join(', ')
    : 'Không có cảnh báo'

  const temp = ws ? `${Math.round(ws.min_temp)}–${Math.round(ws.max_temp)}°C` : '—'
  const rain = ws ? dash(ws.total_rain, ' mm') : '—'
  const soil = ws ? dash(ws.deep_soil_moisture) : '—'

  return (
    <button
      type="button"
      className={`summary-card${active ? ' active' : ''}`}
      style={{ borderTop: `4px solid ${l.color}` }}
      onClick={() => onSelect(district.location_id)}
      aria-label={`Xem chi tiết ${district.location}, mức ${l.label}`}
    >
      <div className="summary-head">
        <span className="summary-name">{district.location}</span>
        <LevelBadge levelKey={district.highest_alert_level} short />
      </div>
      <div className="summary-condition">{condition}</div>
      <div className="summary-metrics">
        <div className="summary-metric">
          <span aria-hidden="true">🌡️</span>
          <span>{temp}</span>
        </div>
        <div className="summary-metric">
          <span aria-hidden="true">🌧️</span>
          <span>{rain}</span>
        </div>
        <div className="summary-metric">
          <span aria-hidden="true">💧</span>
          <span>{soil}<small> ẩm đất</small></span>
        </div>
      </div>
      <span className="summary-chevron" aria-hidden="true">›</span>
    </button>
  )
}
