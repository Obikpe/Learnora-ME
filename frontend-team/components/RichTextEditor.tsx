"use client";

import { useEffect, useRef } from "react";
import { Bold, Italic, Underline, Heading2, List, ListOrdered, Quote, Link2 } from "lucide-react";

function escapeHtml(value: string) {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function inline(value: string) {
  let text = escapeHtml(value);
  const code: string[] = [];
  text = text.replace(/`([^`]+)`/g, (_match, content: string) => {
    const marker = `%%CODE${code.length}%%`;
    code.push("<code>" + content + "</code>");
    return marker;
  });
  text = text.replace(/[([^]]+)]((https?:\/\/[^\s)]+|mailto:[^\s)]+))/g, (_match, label: string, href: string) => "<a href=\"" + escapeHtml(href) + "\">" + label + "</a>");
  text = text.replace(/**(.+?)**/g, "<strong>$1</strong>").replace(/__(.+?)__/g, "<strong>$1</strong>");
  text = text.replace(/(^|[^*])*([^*\n]+)*(?!*)/g, "$1<em>$2</em>").replace(/(^|[^_])_([^_\n]+)_(?!_)/g, "$1<em>$2</em>");
  return text.replace(/%%CODE(\d+)%%/g, (_match, index: string) => code[Number(index)] || "");
}

function sanitiseEditorHtml(value: string) {
  const allowed = new Set(["p","br","h1","h2","h3","h4","h5","h6","strong","b","em","i","u","ul","ol","li","blockquote","pre","code","a","hr"]);
  return value
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<\s*(script|style|iframe|object|embed|svg|math)\b[\s\S]*?<\/\s*\1\s*>/gi, "")
    .replace(/<\/?([a-z][a-z0-9]*)([^>]*)>/gi, (match, rawTag: string, attrs: string) => {
      const tag = rawTag.toLowerCase();
      const closing = /^<\s*\//.test(match);
      if (tag === "div") return closing ? "</p>" : "<p>";
      if (tag === "span") return "";
      if (!allowed.has(tag)) return "";
      if (closing) return tag === "br" || tag === "hr" ? "" : "</" + tag + ">";
      if (tag === "a") {
        const hrefMatch = attrs.match(/href\s*=\s*(["'])(.*?)\1/i);
        const href = hrefMatch?.[2] || "";
        return /^(https?:\/\/|mailto:|\/|#)/i.test(href) ? "<a href=\"" + escapeHtml(href) + "\">" : "<a>";
      }
      return "<" + tag + ">";
    });
}

function toEditorHtml(value: string) {
  const raw = String(value || "").trim();
  if (!raw) return "<p></p>";
  if (/<\s*(p|div|h[1-6]|ul|ol|li|strong|b|em|i|u|blockquote|pre|code|a|br|hr)\b/i.test(raw)) return sanitiseEditorHtml(raw);
  const lines = raw.replace(/\r\n?/g, "\n").split("\n");
  const html: string[] = [];
  let paragraph: string[] = [];
  let listType = "";
  let items: string[] = [];
  let quote: string[] = [];
  let code: string[] = [];
  let inCode = false;
  const flushParagraph = () => { if (paragraph.length) html.push("<p>" + paragraph.map(inline).join("<br/>") + "</p>"); paragraph = []; };
  const flushList = () => { if (listType) html.push("<" + listType + ">" + items.map(item => "<li>" + inline(item) + "</li>").join("") + "</" + listType + ">"); listType = ""; items = []; };
  const flushQuote = () => { if (quote.length) html.push("<blockquote>" + quote.map(item => "<p>" + inline(item) + "</p>").join("") + "</blockquote>"); quote = []; };
  const flushCode = () => { if (inCode) html.push("<pre><code>" + escapeHtml(code.join("\n")) + "</code></pre>"); code = []; inCode = false; };
  for (const line of lines) {
    if (/^\s*```/.test(line)) { flushParagraph(); flushList(); flushQuote(); if (inCode) flushCode(); else inCode = true; continue; }
    if (inCode) { code.push(line); continue; }
    const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+)$/);
    const bullet = line.match(/^\s*[-*+]\s+(.+)$/);
    const numbered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    const quoteLine = line.match(/^\s*>\s?(.*)$/);
    if (heading) { flushParagraph(); flushList(); flushQuote(); const tag = "h" + heading[1].length; html.push("<" + tag + ">" + inline(heading[2]) + "</" + tag + ">"); continue; }
    if (bullet || numbered) { flushParagraph(); flushQuote(); const next = bullet ? "ul" : "ol"; if (listType && listType !== next) flushList(); listType = next; items.push((bullet || numbered)![1]); continue; }
    if (quoteLine) { flushParagraph(); flushList(); quote.push(quoteLine[1]); continue; }
    if (!line.trim()) { flushParagraph(); flushList(); flushQuote(); continue; }
    flushList(); flushQuote(); paragraph.push(line);
  }
  flushParagraph(); flushList(); flushQuote(); flushCode();
  return html.join("") || "<p></p>";
}

export default function RichTextEditor({ value, onChange, placeholder = "Write your lesson content…" }: { value: string; onChange: (value: string) => void; placeholder?: string }) {
  const editor = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!editor.current || editor.current.contains(document.activeElement)) return;
    const html = toEditorHtml(value);
    if (editor.current.innerHTML !== html) editor.current.innerHTML = html;
    if (html !== value) onChange(html);
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
  </div>;
}
