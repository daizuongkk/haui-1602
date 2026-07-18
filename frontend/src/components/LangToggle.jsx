import { LANG_LABELS } from '../domain/levels'

const LANGS = ['vi', 'thai', 'hmong']

// Chuyển đổi ngôn ngữ bản tin: Việt / Thái / H'Mông.
export default function LangToggle({ lang, onChange }) {
  return (
    <div className="lang-toggle">
      {LANGS.map((l) => (
        <button
          key={l}
          className={lang === l ? 'active' : ''}
          onClick={() => onChange(l)}
        >
          {LANG_LABELS[l]}
        </button>
      ))}
    </div>
  )
}
