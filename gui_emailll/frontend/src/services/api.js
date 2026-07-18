// Lớp gọi API. Dùng đường dẫn tương đối (proxy Vite -> backend:8000).
// Có thể ghi đè base URL bằng biến môi trường VITE_API_BASE khi build production.
const BASE = import.meta.env.VITE_API_BASE || ''

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`)
  return res.json()
}

export const api = {
  locations: () => get('/api/locations'),
  summary: () => get('/api/summary'),
  activeAlerts: () => get('/api/alerts/active'),
  forecast: (locationId) => get(`/api/forecast/${locationId}`),
  broadcast: async (body) => {
    const res = await fetch(`${BASE}/api/alerts/broadcast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(`broadcast → ${res.status}`)
    return res.json()
  },
  audioUrl: (path) => `${BASE}${path}`,
}
