import { useState, useRef, useEffect } from 'react';
import { useApp } from '@/context/AppContext';
import { quickSuggestions } from '@/data/mock';
import { GraduationCap, Sparkles, Copy, Check, Share2, Download, RefreshCw, ThumbsUp, ThumbsDown, FileText } from 'lucide-react';
import type { Message } from '@/types';
import Markdown from './Markdown';
import RichCard from './RichCard';
import FollowUpChips from './FollowUpChips';
import HowRudraKnows from './HowRudraKnows';

export default function ChatWindow() {
  const { activeConversation, user, sendMessage } = useApp();
  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const messageCount = activeConversation?.messages.length ?? 0;
  const lastMessage = activeConversation?.messages[messageCount - 1];
  const isStreaming = lastMessage?.streaming;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: isStreaming ? 'auto' : 'smooth', block: 'end' });
  }, [messageCount, lastMessage?.content, isStreaming]);

  if (!activeConversation || activeConversation.messages.length === 0) {
    return <WelcomeScreen userName={user?.name ?? 'there'} onPick={(p) => sendMessage(p)} />;
  }

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto scroll-smooth">
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        {activeConversation.messages.map((m, i) => (
          <MessageBubble
            key={m.id}
            message={m}
            isLast={i === activeConversation.messages.length - 1}
            onFollowUp={sendMessage}
          />
        ))}
        <div ref={bottomRef} className="h-1" aria-hidden />
      </div>
    </div>
  );
}

