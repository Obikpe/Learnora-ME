const PREFIX = "learnora-quiz-tab:";

export function getQuizTabId(): string {
  if (typeof window === "undefined") return "";
  if (window.name.startsWith(PREFIX)) return window.name.slice(PREFIX.length);
  const id = crypto.randomUUID();
  window.name = PREFIX + id;
  return id;
}

export function clearQuizTabSession(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem("learnora_quiz_active");
  sessionStorage.removeItem("learnora_quiz_course_id");
  sessionStorage.removeItem("learnora_quiz_id");
  sessionStorage.removeItem("learnora_quiz_session_id");
  sessionStorage.removeItem("learnora_quiz_tab_id");
}

export function isQuizActiveInThisTab(): boolean {
  if (typeof window === "undefined") return false;
  const storedTabId = sessionStorage.getItem("learnora_quiz_tab_id");
  if (!storedTabId || storedTabId !== getQuizTabId()) {
    if (storedTabId) clearQuizTabSession();
    return false;
  }
  return sessionStorage.getItem("learnora_quiz_active") === "1";
}
