import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { level, LEVEL_ORDER, LANG_LABELS } from '../domain/levels'
import { hazardMeta, dayGlyph } from '../domain/icons'
import LevelBadge from '../components/LevelBadge'
import DistrictMap from '../components/DistrictMap'
import BroadcastPanel from '../components/BroadcastPanel'
import AudioPlayer from '../components/AudioPlayer'

// Giao diện cho BAN CHỈ HUY PCTT / cán bộ xã — giám sát tổng thể.
export default function DashboardView({ locations }) {
  const [summary, setSummary] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [mapSelected, setMapSelected] = useState(null)
  const [drawer, setDrawer] = useState(null)

  useEffect(() => {
    api.summary().then(setSummary)
    api.activeAlerts().then(setAlerts)
  }, [])

  const visibleAlerts = mapSelected
    ? alerts.filter((a) => a.location_id === mapSelected)
    : alerts

  return (
    <div className="container">
      {/* KPI */}
      {summary && (
        <div className="kpi-row">
          {LEVEL_ORDER.map((k) => {
            const l = level(k)
            return (
              <div className="kpi" key={k} style={{ background: l.color }}>
                <div className="n">{summary.counts[k]}</div>
                <div className="l">{l.label}</div>
              </div>
            )
          })}
          <div className="kpi" style={{ background: '#37474f' }}>
            <div className="n">{alerts.length}</div>
            <div className="l">Ngày có cảnh báo</div>
          </div>
        </div>
      )}

      <div className="dash-grid">
        {/* Bản đồ */}
        {summary && (
          <DistrictMap
            districts={summary.districts}
            selectedId={mapSelected}
            onSelect={(id) => setMapSelected((cur) => (cur === id ? null : id))}
          />
        )}

        {/* Danh sách cảnh báo */}
        <div className="panel card">
          <h3>
            Cảnh báo đang hiệu lực
            {mapSelected && (
              <button
                onClick={() => setMapSelected(null)}
                style={{ float: 'right', fontSize: 12, border: 0, background: '#eef1f6', borderRadius: 8, padding: '4px 10px' }}
              >
                ✕ Bỏ lọc
              </button>
            )}
          </h3>
          <div className="alert-list">
            {visibleAlerts.map((a) => {
              const l = level(a.highest_alert_level)
              return (
                <div className="alert-row" key={`${a.location_id}-${a.date}`} onClick={() => setDrawer(a)}>
                  <div className="stripe" style={{ background: l.color }} />
                  <div style={{ fontSize: 22 }}>{dayGlyph(a.alerts)}</div>
                  <div className="meta">
                    <div className="top">{a.location.replace('Huyện ', '')} · {a.date}</div>
                    <div className="haz">{a.alerts.map((h) => h.hazard).join(', ')}</div>
                  </div>
                  <LevelBadge levelKey={a.highest_alert_level} short />
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {drawer && <DetailDrawer record={drawer} onClose={() => setDrawer(null)} />}
    </div>
  )
}

function DetailDrawer({ record, onClose }) {
  const [lang, setLang] = useState('vi')
  const l = level(record.highest_alert_level)
  const ws = record.weather_summary || {}
  const message = record.messages?.[lang]

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer" onClick={(e) => e.stopPropagation()}>
        <button className="close" onClick={onClose}>✕ Đóng</button>
        <h2 style={{ margin: '0 0 4px' }}>{record.location}</h2>
        <div style={{ color: 'var(--ink-soft)', marginBottom: 10 }}>{record.date}</div>
        <LevelBadge levelKey={record.highest_alert_level} />

        {/* Số liệu thời tiết */}
        <div className="metrics">
          <Metric k="Nhiệt độ" v={`${Math.round(ws.min_temp)}°–${Math.round(ws.max_temp)}°C`} />
          <Metric k="Tổng mưa 24h" v={`${ws.total_rain ?? 0} mm`} />
          <Metric k="Mưa 1h lớn nhất" v={`${ws.max_rain_1h ?? 0} mm`} />
          <Metric k="Gió giật" v={`${ws.max_wind_gust ?? 0} km/h`} />
          <Metric k="Tầm nhìn" v={`${ws.min_visibility ?? 0} m`} />
          <Metric k="Độ ẩm đất sâu" v={`${ws.deep_soil_moisture ?? 0}`} />
        </div>

        {/* Danh sách hiểm họa */}
        <h4 style={{ margin: '14px 0 8px' }}>Chi tiết hiểm họa</h4>
        {record.alerts.map((a, i) => {
          const hl = level(a.level)
          return (
            <div key={i} style={{ borderLeft: `4px solid ${hl.color}`, padding: '6px 10px', marginBottom: 8, background: hl.bg, borderRadius: 8 }}>
              <div style={{ fontWeight: 700, fontSize: 14 }}>{hazardMeta(a.hazard).glyph} {a.hazard} — {hl.label}</div>
              <div style={{ fontSize: 13, color: 'var(--ink)' }}>{a.description}</div>
            </div>
          )
        })}

        {/* Bản tin đa ngôn ngữ */}
        <h4 style={{ margin: '14px 0 8px' }}>Bản tin</h4>
        <div className="lang-toggle" style={{ marginBottom: 10 }}>
          {['vi', 'thai', 'hmong'].map((lk) => (
            <button key={lk} className={lang === lk ? 'active' : ''} onClick={() => setLang(lk)}>
              {LANG_LABELS[lk]}
            </button>
          ))}
        </div>
        {message ? (
          <p style={{ lineHeight: 1.55, fontSize: 14 }}>{message}</p>
        ) : (
          <p style={{ color: 'var(--ink-soft)', fontStyle: 'italic', fontSize: 14 }}>
            Bản dịch đang được cập nhật cho ngày/địa điểm này.
          </p>
        )}
        <AudioPlayer audio={record.audio} lang={lang} />

        {/* Phân phối đa kênh */}
        <h4 style={{ margin: '18px 0 4px' }}>Phân phối cảnh báo</h4>
        <BroadcastPanel record={record} />
      </div>
    </div>
  )
}

function Metric({ k, v }) {
  return (
    <div className="metric">
      <div className="v">{v}</div>
      <div className="k">{k}</div>
    </div>
  )
}
