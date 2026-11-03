const allowedTags = new Set(["p","br","h1","h2","h3","h4","h5","h6","strong","b","em","i","u","ul","ol","li","blockquote","pre","code","a","hr","img"]);

function escapeHtml(value: string) {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

function safeHref(value: string) {
  const href = value.trim();
  return /^(https?:\/\/|mailto:|\/(?!\/)|#)/i.test(href) && !/[\u0000-\u001f\\]/.test(href) ? href : "";
}

function sanitizeHtml(value: string) {
  return value
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<\s*(script|style|iframe|object|embed|svg|math)\b[\s\S]*?<\/\s*\1\s*>/gi, "")
    .replace(/<\/?([a-z][a-z0-9]*)([^>]*)>/gi, (match, rawTag: string, attrs: string) => {
      const tag = rawTag.toLowerCase();
      const closing = /^<\s*\//.test(match);
      if (tag === "div") return closing ? "</p>" : "<p>";
      if (tag === "span") return "";
      if (!allowedTags.has(tag)) return "";
      if (closing) return ["br","hr"].includes(tag) ? "" : `</${tag}>`;
      if (tag === "img") {
        const srcMatch = attrs.match(/src\\s*=\\s*(["'])(.*?)\\1/i);
        const altMatch = attrs.match(/alt\\s*=\\s*(["'])(.*?)\\1/i);
        const src = srcMatch?.[2]?.trim() || "";
        const safeSrc = /^(https?:\\/\\/|\\/|\\.\\.?\\/)[^\\s"'<>]+$/i.test(src) && !/[\\u0000-\\u001f\\\\]/.test(src) ? src : "";
        if (!safeSrc) return "";
        return `<img src="${escapeHtml(safeSrc)}" alt="${escapeHtml(altMatch?.[2] || "")}" loading="lazy" decoding="async" />`;
      }
      if (tag === "a") {
        const hrefMatch = attrs.match(/href\s*=\s*(["'])(.*?)\1/i);
        const href = hrefMatch ? safeHref(hrefMatch[2]) : "";
        return href ? `<a href="${escapeHtml(href)}" rel="noopener noreferrer">` : "<a>";
      }
      return `<${tag}>`;
    });
}

function inlineMarkdown(value: string) {
  let text = escapeHtml(value);
  const code: string[] = [];
  text = text.replace(/`([^`]+)`/g, (_match, content: string) => {
    const marker = `%%INLINECODE${code.length}%%`;
    code.push(`<code>${content}</code>`);
    return marker;
  });
  text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|mailto:[^\s)]+|\/[^\s)]*|#[^\s)]*)\)/g, (_match, label: string, href: string) => {
    const safe = safeHref(href);
    return safe ? `<a href="${escapeHtml(safe)}" rel="noopener noreferrer">${label}</a>` : label;
  });
  text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/__(.+?)__/g, "<strong>$1</strong>");
  text = text.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>").replace(/(^|[^_])_([^_\n]+)_(?!_)/g, "$1<em>$2</em>");
  return text.replace(/%%INLINECODE(\d+)%%/g, (_match, index: string) => code[Number(index)] || "");
}

function markdownToHtml(value: string) {
  const lines = value.replace(/\r\n?/g, "\n").split("\n");
  const output: string[] = [];
  let paragraph: string[] = [];
  let listType = "";
  let listItems: string[] = [];
  let quote: string[] = [];
  let code: string[] = [];
  let inCode = false;

  const flushParagraph = () => {
    if (paragraph.length) output.push(`<p>${paragraph.map(inlineMarkdown).join("<br/>")}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (listType) output.push(`<${listType}>${listItems.map(item => `<li>${inlineMarkdown(item)}</li>`).join("")}</${listType}>`);
    listType = "";
    listItems = [];
  };
  const flushQuote = () => {
    if (quote.length) output.push(`<blockquote>${quote.map(line => `<p>${inlineMarkdown(line)}</p>`).join("")}</blockquote>`);
    quote = [];
  };
  const flushCode = () => {
    if (inCode) output.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
    code = [];
    inCode = false;
  };

  for (const line of lines) {
    if (/^\s*```/.test(line)) {
      flushParagraph(); flushList(); flushQuote();
      if (inCode) flushCode(); else inCode = true;
      continue;
    }
    if (inCode) { code.push(line); continue; }
    const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+)$/);
    if (heading) {
      flushParagraph(); flushList(); flushQuote();
      const level = heading[1].length;
      output.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      continue;
    }
    if (/^\s{0,3}([-*_])(?:\s*\1){2,}\s*$/.test(line)) {
      flushParagraph(); flushList(); flushQuote(); output.push("<hr/>"); continue;
    }
    const bullet = line.match(/^\s*[-*+]\s+(.+)$/);
    const numbered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (bullet || numbered) {
      flushParagraph(); flushQuote();
      const nextType = bullet ? "ul" : "ol";
      if (listType && listType !== nextType) flushList();
      listType = nextType;
      listItems.push((bullet || numbered)![1]);
      continue;
    }
    const quoteLine = line.match(/^\s*>\s?(.*)$/);
    if (quoteLine) {
      flushParagraph(); flushList(); quote.push(quoteLine[1]); continue;
    }
    if (!line.trim()) {
      flushParagraph(); flushList(); flushQuote(); continue;
    }
    flushList(); flushQuote(); paragraph.push(line);
  }
  flushParagraph(); flushList(); flushQuote(); flushCode();
  return output.join("");
}

export function lessonContentToHtml(value?: string | null) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  if (/^\s*<\s*(p|div|h[1-6]|ul|ol|li|strong|b|em|i|u|blockquote|pre|code|a|br|hr)\b/i.test(raw)) {
    return sanitizeHtml(raw);
  }
  return markdownToHtml(raw);
}
