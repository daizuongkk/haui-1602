import { level } from '../domain/levels'

// Thanh chọn địa điểm — mỗi huyện là một button, tô viền/nền theo mức cảnh báo khi được chọn.
export default function LocationSelector({ districts, selectedId, onSelect }) {
  return (
    <div className="loc-selector" role="group" aria-label="Chọn khu vực">
      {districts.map((d) => {
        const l = level(d.highest_alert_level)
        const active = d.location_id === selectedId
        return (
          <button
            key={d.location_id}
            type="button"
            className={`loc-chip${active ? ' active' : ''}`}
            aria-pressed={active}
            onClick={() => onSelect(d.location_id)}
            style={active ? { borderColor: l.color, background: l.bg } : undefined}
          >
            <span className="loc-name">
              <span aria-hidden="true">{l.emoji}</span> {d.location}
            </span>
            <span className="loc-sub">{d.location.replace('Huyện ', '').replace('TP. ', '')}</span>
          </button>
        )
      })}
    </div>
  )
}
