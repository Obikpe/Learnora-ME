"use client";

import { useEffect, useRef } from "react";
import { Bold, Italic, Underline, Heading2, List, ListOrdered, Quote, Link2 } from "lucide-react";

function escapeHtml(value: string) {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function toEditorHtml(value: string) {
  const raw = String(value || "").trim();
  if (!raw) return "<p></p>";
  if (/<\s*(p|div|h[1-6]|ul|ol|li|strong|b|em|i|u|blockquote|pre|code|a|br|hr)\b/i.test(raw)) {
    return raw.replace(/<script\b[\s\S]*?<\/script>/gi, "").replace(/\son\w+\s*=\s*(["']).*?\1/gi, "").replace(/javascript:/gi, "");
  }
  const lines = raw.replace(/\r\n?/g, "\n").split("\n");
  const html: string[] = [];
  let paragraph: string[] = [];
  let listType = "";
  let items: string[] = [];
  const flushParagraph = () => { if (paragraph.length) html.push("<p>" + paragraph.map(escapeHtml).join("<br/>") + "</p>"); paragraph = []; };
  const flushList = () => { if (listType) html.push("<" + listType + ">" + items.map(item => "<li>" + escapeHtml(item) + "</li>").join("") + "</" + listType + ">"); listType = ""; items = []; };
  for (const line of lines) {
    const heading = line.match(/^\s{0,3}(#{1,3})\s+(.+)$/);
    const bullet = line.match(/^\s*[-*+]\s+(.+)$/);
    const numbered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (heading) { flushParagraph(); flushList(); const tag = "h" + heading[1].length; html.push("<" + tag + ">" + escapeHtml(heading[2]) + "</" + tag + ">"); continue; }
    if (bullet || numbered) { flushParagraph(); const next = bullet ? "ul" : "ol"; if (listType && listType !== next) flushList(); listType = next; items.push((bullet || numbered)![1]); continue; }
    if (!line.trim()) { flushParagraph(); flushList(); continue; }
    flushList(); paragraph.push(line);
  }
  flushParagraph(); flushList();
  return html.join("") || "<p></p>";
}

export default function RichTextEditor({ value, onChange, placeholder = "Write your lesson content…" }: { value: string; onChange: (value: string) => void; placeholder?: string }) {
  const editor = useRef<HTMLDivElement>(null);
  const initialised = useRef(false);

  useEffect(() => {
    if (!editor.current) return;
    const html = toEditorHtml(value);
    if (editor.current.innerHTML !== html) editor.current.innerHTML = html;
    if (!initialised.current && html !== value) onChange(html);
    initialised.current = true;
  }, [value, onChange]);

  function command(name: string, argument?: string) {
    editor.current?.focus();
    document.execCommand(name, false, argument);
    if (editor.current) onChange(editor.current.innerHTML);
  }

  const tools = [
    { label: "Bold", icon: Bold, run: () => command("bold") },
    { label: "Italic", icon: Italic, run: () => command("italic") },
    { label: "Underline", icon: Underline, run: () => command("underline") },
    { label: "Heading", icon: Heading2, run: () => command("formatBlock", "h2") },
    { label: "Bulleted list", icon: List, run: () => command("insertUnorderedList") },
    { label: "Numbered list", icon: ListOrdered, run: () => command("insertOrderedList") },
    { label: "Quote", icon: Quote, run: () => command("formatBlock", "blockquote") },
    { label: "Link", icon: Link2, run: () => { const url = window.prompt("Enter the link address"); if (url && /^(https?:\/\/|mailto:)/i.test(url)) command("createLink", url); } },
  ];

  return <div className="overflow-hidden rounded-lg border border-white/[.12] bg-[#0b0f14]">
    <div className="flex flex-wrap items-center gap-1 border-b border-white/[.1] p-2">
      {tools.map(({ label, icon: Icon, run }) => <button key={label} type="button" title={label} aria-label={label} onMouseDown={event => event.preventDefault()} onClick={run} className="grid size-9 place-items-center rounded-md text-slate-400 transition hover:bg-white/[.08] hover:text-white"><Icon size={16}/></button>)}
    </div>
    <div ref={editor} contentEditable suppressContentEditableWarning role="textbox" aria-multiline="true" data-placeholder={placeholder} onInput={event => onChange(event.currentTarget.innerHTML)} className="min-h-[19rem] max-h-[55vh] overflow-y-auto px-4 py-4 text-sm leading-7 text-slate-200 outline-none [&_h1]:my-4 [&_h1]:text-2xl [&_h1]:font-bold [&_h2]:my-4 [&_h2]:text-xl [&_h2]:font-bold [&_h3]:my-3 [&_h3]:text-lg [&_h3]:font-semibold [&_ul]:my-3 [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:my-3 [&_ol]:list-decimal [&_ol]:pl-6 [&_blockquote]:my-3 [&_blockquote]:border-l-2 [&_blockquote]:border-amber-400 [&_blockquote]:pl-4"/>
    <div className="border-t border-white/[.08] px-4 py-2 text-[10px] text-slate-600">Write normally and use the formatting tools above.</div>
  </div>;
}
