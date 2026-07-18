import { useEffect, useRef } from 'react'

const CHANNEL_LABEL = { zalo: 'Zalo', sms: 'SMS' }
const CHANNEL_ICON = { zalo: '💬', sms: '📱' }

// Modal xác nhận gửi cảnh báo (mô phỏng). Đóng bằng nút X, Hủy, click nền hoặc phím Escape.
export default function ConfirmSendModal({ channel, preview, onConfirm, onClose }) {
  const dialogRef = useRef(null)

  useEffect(() => {
    dialogRef.current?.focus()
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const label = CHANNEL_LABEL[channel] || 'kênh'

  return (
    <div className="drawer-backdrop modal-center" onClick={onClose}>
      <div
        ref={dialogRef}
        className="confirm-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        <button className="modal-close" onClick={onClose} aria-label="Đóng">✕</button>
        <h3 id="confirm-title">
          <span aria-hidden="true">{CHANNEL_ICON[channel]}</span> Gửi cảnh báo qua {label}
        </h3>
        <p className="modal-sub">Xem trước nội dung sẽ gửi (mô phỏng — không gửi tin thật):</p>
        <div className="modal-preview">{preview}</div>
        <div className="modal-actions">
          <button type="button" className="alert-btn secondary" onClick={onClose}>Hủy</button>
          <button type="button" className="btn-primary" onClick={onConfirm}>Xác nhận gửi</button>
        </div>
      </div>
    </div>
  )
}
