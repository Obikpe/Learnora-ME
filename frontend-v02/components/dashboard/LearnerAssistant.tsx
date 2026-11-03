"use client";

import { useState } from "react";
import { MessageCircle, Send, Sparkles, X } from "lucide-react";
import { askAI } from "../../lib/api/ai";

type ChatMessage = { role: "user" | "assistant"; content: string };

export default function LearnerAssistant({ courses, goal }: { courses: any[]; goal?: string }) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: "Tell me what you want to learn or the kind of work you want to do. I can help you choose a course from Learnora's catalogue." },
  ]);
  const [conversationId, setConversationId] = useState<string>();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function send(value?: string) {
    const message = (value ?? draft).trim();
    if (!message || busy) return;
    setDraft("");
    setError("");
    setMessages(current => [...current, { role: "user", content: message }]);
    setBusy(true);
    const catalogue = courses.slice(0, 15).map(course => [
      `ID: ${course.id}`,
      `Course: ${course.title}`,
      course.level ? `Level: ${course.level}` : "",
      course.estimated_hours ? `Duration: ${course.estimated_hours} hours` : "",
      String(course.short_description || course.description || "").slice(0, 180),
      Array.isArray(course.settings?.topics) && course.settings.topics.length ? `Topics: ${course.settings.topics.slice(0, 5).join(", ")}` : "",
    ].filter(Boolean).join(" | ")).join("\n");
    const prompt = [
      goal ? `Learner's stated goal: ${goal}` : "",
      "Use only the published course catalogue below when recommending Learnora courses. Never invent a course title, course ID, duration, level or availability. If no listed course fits, say so and ask a useful follow-up question.",
      catalogue ? `Published course catalogue:\n${catalogue}` : "The published course catalogue is currently empty.",
      `Learner's message: ${message}`,
    ].filter(Boolean).join("\n\n");
    try {
      const result = await askAI(prompt, "coach", conversationId);
      setConversationId(result.conversation_id || conversationId);
      setMessages(current => [...current, { role: "assistant", content: result.content || result.message || "I couldn't generate a response just now." }]);
    } catch (e: any) {
      setError(e?.message || "The assistant could not respond. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return <>
    {open && <section className="fixed bottom-24 right-4 z-[70] flex h-[min(36rem,calc(100vh-8rem))] w-[min(25rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--card)] shadow-2xl sm:right-6" aria-label="Learnora AI assistant">
      <header className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3">
        <div className="flex items-center gap-2"><span className="grid size-9 place-items-center rounded-full bg-[var(--primary-tint)] text-[var(--primary)]"><Sparkles size={17}/></span><div><h2 className="text-sm font-bold text-[var(--text-heading)]">Learnora assistant</h2><p className="text-[10px] text-[var(--text-muted)]">Course guidance</p></div></div>
        <button type="button" aria-label="Close assistant" onClick={() => setOpen(false)} className="grid size-8 place-items-center rounded-lg hover:bg-[var(--bg-soft)]"><X size={17}/></button>
      </header>
      <div className="flex-1 space-y-3 overflow-y-auto p-4" aria-live="polite">
        {messages.map((message, index) => <div key={index} className={"max-w-[90%] rounded-xl px-3 py-2.5 text-sm leading-6 " + (message.role === "user" ? "ml-auto bg-[var(--primary)] text-[var(--on-primary)]" : "bg-[var(--bg-soft)] text-[var(--text-body)]")}>{message.content}</div>)}
        {busy && <p className="text-xs text-[var(--text-muted)]">Thinking…</p>}
        {error && <p role="alert" className="text-xs text-[var(--warning)]">{error}</p>}
        {messages.length === 1 && <div className="flex flex-wrap gap-2 pt-1">
          <button type="button" onClick={() => void send("Recommend a course for my learning goal.")} className="rounded-full border border-[var(--border)] px-3 py-2 text-xs text-[var(--primary)]">Recommend a course</button>
          <button type="button" onClick={() => void send("I am not sure what to learn next. Help me choose.")} className="rounded-full border border-[var(--border)] px-3 py-2 text-xs text-[var(--primary)]">Help me choose</button>
        </div>}
      </div>
      <form onSubmit={event => { event.preventDefault(); void send(); }} className="flex items-end gap-2 border-t border-[var(--border)] p-3">
        <textarea value={draft} onChange={event => setDraft(event.target.value)} rows={2} maxLength={4000} placeholder="Ask about courses or your learning goal…" className="max-h-28 min-h-11 flex-1 resize-none rounded-xl border border-[var(--border)] bg-[var(--bg)] px-3 py-2.5 text-sm text-[var(--text-body)] outline-none focus:border-[var(--primary)]"/>
        <button type="submit" disabled={!draft.trim() || busy} aria-label="Send message" className="grid size-11 shrink-0 place-items-center rounded-xl bg-[var(--primary)] text-[var(--on-primary)] disabled:opacity-40"><Send size={16}/></button>
      </form>
    </section>}
    <button type="button" onClick={() => setOpen(value => !value)} aria-label={open ? "Close Learnora assistant" : "Chat with Learnora assistant"} className="fixed bottom-5 right-4 z-[71] grid size-14 place-items-center rounded-full bg-[var(--primary)] text-[var(--on-primary)] shadow-xl transition hover:scale-105 sm:right-6">
      {open ? <X size={22}/> : <span className="relative"><MessageCircle size={23}/><Sparkles size={12} className="absolute -right-2 -top-2"/></span>}
    </button>
  </>;
}
