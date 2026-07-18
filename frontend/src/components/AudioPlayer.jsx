import { useRef, useState } from 'react'
import { api } from '../services/api'
import { PlayIcon, SpeakerIcon } from '../domain/icons'
import { LANG_LABELS } from '../domain/levels'

// Nút nghe bản tin bằng giọng nói. Nếu không có audio cho ngôn ngữ đang chọn
// thì nút bị vô hiệu hoá (suy giảm mềm, không vỡ giao diện).
export default function AudioPlayer({ audio, lang }) {
  const audioRef = useRef(null)
  const [playing, setPlaying] = useState(false)
  const [failed, setFailed] = useState(false)

  const src = audio && audio[lang] ? api.audioUrl(audio[lang]) : null
  const disabled = !src || failed

  function toggle() {
    const el = audioRef.current
    if (!el) return
    if (playing) {
      el.pause()
    } else {
      el.play().catch(() => setFailed(true))
    }
  }

  return (
    <>
      <button className="audio-btn" onClick={toggle} disabled={disabled}>
        {playing ? <SpeakerIcon /> : <PlayIcon />}
        {disabled
          ? 'Chưa có bản đọc'
          : playing ? 'Đang phát…' : `Nghe bản tin (${LANG_LABELS[lang]})`}
      </button>
      {src && (
        <audio
          ref={audioRef}
          src={src}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)}
          onError={() => { setFailed(true); setPlaying(false) }}
        />
      )}
    </>
  )
}
