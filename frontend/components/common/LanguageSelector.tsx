"use client";
import { Languages } from "lucide-react";
import { LANGUAGES, useLanguage } from "@/lib/i18n";
import type { Language } from "@/lib/types";

export function LanguageSelector() {
  const { lang, setLang } = useLanguage();
  return (
    <label className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm">
      <Languages className="h-4 w-4 text-slate-500" />
      <select
        value={lang}
        onChange={(e) => setLang(e.target.value as Language)}
        className="cursor-pointer bg-transparent font-medium outline-none"
        aria-label="Chọn ngôn ngữ"
      >
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code}>
            {l.flag} {l.label}
          </option>
        ))}
      </select>
    </label>
  );
}