function WelcomeScreen({ userName, onPick }: { userName: string; onPick: (prompt: string) => void }) {
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-3xl mx-auto px-4 py-10 flex flex-col items-center text-center animate-fade-in">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500 to-brand-800 flex items-center justify-center text-white shadow-app-lg mb-5 animate-float">
          <GraduationCap className="w-9 h-9" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold">{greeting}, {userName} 👋</h1>
        <p className="text-muted mt-2 text-base">How can I help you today?</p>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 mt-8 w-full">
          {quickSuggestions.map((s, i) => (
            <button
              key={s.id}
              onClick={() => onPick(s.prompt)}
              className="group flex flex-col items-center gap-2 p-3.5 rounded-2xl surface-2 border border-app hover:border-brand-500 hover:shadow-app hover:-translate-y-0.5 transition text-center animate-slide-up"
              style={{ animationDelay: `${i * 40}ms` }}
            >
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${s.color}`}>
                <IconByName name={s.icon} />
              </div>
              <span className="text-xs font-medium leading-tight">{s.label}</span>
            </button>
          ))}
        </div>

        <div className="mt-8 flex items-center gap-2 text-xs text-muted">
          <Sparkles className="w-3.5 h-3.5" />
          Ask anything about your campus — attendance, bus, placements, library, and more.
        </div>
      </div>
    </div>
  );
}

function MessageBubble({
  message,
  isLast,
  onFollowUp,
}: {
  message: Message;
  isLast: boolean;
  onFollowUp: (prompt: string) => void;
}) {
  const { regenerate, setFeedback } = useApp();
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const copy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  if (isUser) {
    return (
      <div className="flex justify-end animate-slide-up">
        <div className="max-w-[85%]">
          {message.attachments && message.attachments.length > 0 && (
            <div className="flex flex-wrap gap-2 justify-end mb-2">
              {message.attachments.map(a => (
                <div key={a.id} className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg surface-2 border border-app text-xs">
                  <FileText className="w-3.5 h-3.5 text-brand-600" />
                  <span className="truncate max-w-32">{a.name}</span>
                </div>
              ))}
            </div>
          )}
          <div className="px-4 py-3 rounded-2xl rounded-tr-md bg-brand-700 text-white text-sm leading-relaxed">
            {message.content}
          </div>
          <div className="text-[10px] text-muted text-right mt-1">{formatTime(message.createdAt)}</div>
        </div>
      </div>
    );
  }

  const showFollowups = isLast && !message.streaming && !!message.suggestedFollowups?.length;

  return (
    <div className="flex gap-3 animate-slide-up">
      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-brand-500 to-brand-800 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
        <GraduationCap className="w-4.5 h-4.5" />
      </div>
      <div className="flex-1 min-w-0">
        {message.agentName && !message.streaming && (
          <div className="text-[10px] font-semibold uppercase tracking-wide text-brand-600 mb-1 flex items-center gap-2 flex-wrap">
            <span>{message.agentName.replace(/_/g, ' ')} agent</span>
            {message.contextUsed && (
              <span className="normal-case font-normal text-brand-700 bg-brand-50 border border-brand-200 px-2 py-0.5 rounded-full flex items-center gap-1 text-[10px]">
                <Sparkles className="w-2.5 h-2.5 text-brand-600" />
                Using conversation context
              </span>
            )}
          </div>
        )}

        {message.streaming && !message.content ? (
          <TypingIndicator />
        ) : (
          <>
            <Markdown content={message.content} />
            {message.cards && message.cards.map((c, i) => <RichCard key={i} data={c} />)}
            {!message.streaming && <HowRudraKnows evidence={message.evidence} />}
          </>
        )}

        {showFollowups && (
          <FollowUpChips items={message.suggestedFollowups!} onPick={onFollowUp} />
        )}

        {!message.streaming && message.content && (
          <MessageActions
            copied={copied}
            onCopy={copy}
            onShare={() => navigator.share?.({ text: message.content }).catch(() => {})}
            onDownload={() => downloadText(message.content, 'response.md')}
            onRegenerate={() => regenerate(message.id)}
            feedback={message.feedback}
            onFeedback={(f) => setFeedback(message.id, f)}
          />
        )}
        <div className="text-[10px] text-muted mt-1">{formatTime(message.createdAt)}</div>
      </div>
    </div>
  );
}

function MessageActions({ copied, onCopy, onShare, onDownload, onRegenerate, feedback, onFeedback }: {
  copied: boolean; onCopy: () => void; onShare: () => void; onDownload: () => void; onRegenerate: () => void;
  feedback?: 'up' | 'down' | null; onFeedback: (f: 'up' | 'down') => void;
}) {
  return (
    <div className="flex items-center gap-1 mt-2 -ml-1.5 opacity-80 hover:opacity-100 transition">
      <ActionBtn onClick={onCopy} title="Copy" active={copied}>
        {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
      </ActionBtn>
      <ActionBtn onClick={onShare} title="Share"><Share2 className="w-3.5 h-3.5" /></ActionBtn>
      <ActionBtn onClick={onDownload} title="Download"><Download className="w-3.5 h-3.5" /></ActionBtn>
      <ActionBtn onClick={onRegenerate} title="Regenerate"><RefreshCw className="w-3.5 h-3.5" /></ActionBtn>
      <div className="w-px h-4 bg-app mx-1" />
      <ActionBtn onClick={() => onFeedback('up')} title="Good response" active={feedback === 'up'}>
        <ThumbsUp className="w-3.5 h-3.5" />
      </ActionBtn>
      <ActionBtn onClick={() => onFeedback('down')} title="Bad response" active={feedback === 'down'}>
        <ThumbsDown className="w-3.5 h-3.5" />
      </ActionBtn>
    </div>
  );
}

function ActionBtn({ children, onClick, title, active }: { children: React.ReactNode; onClick: () => void; title: string; active?: boolean }) {
  return (
    <button onClick={onClick} title={title} className={`p-1.5 rounded-lg hover:bg-app transition ${active ? 'text-brand-600' : 'text-muted hover:text-brand-600'}`}>
      {children}
    </button>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 py-2">
      <span className="typing-dot w-2 h-2 rounded-full bg-brand-500" />
      <span className="typing-dot w-2 h-2 rounded-full bg-brand-500" />
      <span className="typing-dot w-2 h-2 rounded-full bg-brand-500" />
    </div>
  );
}

function formatTime(t: number | string | undefined) {
  if (t == null) return '';
  const d = new Date(typeof t === 'number' ? t : t);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function downloadText(text: string, filename: string) {
  const blob = new Blob([text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

import * as Icons from 'lucide-react';
function IconByName({ name }: { name: string }) {
  const Cmp = (Icons as any)[name] ?? Icons.Sparkles;
  return <Cmp className="w-5 h-5" />;
}
