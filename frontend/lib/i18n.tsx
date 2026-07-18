"use client";
import { createContext, useContext, useState, type ReactNode } from "react";
import type { Language } from "./types";

export const LANGUAGES: { code: Language; label: string; flag: string }[] = [
  { code: "vi", label: "Tiếng Việt", flag: "🇻🇳" },
  { code: "thai", label: "Tiếng Thái", flag: "🌸" },
  { code: "hmong", label: "Tiếng H'Mông", flag: "🏔️" },
];

const LangContext = createContext<{
  lang: Language;
  setLang: (l: Language) => void;
}>({ lang: "vi", setLang: () => {} });

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Language>("vi");
  return <LangContext.Provider value={{ lang, setLang }}>{children}</LangContext.Provider>;
}

export const useLanguage = () => useContext(LangContext);
