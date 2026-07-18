import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { level } from '../domain/levels'
import { hazardMeta, actionPictos } from '../domain/icons'
import { useSpeech } from '../domain/useSpeech'
import LevelBadge from './LevelBadge'
import Sparkbars from './Sparkbars'

const shortDate = (s) => (s || '').split('/').slice(0, 2).join('/') // dd/mm/yyyy → dd/mm
const priority = (r) => level(r.highest_alert_level).priority

// Side panel bên phải khi click một khu vực: dự báo 3–7 ngày, biểu đồ, khuyến nghị AI, nút hành động.
export default function RiskSidePanel({ district, onClose, onSend, onToast }) {
  const [days, setDays] = useState(null)
  const { speaking, toggle } = useSpeech()

  useEffect(() => {
    let alive = true
    setDays(null)
    api.forecast(district.location_id)
      .then((d) => { if (alive) setDays(d) })
      .catch(() => { if (alive) setDays([]) })
    return () => { alive = false }
  }, [district.location_id])

  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const l = level(district.highest_alert_level)
  const window7 = (days || []).slice(0, 7)
  const worst = window7.length
    ? window7.reduce((a, b) => (priority(b) > priority(a) ? b : a))
    : null
  const recommendations = worst?.alerts?.map((h) => h.description) ?? []
  const pictos = worst ? actionPictos(worst.alerts) : []

  function speakWarning() {
    const text = worst?.messages?.vi
      || `Khu vực ${district.location}, mức cảnh báo ${l.label}.`
    toggle(text, () => onToast('Trình duyệt không hỗ trợ đọc giọng nói'))
  }

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer" role="dialog" aria-modal="true" aria-label={`Chi tiết ${district.location}`} onClick={(e) => e.stopPropagation()}>
        <button className="close" onClick={onClose} aria-label="Đóng">✕ Đóng</button>
        <h2 style={{ margin: '0 0 6px' }}>{district.location}</h2>
        <LevelBadge levelKey={district.highest_alert_level} />

        {days === null && <div className="loading">Đang tải dự báo…</div>}

        {days && days.length === 0 && (
          <p style={{ color: 'var(--ink-soft)', fontStyle: 'italic', marginTop: 14 }}>
            Chưa có dữ liệu dự báo cho khu vực này.
          </p>
        )}

        {window7.length > 0 && (
          <>
            <h4 className="panel-h">Dự báo {window7.length} ngày</h4>
            <Sparkbars
              title="Nhiệt độ cao nhất" unit="°C" color={l.color} decimals={0}
              data={window7.map((r) => ({ label: shortDate(r.date), value: r.weather_summary.max_temp }))}
            />
            <Sparkbars
              title="Lượng mưa 24h" unit="mm" color="#0b74c4" decimals={1}
              data={window7.map((r) => ({ label: shortDate(r.date), value: r.weather_summary.total_rain }))}
            />
            <Sparkbars
              title="Gió giật" unit="km/h" color="#7a5cc4" decimals={0}
              data={window7.map((r) => ({ label: shortDate(r.date), value: r.weather_summary.max_wind_gust }))}
            />

            {recommendations.length > 0 && (
              <>
                <h4 className="panel-h">Khuyến nghị AI</h4>
                <ul className="rec-list">
                  {worst.alerts.map((h, i) => (
                    <li key={i}>
                      <strong>{hazardMeta(h.hazard).glyph} {hazardMeta(h.hazard).label}:</strong> {h.description}
                    </li>
                  ))}
                </ul>
              </>
            )}

            {pictos.length > 0 && (
              <div className="rec-pictos">
                {pictos.map((p, i) => (
                  <span key={i} className="rec-picto"><span aria-hidden="true">{p.icon}</span> {p.text}</span>
                ))}
              </div>
            )}
          </>
        )}

        <div className="panel-actions">
          <button type="button" className="alert-btn" style={{ background: l.color }} onClick={speakWarning}>
            <span aria-hidden="true">🔊</span> {speaking ? 'Đang phát…' : 'Nghe cảnh báo'}
          </button>
          <button type="button" className="alert-btn secondary" onClick={() => onToast('Đã phát cảnh báo đa kênh (mô phỏng)')}>
            <span aria-hidden="true">📢</span> Phát cảnh báo
          </button>
          <button type="button" className="alert-btn secondary" onClick={() => onSend('sms')}>
            <span aria-hidden="true">📱</span> Gửi SMS
          </button>
          <button type="button" className="alert-btn secondary" onClick={() => onSend('zalo')}>
            <span aria-hidden="true">💬</span> Gửi Zalo
          </button>
        </div>
      </div>
    </div>
  )
}
