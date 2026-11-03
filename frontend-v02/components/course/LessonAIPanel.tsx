"use client";

import { useState } from "react";
import { X, Send, Sparkles, BookOpen } from "lucide-react";
import { askAI } from "../../lib/api/ai";

type Props = { courseId: string; lessonId: string; lessonTitle: string; notes: string; lessonContent: string; video?: any; onClose: () => void; };

function transcriptText(video: any) {
  const value = video?.transcript_text || video?.transcript || video?.captions_text || video?.captions || "";
  if (typeof value === "string") return value.slice(0, 10000);
  if (Array.isArray(value)) return value.map((part: any) => typeof part === "string" ? part : part?.text || "").join("\n").slice(0, 10000);
  return "";
}

export default function LessonAIPanel({ courseId, lessonId, lessonTitle, notes, lessonContent, video, onClose }: Props) {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [conversationId, setConversationId] = useState<string>();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function send(event?: any) {
    event?.preventDefault?.();
    if (!prompt.trim() || busy) return;
    const question = prompt.trim();
    setPrompt("");
    setError("");
    setMessages(old => [...old, { role: "user", content: question }]);
    setBusy(true);
    const learnerNotes = notes.trim() ? "My current lesson notes (may include unsaved edits):\n" + notes.slice(0, 2500) + "\n\n" : "";
    try {
      const result = await askAI(learnerNotes + question, "tutor", conversationId, { course_id: courseId, lesson_id: lessonId });
      setConversationId(result.conversation_id);
      setMessages(old => [...old, { role: "assistant", content: result.content || "I could not generate a response just now." }]);
    } catch (e: any) {
      setError(e?.message || "The lesson assistant is temporarily unavailable.");
    } finally { setBusy(false); }
  }
  return <div className="fixed inset-y-0 right-0 z-[90] flex w-full max-w-[390px] flex-col border-l border-[var(--border)] bg-[var(--card)] shadow-2xl">
    <header className="flex items-center justify-between gap-3 border-b border-[var(--border)] px-4 py-4">
      <div className="flex min-w-0 items-center gap-3"><span className="grid size-9 shrink-0 place-items-center rounded-xl bg-[var(--primary-tint)] text-[var(--primary)]"><Sparkles size={18}/></span><div className="min-w-0"><h2 className="text-sm font-bold text-[var(--text-heading)]">Ask about this lesson</h2><p className="truncate text-[11px] text-[var(--text-muted)]">{lessonTitle}</p></div></div>
      <button type="button" onClick={onClose} aria-label="Close AI assistant" className="grid size-9 place-items-center rounded-lg border border-[var(--border)] text-[var(--text-muted)] hover:bg-[var(--bg-soft)]"><X size={17}/></button>
    </header>
    <div className="flex items-start gap-2 border-b border-[var(--border)] bg-[var(--bg-soft)] px-4 py-3 text-[11px] leading-5 text-[var(--text-muted)]"><BookOpen size={14} className="mt-0.5 shrink-0 text-[var(--primary)]"/>Lesson notes and published lesson material are included. Video transcript is included when available in the lesson media record.</div>
    <div className="flex-1 space-y-3 overflow-y-auto p-4" aria-live="polite">
      {!messages.length && <p className="rounded-xl border border-[var(--border)] p-4 text-sm leading-6 text-[var(--text-muted)]">Ask for an explanation, an example, or a hint. Your course remains open behind this panel.</p>}
      {messages.map((message, index) => <div key={index} className={"max-w-[95%] whitespace-pre-wrap rounded-xl p-3 text-sm leading-6 " + (message.role === "user" ? "ml-auto bg-[var(--primary-tint)] text-[var(--text-heading)]" : "bg-[var(--bg-soft)] text-[var(--text-body)]")}>{message.content}</div>)}
      {busy && <p className="text-xs text-[var(--text-muted)]">Thinking about your lesson…</p>}
    </div>
    <form onSubmit={send} className="border-t border-[var(--border)] p-3">
      {error && <p role="alert" className="mb-2 text-xs text-[var(--error)]">{error}</p>}
      <textarea value={prompt} onChange={e => setPrompt(e.target.value)} rows={3} maxLength={4000} placeholder="Ask a question about what you're learning…" className="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--bg)] p-3 text-sm text-[var(--text-body)] outline-none focus:border-[var(--primary)]"/>
      <button type="submit" disabled={busy || !prompt.trim()} className="mt-2 inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-xl bg-[var(--primary)] px-4 text-sm font-semibold text-[var(--on-primary)] disabled:opacity-50">{busy ? "Thinking…" : <><Send size={14}/> Ask Learnora AI</>}</button>
    </form>
  </div>;
}
