import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import { level } from '../domain/levels'
import { hazardMeta } from '../domain/icons'
import LocationSelector from '../components/LocationSelector'
import CurrentAlertCard from '../components/CurrentAlertCard'
import LocationSummaryCard from '../components/LocationSummaryCard'
import RiskMap from '../components/RiskMap'
import RiskSidePanel from '../components/RiskSidePanel'
import ConfirmSendModal from '../components/ConfirmSendModal'
import Toast from '../components/Toast'

// dd/mm/yyyy → khoá so sánh (yyyy, mm, dd) để chọn ngày gần nhất.
const dateKey = (s) => (s || '').split('/').reverse().join('')

// Bản ghi r có "đáng chọn" hơn cur không: ưu tiên mức cao hơn, rồi ngày sớm hơn.
function isBetter(r, cur) {
  const dp = level(r.highest_alert_level).priority - level(cur.highest_alert_level).priority
  if (dp !== 0) return dp > 0
  return dateKey(r.date) < dateKey(cur.date)
}

// Với mỗi huyện, chọn bản ghi cảnh báo tiêu biểu: mức cao nhất, rồi ngày sớm nhất.
function pickRepresentative(records) {
  const byLoc = {}
  for (const r of records) {
    const cur = byLoc[r.location_id]
    if (!cur || isBetter(r, cur)) byLoc[r.location_id] = r
  }
  return byLoc
}

function nowStamp() {
  return new Date().toLocaleString('vi-VN', {
    hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric',
  })
}

// Giao diện BAN CHỈ HUY PCTT — dashboard giám sát 3 khu vực bằng dữ liệu thật từ backend.
export default function DashboardView() {
  const [districts, setDistricts] = useState([])
  const [recordByLoc, setRecordByLoc] = useState({})
  const [selectedId, setSelectedId] = useState(null)
  const [updatedAt, setUpdatedAt] = useState(nowStamp())
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState(false)
  const [modal, setModal] = useState(null) // { channel }
  const [toast, setToast] = useState('')
  const [panelId, setPanelId] = useState(null) // khu vực đang mở side panel

  async function load(isRefresh = false) {
    if (isRefresh) setIsRefreshing(true)
    try {
      const [summary, active] = await Promise.all([api.summary(), api.activeAlerts()])
      const list = summary.districts
      setDistricts(list)
      setRecordByLoc(pickRepresentative(active))
      setError(false)
      // Mặc định chọn khu vực nguy hiểm nhất (đọc nhanh: đâu là nơi nguy hiểm).
      setSelectedId((cur) => {
        if (cur && list.some((d) => d.location_id === cur)) return cur
        const worst = [...list].sort(
          (a, b) => level(b.highest_alert_level).priority - level(a.highest_alert_level).priority,
        )[0]
        return worst?.location_id ?? null
      })
      setUpdatedAt(nowStamp())
    } catch {
      setError(true)
    } finally {
      if (isRefresh) setIsRefreshing(false)
    }
  }

  useEffect(() => { load() }, [])

  async function refresh() {
    const started = Date.now()
    await load(true)
    const wait = Math.max(0, 700 - (Date.now() - started))
    setTimeout(() => setToast('Đã cập nhật dữ liệu mới nhất'), wait)
  }

  const selectedDistrict = useMemo(
    () => districts.find((d) => d.location_id === selectedId) || null,
    [districts, selectedId],
  )
  const selectedRecord = selectedId ? recordByLoc[selectedId] : null
  const panelDistrict = panelId ? districts.find((d) => d.location_id === panelId) : null

  // Click bản đồ / card chi tiết: chọn khu vực và mở side panel.
  function openPanel(id) {
    setSelectedId(id)
    setPanelId(id)
  }

  function confirmSend() {
    const channel = modal?.channel
    setModal(null)
    setToast(channel === 'zalo' ? 'Đã giả lập gửi cảnh báo qua Zalo' : 'Đã giả lập gửi cảnh báo qua SMS')
  }

  const previewText = useMemo(() => {
    if (!selectedDistrict) return ''
    const r = selectedRecord
    if (r?.messages?.vi) return r.messages.vi
    const haz = r?.alerts?.map((h) => hazardMeta(h.hazard).label).join(', ') || 'Theo dõi thời tiết'
    return `${selectedDistrict.location} — ${level(selectedDistrict.highest_alert_level).label}. ${haz}.`
  }, [selectedDistrict, selectedRecord])

  if (error) {
    return (
      <div className="container">
        <div className="empty-state card">
          <p>Chưa có dữ liệu thời tiết. Hãy chạy backend rồi thử lại.</p>
          <button className="btn-primary" onClick={() => load()}>Thử tải lại</button>
        </div>
      </div>
    )
  }

  if (!districts.length) {
    return <div className="loading">Đang tải dữ liệu…</div>
  }

  return (
    <div className="container">
      {/* Thanh chọn địa điểm + thời gian cập nhật */}
      <div className="dash-top">
        <LocationSelector districts={districts} selectedId={selectedId} onSelect={setSelectedId} />
        <div className="last-updated">
          <span className="lu-text">Cập nhật lúc {updatedAt}</span>
          <button
            type="button"
            className="refresh-btn"
            onClick={refresh}
            disabled={isRefreshing}
            aria-label="Làm mới dữ liệu"
          >
            <span className={isRefreshing ? 'spin' : ''} aria-hidden="true">🔄</span>
            {isRefreshing ? 'Đang cập nhật…' : 'Làm mới'}
          </button>
        </div>
      </div>

      {/* Nội dung chính: cảnh báo + hướng dẫn (trái) · bản đồ (phải) */}
      <div className="dash-main">
        <div className="dash-left">
          {selectedDistrict && (
            <CurrentAlertCard
              district={selectedDistrict}
              record={selectedRecord}
              onSend={(channel) => setModal({ channel })}
              onToast={setToast}
            />
          )}
        </div>
        <div className="dash-right">
          <RiskMap
            districts={districts}
            recordByLoc={recordByLoc}
            selectedId={selectedId}
            onSelect={openPanel}
          />
        </div>
      </div>

      {/* Chi tiết nhanh các khu vực */}
      <div className="summary-section">
        <div className="summary-section-head">
          <h3>Chi tiết khu vực</h3>
        </div>
        <div className="summary-grid">
          {districts.map((d) => (
            <LocationSummaryCard
              key={d.location_id}
              district={d}
              record={recordByLoc[d.location_id]}
              active={d.location_id === selectedId}
              onSelect={openPanel}
            />
          ))}
        </div>
      </div>

      {panelDistrict && (
        <RiskSidePanel
          district={panelDistrict}
          onClose={() => setPanelId(null)}
          onSend={(channel) => setModal({ channel })}
          onToast={setToast}
        />
      )}

      {modal && (
        <ConfirmSendModal
          channel={modal.channel}
          preview={previewText}
          onConfirm={confirmSend}
          onClose={() => setModal(null)}
        />
      )}
      {toast && <Toast message={toast} onClose={() => setToast('')} />}
    </div>
  )
}
