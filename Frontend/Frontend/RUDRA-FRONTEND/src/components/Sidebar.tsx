import { useState, useMemo } from 'react';
import { Plus, Search, Pin, MoreHorizontal, Trash2, Pencil, X, Check, Settings, LogOut, GraduationCap, MessageSquare } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import useAuth from '@/hooks/useAuth';

interface SidebarProps {
  onOpenSettings: () => void;
  onOpenProfile: () => void;
}

export default function Sidebar({ onOpenSettings, onOpenProfile }: SidebarProps) {
  const { conversations, activeId, selectConversation, newConversation, deleteConversation, renameConversation, togglePin, user, logout: appLogout, sidebarOpen, setSidebarOpen } = useApp();
  const { logout: firebaseLogout } = useAuth();
  const [query, setQuery] = useState('');
  const [menuId, setMenuId] = useState<string | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameVal, setRenameVal] = useState('');

  const handleLogout = async () => {
    try {
      await firebaseLogout();
    } catch {
      // Ignore auth logout error if any
    }
    appLogout();
  };

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return conversations;
    return conversations.filter(c =>
      c.title.toLowerCase().includes(q) ||
      c.messages.some(m => m.content.toLowerCase().includes(q))
    );
  }, [conversations, query]);

  const pinned = filtered.filter(c => c.pinned);
  const getMs = (val: number | string) => {
    if (typeof val === 'number') return val;
    const parsed = new Date(val).getTime();
    return isNaN(parsed) ? Date.now() : parsed;
  };

  const now = Date.now();
  const today = filtered.filter(c => !c.pinned && now - getMs(c.updatedAt) < 86400000);
  const yesterday = filtered.filter(c => !c.pinned && now - getMs(c.updatedAt) >= 86400000 && now - getMs(c.updatedAt) < 172800000);
  const prev7 = filtered.filter(c => !c.pinned && now - getMs(c.updatedAt) >= 172800000 && now - getMs(c.updatedAt) < 604800000);
  const older = filtered.filter(c => !c.pinned && now - getMs(c.updatedAt) >= 604800000);

  const groups = [
    { label: 'Pinned', items: pinned },
    { label: 'Today', items: today },
    { label: 'Yesterday', items: yesterday },
    { label: 'Previous 7 Days', items: prev7 },
    { label: 'Older', items: older },
  ].filter(g => g.items.length > 0);


  return (
    <>
      {sidebarOpen && <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={() => setSidebarOpen(false)} />}

      <aside className={`
        fixed lg:static z-40 h-full w-72 flex-shrink-0 surface border-r border-app flex flex-col
        transition-transform duration-300
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:hidden'}
      `}>
        {/* Header */}
        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-brand-700 flex items-center justify-center text-white">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div className="font-bold text-sm leading-tight">
              Rudra-AI
              <div className="text-[10px] text-muted font-normal">Vasavi College of Engineering</div>
            </div>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-muted hover:text-brand-600 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* New chat */}
        <div className="px-3">
          <button onClick={newConversation} className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl bg-brand-700 hover:bg-brand-800 text-white text-sm font-medium transition group">
            <Plus className="w-4 h-4 group-hover:rotate-90 transition" />
            New Chat
          </button>
        </div>

        {/* Search */}
        <div className="px-3 mt-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search chats & messages"
              className="w-full pl-9 pr-3 py-2 rounded-lg surface-2 border border-app focus:border-brand-500 outline-none text-sm"
            />
          </div>
        </div>

        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto px-2 mt-2 pb-2 space-y-3">
          {groups.length === 0 && (
            <div className="text-center text-muted text-xs py-10">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-40" />
              No conversations yet.
            </div>
          )}
          {groups.map(g => (
            <div key={g.label}>
              <div className="px-2 py-1.5 text-[11px] font-semibold text-muted uppercase tracking-wide flex items-center gap-1">
                {g.label === 'Pinned' && <Pin className="w-3 h-3" />}
                {g.label}
              </div>
              <div className="space-y-0.5">
                {g.items.map(c => (
                  <div
                    key={c.id}
                    className={`group relative flex items-center gap-2 px-2.5 py-2 rounded-lg cursor-pointer transition ${activeId === c.id ? 'bg-brand-50 dark:bg-brand-700/15 text-brand-700 dark:text-brand-300' : 'hover:bg-app surface-2'}`}
                    onClick={() => selectConversation(c.id)}
                  >
                    {renamingId === c.id ? (
                      <input
                        autoFocus
                        value={renameVal}
                        onChange={e => setRenameVal(e.target.value)}
                        onClick={e => e.stopPropagation()}
                        onKeyDown={e => {
                          if (e.key === 'Enter') { renameConversation(c.id, renameVal); setRenamingId(null); }
                          if (e.key === 'Escape') setRenamingId(null);
                        }}
                        className="flex-1 bg-transparent border border-brand-500 rounded px-1 py-0.5 text-sm outline-none"
                      />
                    ) : (
                      <span className="flex-1 truncate text-sm">{c.title}</span>
                    )}

                    {renamingId === c.id ? (
                      <button onClick={(e) => { e.stopPropagation(); renameConversation(c.id, renameVal); setRenamingId(null); }} className="text-emerald-500 hover:text-emerald-600 p-1">
                        <Check className="w-3.5 h-3.5" />
                      </button>
                    ) : (
                      <button onClick={(e) => { e.stopPropagation(); setMenuId(menuId === c.id ? null : c.id); }} className="opacity-0 group-hover:opacity-100 text-muted hover:text-brand-600 p-1 transition">
                        <MoreHorizontal className="w-4 h-4" />
                      </button>
                    )}

                    {menuId === c.id && (
                      <div className="absolute right-0 top-9 z-10 w-36 surface border border-app rounded-lg shadow-app-lg py-1 text-sm animate-scale-in" onClick={e => e.stopPropagation()}>
                        <button onClick={() => { togglePin(c.id); setMenuId(null); }} className="w-full flex items-center gap-2 px-3 py-1.5 hover:bg-app">
                          <Pin className="w-3.5 h-3.5" /> {c.pinned ? 'Unpin' : 'Pin'}
                        </button>
                        <button onClick={() => { setRenamingId(c.id); setRenameVal(c.title); setMenuId(null); }} className="w-full flex items-center gap-2 px-3 py-1.5 hover:bg-app">
                          <Pencil className="w-3.5 h-3.5" /> Rename
                        </button>
                        <button onClick={() => { deleteConversation(c.id); setMenuId(null); }} className="w-full flex items-center gap-2 px-3 py-1.5 hover:bg-app text-rose-500">
                          <Trash2 className="w-3.5 h-3.5" /> Delete
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="border-t border-app p-3 space-y-1">
          <button onClick={onOpenProfile} className="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-app surface-2 cursor-pointer w-full text-left">
            <div className="w-8 h-8 rounded-full bg-brand-700 text-white flex items-center justify-center text-xs font-semibold">
              {user?.name?.[0] ?? 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{user?.name}</div>
              <div className="text-[11px] text-muted truncate">
                {user?.role === 'student'
                  ? `${user.rollNo ? `${user.rollNo} · ` : ''}${user.branch || 'Student'}`
                  : user?.role === 'faculty'
                  ? `${user.teacherId ? `${user.teacherId} · ` : ''}${user.department || 'Faculty'}`
                  : user?.role}
              </div>
            </div>
          </button>
          <button onClick={onOpenSettings} className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-app surface-2 text-sm text-muted transition">
            <Settings className="w-4 h-4" /> Settings
          </button>
          <button onClick={handleLogout} className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-500/10 text-sm text-rose-500 transition">
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </aside>
    </>
  );
}
