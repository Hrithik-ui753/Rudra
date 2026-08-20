import { useState, useRef, useEffect } from 'react';
import { Paperclip, Mic, Smile, Send, X, FileText, Image as ImageIcon } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import type { Attachment } from '@/types';
import { uid } from '@/data/responses';

const EMOJIS = ['😀','😄','😊','😎','🤔','😴','🥳','😇','🙂','🙌','👍','👏','✨','🔥','💡','📝','📚','🎓','🚌','📅','🏠','🎉','✅','❤️','🚀','💯','🤝','📌','⚡','🌟'];

export default function PromptComposer() {
  const { sendMessage } = useApp();
  const [text, setText] = useState('');
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [showEmoji, setShowEmoji] = useState(false);
  const [recording, setRecording] = useState(false);
  const [waveHeights, setWaveHeights] = useState<number[]>(Array(20).fill(0.3));
  const taRef = useRef<HTMLTextAreaElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  // Auto-expand textarea
  useEffect(() => {
    const ta = taRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 160) + 'px';
    }
  }, [text]);

  // Wave animation while recording
  useEffect(() => {
    if (!recording) return;
    const id = setInterval(() => {
      setWaveHeights(Array(20).fill(0).map(() => 0.2 + Math.random() * 0.8));
    }, 120);
    return () => clearInterval(id);
  }, [recording]);

  const submit = () => {
    if (!text.trim() && attachments.length === 0) return;
    sendMessage(text, attachments.length ? attachments : undefined);
    setText('');
    setAttachments([]);
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const onFiles = (files: FileList | null) => {
    if (!files) return;
    const next: Attachment[] = Array.from(files).slice(0, 5).map(f => ({
      id: uid('att'), name: f.name, type: f.type || 'file', size: f.size,
    }));
    setAttachments(prev => [...prev, ...next].slice(0, 8));
  };

  const toggleVoice = () => {
    if (recording) {
      setRecording(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        setRecording(true);

        recognition.onresult = (event: any) => {
          const transcript = event.results[0]?.[0]?.transcript;
          if (transcript) {
            setText(transcript);
          }
          setRecording(false);
        };

        recognition.onerror = () => {
          if (!text) setText('What is my timetable for today?');
          setRecording(false);
        };

        recognition.onend = () => {
          setRecording(false);
        };

        recognition.start();
        return;
      } catch {
        // Fallback below
      }
    }

    setRecording(true);
    setTimeout(() => {
      if (!text) {
        setText('What is my attendance in DBMS?');
      }
      setRecording(false);
    }, 2500);
  };

  return (
    <div className="px-3 sm:px-4 pb-4 pt-2">
      <div className="max-w-3xl mx-auto">
        {recording && (
          <div className="mb-2 flex items-center justify-center gap-1 h-12 rounded-2xl surface-2 border border-app animate-fade-in">
            {waveHeights.map((h, i) => (
              <div key={i} className="wave-bar w-1 rounded-full bg-rose-500" style={{ height: `${h * 32}px`, animationDelay: `${i * 50}ms` }} />
            ))}
            <span className="ml-3 text-xs text-rose-500 font-medium animate-pulse">Listening...</span>
          </div>
        )}

        {/* Attachment chips */}
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2 animate-fade-in">
            {attachments.map(a => (
              <div key={a.id} className="flex items-center gap-1.5 pl-2.5 pr-1.5 py-1.5 rounded-lg surface-2 border border-app text-xs group">
                {a.type.startsWith('image/') ? <ImageIcon className="w-3.5 h-3.5 text-brand-600" /> : <FileText className="w-3.5 h-3.5 text-brand-600" />}
                <span className="truncate max-w-36">{a.name}</span>
                <button onClick={() => setAttachments(prev => prev.filter(x => x.id !== a.id))} className="p-0.5 rounded hover:bg-app text-muted hover:text-rose-500 transition">
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Emoji picker */}
        {showEmoji && (
          <div className="mb-2 p-3 rounded-2xl surface-2 border border-app shadow-app animate-scale-in">
            <div className="grid grid-cols-10 gap-1">
              {EMOJIS.map(e => (
                <button key={e} onClick={() => { setText(t => t + e); setShowEmoji(false); taRef.current?.focus(); }} className="text-lg p-1.5 rounded hover:bg-app transition">
                  {e}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="relative flex items-end gap-2 p-2 rounded-2xl surface border border-app focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/20 transition shadow-app">
          <input ref={fileRef} type="file" multiple accept=".pdf,.doc,.docx,.xls,.xlsx,image/*" className="hidden" onChange={e => onFiles(e.target.files)} />

          <button onClick={() => fileRef.current?.click()} className="p-2 rounded-xl hover:bg-app text-muted hover:text-brand-600 transition flex-shrink-0" title="Attach files">
            <Paperclip className="w-5 h-5" />
          </button>

          <textarea
            ref={taRef}
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={onKey}
            rows={1}
            placeholder="Ask anything about your campus..."
            className="flex-1 resize-none bg-transparent outline-none text-sm py-2 max-h-40 leading-relaxed placeholder:text-muted"
          />

          <button onClick={() => setShowEmoji(s => !s)} className={`p-2 rounded-xl hover:bg-app transition flex-shrink-0 ${showEmoji ? 'text-brand-600' : 'text-muted hover:text-brand-600'}`} title="Emoji">
            <Smile className="w-5 h-5" />
          </button>

          <button onClick={toggleVoice} className={`p-2 rounded-xl transition flex-shrink-0 ${recording ? 'bg-rose-500 text-white animate-pulse' : 'hover:bg-app text-muted hover:text-brand-600'}`} title="Voice input">
            <Mic className="w-5 h-5" />
          </button>

          <button
            onClick={submit}
            disabled={!text.trim() && attachments.length === 0}
            className="p-2.5 rounded-xl bg-brand-700 text-white hover:bg-brand-800 disabled:opacity-40 disabled:cursor-not-allowed transition flex-shrink-0 group"
            title="Send"
          >
            <Send className="w-4.5 h-4.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition" />
          </button>
        </div>

        <div className="text-center text-[10px] text-muted mt-2">
          Rudra-AI can make mistakes. Verify important info with Vasavi College of Engineering official sources.
        </div>
      </div>
    </div>
  );
}
