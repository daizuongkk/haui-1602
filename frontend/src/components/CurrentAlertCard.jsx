import { useEffect } from 'react'
import { level } from '../domain/levels'
import { hazardMeta, dayGlyph, actionPictos } from '../domain/icons'
import { useSpeech } from '../domain/useSpeech'
import LevelBadge from './LevelBadge'

// Khối cảnh báo hiện tại + hướng dẫn hành động cho khu vực đang chọn.
// Dữ liệu thật từ backend (bản ghi cảnh báo đã hợp nhất). Nếu không có cảnh báo → trạng thái an toàn.
export default function CurrentAlertCard({ district, record, onSend, onToast }) {
  const { speaking, toggle, stop } = useSpeech()

  const l = level(district.highest_alert_level)
  const hazards = record?.alerts ?? []
  const condition = hazards.length
    ? hazards.map((h) => hazardMeta(h.hazard).label).join(', ')
    : 'Hiện không có cảnh báo cho khu vực này'
  const effectiveTime = record ? `Trong ngày ${record.date}` : null
  const actions = hazards.length
    ? actionPictos(hazards)
    : [{ icon: '📻', text: 'Tiếp tục theo dõi bản tin thời tiết địa phương' }]

  // Dừng đọc khi đổi khu vực.
  useEffect(() => stop(), [district.location_id]) // eslint-disable-line react-hooks/exhaustive-deps

  function toggleSpeak() {
    const text = record?.messages?.vi
      || `Cảnh báo mức ${l.label} tại ${district.location}. ${condition}. `
         + `Người dân cần: ${actions.map((a) => a.text).join('. ')}.`
    toggle(text, () => onToast('Trình duyệt không hỗ trợ đọc giọng nói'))
  }

  return (
    <div className="alert-card2 card" style={{ borderLeft: `6px solid ${l.color}` }}>
      <div className="alert-main">
        <div className="alert-icon-big" style={{ background: l.bg, color: l.color }} aria-hidden="true">
          {dayGlyph(hazards)}
        </div>
        <div className="alert-body">
          <span className="alert-badge">CẢNH BÁO HIỆN TẠI</span>
          <div className="alert-level-title" style={{ color: l.color }}>{l.short}</div>
          <LevelBadge levelKey={district.highest_alert_level} />
          <p className="alert-desc">{condition}</p>
          {effectiveTime && (
            <p className="alert-time"><span aria-hidden="true">🕐</span> {effectiveTime}</p>
          )}

          <div className="alert-actions">
            <button
              type="button"
              className="alert-btn"
              style={{ background: l.color }}
              onClick={toggleSpeak}
              aria-label={speaking ? 'Dừng đọc cảnh báo' : 'Nghe cảnh báo bằng giọng nói'}
            >
              <span aria-hidden="true">🔊</span> {speaking ? 'Đang phát…' : 'Nghe cảnh báo'}
            </button>
            <button
              type="button"
              className="alert-btn secondary"
              onClick={() => onSend('zalo')}
              aria-label="Gửi cảnh báo qua Zalo"
            >
              <span aria-hidden="true">💬</span> Gửi qua Zalo
            </button>
            <button
              type="button"
              className="alert-btn secondary"
              onClick={() => onSend('sms')}
              aria-label="Gửi cảnh báo qua SMS"
            >
              <span aria-hidden="true">📱</span> Gửi SMS
            </button>
          </div>
        </div>
      </div>

      <div className="alert-split" aria-hidden="true" />

      <div className="instructions">
        <h4>Người dân cần:</h4>
        <ul className="instruction-list">
          {actions.map((a, i) => (
            <li className="instruction-item" key={i}>
              <span className="instruction-icon" aria-hidden="true">{a.icon}</span>
              <span>{a.text}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
