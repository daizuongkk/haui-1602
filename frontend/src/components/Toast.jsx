import { useEffect } from 'react'

// Thông báo nổi ngắn, tự ẩn sau ~2.6s.
export default function Toast({ message, onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 2600)
    return () => clearTimeout(t)
  }, [message, onClose])

  return (
    <div className="toast" role="status" aria-live="polite">
      <span aria-hidden="true">✓</span> {message}
    </div>
  )
}
