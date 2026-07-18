import { level } from '../domain/levels'
import { dayGlyph } from '../domain/icons'

const DOW = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

function dowLabel(ddmmyyyy) {
  const [d, m, y] = ddmmyyyy.split('/').map(Number)
  const date = new Date(y, m - 1, d)
  return DOW[date.getDay()]
}

// Dải dự báo nhiều ngày: mỗi ngày một thẻ tô màu theo mức cảnh báo + biểu tượng thời tiết.
export default function ForecastStrip({ days, selectedDate, onSelect }) {
  return (
    <div className="forecast-strip">
      {days.map((day) => {
        const l = level(day.highest_alert_level)
        return (
          <div
            key={day.date}
            className={`day-card ${day.date === selectedDate ? 'selected' : ''}`}
            style={{ background: l.color }}
            onClick={() => onSelect(day.date)}
            title={`${day.date} · ${l.label}`}
          >
            <div className="dow">{dowLabel(day.date)}</div>
            <div className="d-icon">{dayGlyph(day.alerts)}</div>
            <div className="temp">
              {Math.round(day.weather_summary?.min_temp ?? 0)}° / {Math.round(day.weather_summary?.max_temp ?? 0)}°
            </div>
          </div>
        )
      })}
    </div>
  )
}
