"use client";

import { useMemo } from "react";
import { lessonContentToHtml } from "../../lib/rich-content";

export default function RichContent({ content }: { content?: string | null }) {
  const html = useMemo(() => lessonContentToHtml(content), [content]);
  if (!html) return null;
  return <article className="lesson-rich-content mt-6 text-sm leading-8 text-[var(--text-body)] [&_h1]:mb-3 [&_h1]:mt-7 [&_h1]:text-2xl [&_h1]:font-bold [&_h1]:text-[var(--text-heading)] [&_h2]:mb-3 [&_h2]:mt-7 [&_h2]:text-xl [&_h2]:font-bold [&_h2]:text-[var(--text-heading)] [&_h3]:mb-2 [&_h3]:mt-6 [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:text-[var(--text-heading)] [&_p]:mb-4 [&_ul]:mb-4 [&_ul]:list-disc [&_ul]:space-y-1 [&_ul]:pl-6 [&_ol]:mb-4 [&_ol]:list-decimal [&_ol]:space-y-1 [&_ol]:pl-6 [&_li]:pl-1 [&_blockquote]:my-5 [&_blockquote]:border-l-2 [&_blockquote]:border-[var(--primary)] [&_blockquote]:pl-4 [&_blockquote]:text-[var(--text-muted)] [&_pre]:my-5 [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:bg-[var(--bg-soft)] [&_pre]:p-4 [&_pre]:text-sm [&_code]:rounded [&_code]:bg-[var(--bg-soft)] [&_code]:px-1 [&_code]:py-0.5 [&_a]:font-semibold [&_a]:text-[var(--primary)] [&_a]:underline" dangerouslySetInnerHTML={{ __html: html }} />;
}
