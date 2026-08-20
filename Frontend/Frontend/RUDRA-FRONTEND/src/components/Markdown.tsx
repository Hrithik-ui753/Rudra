import { useMemo } from 'react';

export default function Markdown({ content }: { content: string }) {
  const html = useMemo(() => render(content), [content]);
  return <div className="md" dangerouslySetInnerHTML={{ __html: html }} />;
}

function render(src: string): string {
  let s = escapeHtml(src);
  // Code blocks
  s = s.replace(/```([\s\S]*?)```/g, (_, code) => `<pre><code>${code.trim()}</code></pre>`);
  // Inline code
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Horizontal rules
  s = s.replace(/^---$/gm, '<hr>');
  s = s.replace(/^\*\*\*$/gm, '<hr>');
  // Headings
  s = s.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  s = s.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  s = s.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  // Blockquote
  s = s.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
  // Bold / italic
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  // Links
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  // Tables
  s = renderTables(s);
  // Lists
  s = renderLists(s);
  // Paragraphs
  s = s.split(/\n{2,}/).map(block => {
    if (/^<(h\d|ul|ol|pre|blockquote|table|hr)/.test(block.trim())) return block;
    return `<p>${block.replace(/\n/g, '<br>')}</p>`;
  }).join('\n');
  return s;
}

function renderTables(s: string): string {
  return s.replace(/((?:^\|.+?\|\s*\n)+)/gm, (table) => {
    const rows = table.trim().split('\n').map(r => r.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim()));
    if (rows.length < 2) return table;
    const header = rows[0];
    const body = rows.slice(2);
    return `<table><thead><tr>${header.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${body.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  });
}

function renderLists(s: string): string {
  const lines = s.split('\n');
  let out = '';
  let list: 'ul' | 'ol' | null = null;
  for (const line of lines) {
    const ulMatch = line.match(/^\s*[-*•🔹] (.+)$/);
    const olMatch = line.match(/^\s*\d+\. (.+)$/);
    if (ulMatch) {
      if (list !== 'ul') { if (list) out += `</${list}>`; out += '<ul>'; list = 'ul'; }
      out += `<li>${ulMatch[1]}</li>`;
    } else if (olMatch) {
      if (list !== 'ol') { if (list) out += `</${list}>`; out += '<ol>'; list = 'ol'; }
      out += `<li>${olMatch[1]}</li>`;
    } else {
      if (list) { out += `</${list}>`; list = null; }
      out += line + '\n';
    }
  }
  if (list) out += `</${list}>`;
  return out;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

