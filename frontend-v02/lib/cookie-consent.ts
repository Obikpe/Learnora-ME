export function hasFunctionalCookieConsent(): boolean {
  if (typeof window === "undefined") return false;
  try {
    const consent = JSON.parse(window.localStorage.getItem("learnora_cookie_consent_v1") || "null");
    return consent?.version === 1 && consent?.essential === true && consent?.functional === true;
  } catch {
    return false;
  }
}
