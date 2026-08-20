import { useState, useMemo, useEffect, useRef } from 'react';
import { Search, X, MessageSquare, ArrowRight, Plus } from 'lucide-react';
import { useApp } from '@/context/AppContext';

type SearchResult = {
  id: string;
  label: string;
  sub: string;
  type: 'chat' | 'message' | 'new';
  conversationId?: string;
};

export default function SearchModal({ onClose }: { onClose: () => void }) {
  const { conversations, selectConversation, sendMessageInNewChat } = useApp();
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    const items: SearchResult[] = [];

    if (!q) {
      conversations.slice(0, 8).forEach(c => {
        items.push({ id: c.id, label: c.title, sub: `${c.messages.length} messages`, type: 'chat', conversationId: c.id });
      });
      return items;
    }

    conversations.forEach(c => {
      if (c.title.toLowerCase().includes(q)) {
        items.push({ id: `chat-${c.id}`, label: c.title, sub: 'Conversation', type: 'chat', conversationId: c.id });
      }
      c.messages.forEach(m => {
        if (m.content.toLowerCase().includes(q)) {
          items.push({
            id: `msg-${c.id}-${m.id}`,
            label: m.content.slice(0, 60),
            sub: `In: ${c.title}`,
            type: 'message',
            conversationId: c.id,
          });
        }
      });
    });

    items.push({ id: 'new-ask', label: `Ask: "${query.trim()}"`, sub: 'Start new chat', type: 'new' });
    return items.slice(0, 20);
  }, [query, conversations]);

  const pick = (item: SearchResult) => {
    if (item.type === 'new') {
      sendMessageInNewChat(query.trim());
    } else if (item.conversationId) {
      selectConversation(item.conversationId);
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-[10vh] animate-fade-in-fast" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div className="relative w-full max-w-xl surface rounded-2xl border border-app shadow-app-lg overflow-hidden animate-scale-in" onClick={e => e.stopPropagation()}>
        <div className="flex items-center gap-3 p-3 border-b border-app">
          <Search className="w-5 h-5 text-muted" />
          <input
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && query.trim()) {
                sendMessageInNewChat(query.trim());
                onClose();
              }
            }}
            placeholder="Search your chats and messages..."
            className="flex-1 bg-transparent outline-none text-sm"
          />
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-app text-muted"><X className="w-4 h-4" /></button>
        </div>
        <div className="max-h-[50vh] overflow-y-auto p-2">
          {results.length === 0 ? (
            <div className="text-center text-muted text-sm py-8">No matching chats or messages</div>
          ) : (
            results.map(r => {
              const Icon = r.type === 'new' ? Plus : MessageSquare;
              return (
                <button key={r.id} onClick={() => pick(r)} className="w-full flex items-center gap-3 p-2.5 rounded-xl hover:bg-app transition text-left group">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-brand-600 bg-brand-50 dark:bg-brand-700/10">
                    <Icon className="w-4.5 h-4.5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">{r.label}</div>
                    <div className="text-[11px] text-muted truncate">{r.sub}</div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-muted opacity-0 group-hover:opacity-100 transition" />
                </button>
              );
            })
          )}
        </div>
        <div className="p-2 border-t border-app flex items-center justify-between text-[11px] text-muted">
          <span>{results.length} results from your saved chats</span>
          <span>Enter = new chat · Click = open chat</span>
        </div>
      </div>
    </div>
  );
}
