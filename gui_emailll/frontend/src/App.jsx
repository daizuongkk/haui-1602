import { useEffect, useState } from 'react'
import { api } from './services/api'
import ResidentView from './views/ResidentView'
import DashboardView from './views/DashboardView'

export default function App() {
  const [tab, setTab] = useState('resident')
  const [locations, setLocations] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.locations().then(setLocations).catch((e) => setError(e.message))
  }, [])

  return (
    <div>
      <header className="app-header">
        <div>
          <h1>🌦️ Cảnh báo Thời tiết Vi mô — Điện Biên</h1>
          <div className="sub">Đúng người · Đúng lúc · Đúng ngôn ngữ (Việt · Thái · H'Mông)</div>
        </div>
        <div className="tabs">
          <button className={tab === 'resident' ? 'active' : ''} onClick={() => setTab('resident')}>
            👨‍🌾 Người dân
          </button>
          <button className={tab === 'dashboard' ? 'active' : ''} onClick={() => setTab('dashboard')}>
            🛰️ Ban Chỉ huy PCTT
          </button>
        </div>
      </header>

      {error && (
        <div className="error-box">
          Không kết nối được tới API ({error}). Hãy chạy backend: <code>cd backend &amp;&amp; uvicorn main:app --reload</code>
        </div>
      )}

      {!locations && !error && <div className="loading">Đang tải…</div>}

      {locations && (
        tab === 'resident'
          ? <ResidentView locations={locations} />
          : <DashboardView locations={locations} />
      )}
    </div>
  )
}
