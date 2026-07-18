import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { level } from '../domain/levels'
import { dayGlyph, actionPictos, hazardMeta } from '../domain/icons'
import LangToggle from '../components/LangToggle'
import AudioPlayer from '../components/AudioPlayer'
import ForecastStrip from '../components/ForecastStrip'

// Giao diện cho NGƯỜI DÂN — mô phỏng màn hình điện thoại.
// Ưu tiên: hiểu được mức nguy hiểm chỉ bằng màu + biểu tượng, không cần đọc chữ.
export default function ResidentView({ locations }) {
  const [locationId, setLocationId] = useState(locations[0]?.id)
  const [days, setDays] = useState([])
  const [selectedDate, setSelectedDate] = useState(null)
  const [lang, setLang] = useState('vi')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!locationId) return
    setLoading(true)
    api.forecast(locationId).then((data) => {
      setDays(data)
      setSelectedDate(data[0]?.date ?? null)
      setLoading(false)
    })
  }, [locationId])

  const day = days.find((d) => d.date === selectedDate)
  const l = day ? level(day.highest_alert_level) : level('Green')
  const locName = locations.find((x) => x.id === locationId)?.name ?? ''
  const pictos = day ? actionPictos(day.alerts) : []
  const message = day?.messages?.[lang]

  return (
    <div className="phone-wrap">
      <div className="phone">
        {/* Chọn huyện */}
        <div className="district-picker">
          {locations.map((loc) => (
            <button
              key={loc.id}
              className={loc.id === locationId ? 'active' : ''}
              onClick={() => setLocationId(loc.id)}
            >
              {loc.name.replace('Huyện ', '')}
            </button>
          ))}
        </div>

        {loading || !day ? (
          <div className="loading">Đang tải dự báo…</div>
        ) : (
          <>
            {/* Banner mức cảnh báo lớn */}
            <div className="hero" style={{ background: l.color }}>
              <div className="hero-icon">{dayGlyph(day.alerts)}</div>
              <div className="hero-status">{l.short}</div>
              <div className="hero-where">{locName} · {day.date}</div>
              <div className="hero-hazards">
                {day.alerts.map((a, i) => (
                  <span className="hero-hazard-chip" key={i}>
                    {hazardMeta(a.hazard).glyph} {hazardMeta(a.hazard).label}
                  </span>
                ))}
              </div>
            </div>

            {/* Bản tin + nghe giọng nói */}
            <div className="bulletin">
              <LangToggle lang={lang} onChange={setLang} />
              {message ? (
                <p>{message}</p>
              ) : (
                <p className="untranslated">
                  Bản dịch cho ngôn ngữ này đang được cập nhật. Vui lòng xem bản Tiếng Việt hoặc nghe bản tin.
                </p>
              )}
              <AudioPlayer audio={day.audio} lang={lang} />
            </div>

            {/* Hành động khuyến nghị bằng biểu tượng */}
            {pictos.length > 0 && (
              <div className="actions-row">
                <h4>Khuyến cáo</h4>
                <div className="pictos">
                  {pictos.map((p, i) => (
                    <div className="picto" key={i}>
                      <div style={{ fontSize: 34 }}>{p.icon}</div>
                      <span>{p.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Dự báo 7 ngày */}
            <div className="actions-row" style={{ paddingBottom: 4 }}>
              <h4>Dự báo 7 ngày</h4>
            </div>
            <ForecastStrip days={days} selectedDate={selectedDate} onSelect={setSelectedDate} />
          </>
        )}
      </div>
    </div>
  )
}
