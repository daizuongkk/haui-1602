import { useState } from 'react'
import { api } from '../services/api'
import AudioPlayer from './AudioPlayer'

// Bảng MÔ PHỎNG phân phối đa kênh: SMS / Zalo OA / loa phát thanh.
// Gọi POST /api/alerts/broadcast và hiển thị nội dung sẽ gửi (không gửi thật).
export default function BroadcastPanel({ record }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function send() {
    setLoading(true)
    try {
      const r = await api.broadcast({ location_id: record.location_id, date: record.date })
      setResult(r)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ marginTop: 16 }}>
      <button className="btn-primary" onClick={send} disabled={loading}>
        {loading ? 'Đang tạo…' : '📢 Mô phỏng gửi cảnh báo đa kênh'}
      </button>
      <div className="muted" style={{ fontSize: 12, marginTop: 6, color: 'var(--ink-soft)' }}>
        Minh hoạ lớp phân phối — hệ thống không gửi tin thật.
      </div>

      {result && (
        <div className="broadcast-out">
          {result.channels.sms && (
            <div className="channel">
              <div className="ch-head">📱 SMS — {result.channels.sms.to}</div>
              <div className="sms-body">{result.channels.sms.text}</div>
              <div className="muted">Độ dài: {result.channels.sms.length} ký tự</div>
            </div>
          )}

          {result.channels.zalo && (
            <div className="channel">
              <div className="ch-head">💬 Zalo OA — {result.channels.zalo.to}</div>
              <div style={{ fontWeight: 700, fontSize: 14 }}>{result.channels.zalo.title}</div>
              <div className="muted" style={{ marginBottom: 6 }}>{result.channels.zalo.subtitle}</div>
              <div style={{ fontSize: 14, lineHeight: 1.5 }}>{result.channels.zalo.body}</div>
            </div>
          )}

          {result.channels.loudspeaker && (
            <div className="channel">
              <div className="ch-head">📢 Loa phát thanh xã — {result.channels.loudspeaker.to}</div>
              <div className="muted" style={{ marginBottom: 8 }}>{result.channels.loudspeaker.instructions}</div>
              {result.channels.loudspeaker.has_translation ? (
                <AudioPlayer audio={result.channels.loudspeaker.audio} lang="vi" />
              ) : (
                <div className="muted">Bản đọc đa ngôn ngữ đang được cập nhật cho ngày này.</div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
