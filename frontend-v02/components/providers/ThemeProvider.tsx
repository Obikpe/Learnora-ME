"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { hasFunctionalCookieConsent } from "../../lib/cookie-consent";

type Theme = "light" | "dark";
type ThemeContextValue = {
  theme: Theme;
  setTheme: (next: Theme) => void;
  toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("light");

  useEffect(() => {
    let initial: Theme = "light";
    try {
      if (hasFunctionalCookieConsent() && window.localStorage.getItem("learnora_theme") === "dark") {
        initial = "dark";
      }
    } catch {
      // Light mode remains the safe default when browser storage is unavailable.
    }
    document.documentElement.dataset.theme = initial;
    setThemeState(initial);

    const syncTheme = (event: StorageEvent) => {
      if (event.key !== "learnora_theme") return;
      const next: Theme = event.newValue === "dark" ? "dark" : "light";
      document.documentElement.dataset.theme = next;
      setThemeState(next);
    };
    window.addEventListener("storage", syncTheme);
    return () => window.removeEventListener("storage", syncTheme);
  }, []);

  const setTheme = useCallback((next: Theme) => {
    setThemeState(next);
    document.documentElement.dataset.theme = next;
    try {
      if (hasFunctionalCookieConsent()) window.localStorage.setItem("learnora_theme", next);
      else window.localStorage.removeItem("learnora_theme");
    } catch {
      // The selected theme still applies for the current app session.
    }
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme(theme === "dark" ? "light" : "dark");
  }, [setTheme, theme]);

  const value = useMemo(() => ({ theme, setTheme, toggleTheme }), [theme, setTheme, toggleTheme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("useTheme must be used inside ThemeProvider");
  return context;
}
