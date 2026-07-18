import { useEffect, useState } from 'react'

// Đọc văn bản tiếng Việt bằng Web Speech API. Dùng chung cho card cảnh báo và side panel.
// toggle(text, onUnsupported): đang đọc thì dừng, ngược lại đọc text.
export function useSpeech() {
  const [speaking, setSpeaking] = useState(false)

  // Dừng đọc khi component rời trang.
  useEffect(() => () => window.speechSynthesis?.cancel(), [])

  function toggle(text, onUnsupported) {
    const synth = window.speechSynthesis
    if (!synth || typeof window.SpeechSynthesisUtterance === 'undefined') {
      onUnsupported?.()
      return
    }
    if (speaking) {
      synth.cancel()
      setSpeaking(false)
      return
    }
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'vi-VN'
    u.onend = () => setSpeaking(false)
    u.onerror = () => setSpeaking(false)
    synth.cancel()
    synth.speak(u)
    setSpeaking(true)
  }

  function stop() {
    window.speechSynthesis?.cancel()
    setSpeaking(false)
  }

  return { speaking, toggle, stop }
}
