import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode, type Dispatch, type SetStateAction } from 'react';
import type { CardData, Conversation, Evidence, Message, Role, User } from '@/types';
import { uid, ts, createUserMessage, createAssistantMessage, extractCardsFromBackendData } from '@/data/responses';
import { stripFollowupFooter, sleep } from '@/utils/chat';
import { buildAuthHeader } from '@/lib/firebase-auth';

type Theme = 'light' | 'dark';

interface AppState {
  user: User | null;
  theme: Theme;
  conversations: Conversation[];
  activeId: string | null;
  activeConversation: Conversation | null;
  sidebarOpen: boolean;
  rightPanelOpen: boolean;
  login: (user: User) => Promise<void>;
  logout: () => void;
  updateUser: (patch: Partial<User>) => void;
  toggleTheme: () => void;
  setTheme: (t: Theme) => void;
  newConversation: () => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, title: string) => void;
  togglePin: (id: string) => void;
  sendMessage: (text: string, attachments?: Message['attachments'], options?: { conversationId?: string; forceNew?: boolean }) => void;
  sendMessageInNewChat: (text: string) => void;
  regenerate: (messageId: string) => void;
  setFeedback: (messageId: string, feedback: 'up' | 'down') => void;
  setSidebarOpen: (v: boolean) => void;
  setRightPanelOpen: (v: boolean) => void;
}

const AppContext = createContext<AppState | null>(null);
const LS_KEY = 'smartcampus_state_v1';
export const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

export function authToken(userId?: string | null) {
  if (!userId) return 'Bearer user_guest';
  const cleanId = userId.startsWith('user_') ? userId : `user_${userId}`;
  return `Bearer ${cleanId}`;
}

function loadTheme(): Theme {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) {
      const data = JSON.parse(raw) as { theme?: Theme };
      if (data.theme === 'dark' || data.theme === 'light') return data.theme;
    }
  } catch { /* ignore */ }
  return 'light';
}

function persistTheme(theme: Theme) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify({ theme }));
  } catch { /* ignore */ }
}

function clearPersistedState() {
  try {
    localStorage.removeItem(LS_KEY);
  } catch { /* ignore */ }
}

type HistoryRow = {
  session_id?: string;
  id?: string;
  sender?: string;
  message?: string;
  created_at?: string;
  agent_name?: string;
  suggested_followups?: string[];
};

function parseFollowups(msg: HistoryRow): string[] {
  if (Array.isArray(msg.suggested_followups) && msg.suggested_followups.length) {
    return msg.suggested_followups.slice(0, 3);
  }
  return [];
}

async function streamAssistantReply(
  convId: string,
  msgId: string,
  fullText: string,
  meta: { suggestedFollowups?: string[]; agentName?: string; cards?: CardData[]; evidence?: Evidence[]; contextUsed?: boolean },
  setConversations: Dispatch<SetStateAction<Conversation[]>>,
) {
  const chunks = fullText.match(/\S+\s*|\s+/g) ?? [fullText];
  let acc = '';

  for (let i = 0; i < chunks.length; i++) {
    acc += chunks[i];
    const done = i === chunks.length - 1;
    setConversations(prev => prev.map(c => {
      if (c.id !== convId) return c;
      return {
        ...c,
        suggestedFollowups: done ? (meta.suggestedFollowups ?? []) : [],
        updatedAt: done ? ts() : c.updatedAt,
        messages: c.messages.map(m => m.id === msgId ? {
          ...m,
          content: acc,
          streaming: !done,
          suggestedFollowups: done ? meta.suggestedFollowups : undefined,
          agentName: meta.agentName,
          cards: meta.cards?.length ? meta.cards : m.cards,
          evidence: meta.evidence?.length ? meta.evidence : m.evidence,
          contextUsed: meta.contextUsed ?? m.contextUsed,
        } : m),
      };
    }));
    if (!done) await sleep(14);
  }
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [theme, setThemeState] = useState<Theme>(loadTheme);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const historyLoadedFor = useRef<string | null>(null);

  // Persist theme only — user/chats come from login + backend, not stale localStorage
  useEffect(() => {
    persistTheme(theme);
  }, [theme]);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') root.classList.add('dark');
    else root.classList.remove('dark');
  }, [theme]);

  useEffect(() => {
    const apply = () => {
      if (window.innerWidth < 1024) {
        setSidebarOpen(false);
        setRightPanelOpen(false);
      }
    };
    apply();
    window.addEventListener('resize', apply);
    return () => window.removeEventListener('resize', apply);
  }, []);

  const saveProfileToDb = useCallback(async (loggedInUser: User) => {
    try {
      await fetch(`${API_BASE_URL}/api/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: await buildAuthHeader(authToken(loggedInUser.id)),
        },
        body: JSON.stringify({
          name: loggedInUser.name,
          email: loggedInUser.email,
          role: loggedInUser.role,
          department: loggedInUser.department || loggedInUser.branch,
          branch: loggedInUser.branch || loggedInUser.department,
          roll_no: loggedInUser.rollNo,
          rollNo: loggedInUser.rollNo,
          year: loggedInUser.year,
          section: loggedInUser.section,
          phone: (loggedInUser as User & { phone?: string }).phone,
        }),
      });
    } catch (e) {
      console.warn('Profile save failed:', e);
    }
  }, []);

  const syncProfile = useCallback(async (loggedInUser: User) => {
    await saveProfileToDb(loggedInUser);
    try {
      const pRes = await fetch(`${API_BASE_URL}/api/profile`, {
        headers: { Authorization: await buildAuthHeader(authToken(loggedInUser.id)) }
      });
      if (!pRes.ok) return;
      const pData = await pRes.json();
      if (!pData?.name) return;

      setUser(prev => prev ? {
        ...prev,
        // Keep Firebase/local auth id — never replace with DB uuid
        name: pData.name,
        email: pData.email || prev.email,
        role: (pData.role as Role) || prev.role,
        department: pData.department || prev.department,
        branch: pData.department || prev.branch || prev.department,
        rollNo: pData.roll_no || prev.rollNo,
        year: pData.year || prev.year,
        section: pData.section || prev.section,
        phone: pData.phone || (prev as User & { phone?: string }).phone,
      } : prev);
    } catch (e) {
      console.warn('Profile sync failed:', e);
    }
  }, [saveProfileToDb]);

  const loadHistoryOnce = useCallback(async (loggedInUser: User) => {
    if (historyLoadedFor.current === loggedInUser.id) return;
    historyLoadedFor.current = loggedInUser.id;

    try {
      const hRes = await fetch(`${API_BASE_URL}/api/history`, {
        headers: { Authorization: await buildAuthHeader(authToken(loggedInUser.id)) }
      });
      if (!hRes.ok) return;

      const hData = await hRes.json();
      if (!hData?.messages?.length) return;

      const grouped: Record<string, Message[]> = {};
      hData.messages.forEach((msg: HistoryRow) => {
        const sid = msg.session_id || 'default_session';
        if (!grouped[sid]) grouped[sid] = [];
        const isAssistant = msg.sender !== 'user';
        const followups = isAssistant ? parseFollowups(msg) : undefined;
        grouped[sid].push({
          id: msg.id || uid('m'),
          role: isAssistant ? 'assistant' : 'user',
          content: isAssistant ? stripFollowupFooter(msg.message || '') : (msg.message || ''),
          createdAt: msg.created_at ? new Date(msg.created_at).getTime() : Date.now(),
          agentName: msg.agent_name,
          suggestedFollowups: followups,
        });
      });

      const loadedConvs: Conversation[] = Object.entries(grouped).map(([sid, msgs]) => {
        const lastAssistant = [...msgs].reverse().find(m => m.role === 'assistant');
        return {
          id: sid,
          title: msgs.find(m => m.role === 'user')?.content?.slice(0, 40) || 'Campus Assistant Chat',
          messages: msgs,
          createdAt: msgs[0]?.createdAt || Date.now(),
          updatedAt: msgs[msgs.length - 1]?.createdAt || Date.now(),
          suggestedFollowups: lastAssistant?.suggestedFollowups,
        };
      }).sort((a, b) => b.updatedAt - a.updatedAt);

      // Populate sidebar only — do NOT auto-switch the active chat
      setConversations(loadedConvs);
    } catch (e) {
      console.warn('History sync failed:', e);
    }
  }, []);

  const login = useCallback(async (u: User) => {
    historyLoadedFor.current = null;
    setConversations([]);
    setActiveId(null);
    setUser(u);
    await syncProfile(u);
    await loadHistoryOnce(u);
  }, [syncProfile, loadHistoryOnce]);

  const logout = useCallback(() => {
    historyLoadedFor.current = null;
    setUser(null);
    setConversations([]);
    setActiveId(null);
    clearPersistedState();
    persistTheme(theme);
  }, [theme]);

  const toggleTheme = useCallback(() => setThemeState(t => t === 'dark' ? 'light' : 'dark'), []);
  const setTheme = useCallback((t: Theme) => setThemeState(t), []);

  const updateUser = useCallback(async (patch: Partial<User>) => {
    setUser(u => u ? { ...u, ...patch } : u);
    const uidToUse = user?.id;
    if (!uidToUse) return;
    try {
      await fetch(`${API_BASE_URL}/api/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: await buildAuthHeader(authToken(uidToUse)),
        },
        body: JSON.stringify({
          name: patch.name,
          email: patch.email,
          role: patch.role,
          department: patch.department || patch.branch,
          branch: patch.branch || patch.department,
          roll_no: patch.rollNo,
          rollNo: patch.rollNo,
          phone: (patch as Partial<User & { phone?: string }>).phone,
          year: patch.year,
          section: patch.section,
        }),
      });
    } catch (e) {
      console.warn('Failed to sync profile update to backend:', e);
    }
  }, [user?.id]);

  const newConversation = useCallback(() => {
    const id = uid('c');
    const conv: Conversation = {
      id, title: 'New Chat', messages: [], createdAt: ts(), updatedAt: ts(),
    };
    setConversations(prev => [conv, ...prev]);
    setActiveId(id);
    if (window.innerWidth < 1024) setSidebarOpen(false);
  }, []);

  const selectConversation = useCallback((id: string) => {
    setActiveId(id);
    if (window.innerWidth < 1024) setSidebarOpen(false);
  }, []);

  const deleteConversation = useCallback((id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    setActiveId(curr => curr === id ? null : curr);
  }, []);

  const renameConversation = useCallback((id: string, title: string) => {
    setConversations(prev => prev.map(c => c.id === id ? { ...c, title } : c));
  }, []);

  const togglePin = useCallback((id: string) => {
    setConversations(prev => prev.map(c => c.id === id ? { ...c, pinned: !c.pinned } : c));
  }, []);

  const sendMessage = useCallback(async (
    text: string,
    attachments?: Message['attachments'],
    options?: { conversationId?: string; forceNew?: boolean }
  ) => {
    if (!text.trim() && !attachments?.length) return;
    if (!user?.id) return;

    let currentConvId = options?.conversationId;

    if (options?.forceNew) {
      currentConvId = uid('c');
      const title = text.slice(0, 40) || 'New Chat';
      setConversations(prev => [{
        id: currentConvId!,
        title,
        messages: [],
        createdAt: ts(),
        updatedAt: ts(),
      }, ...prev]);
      setActiveId(currentConvId);
    } else {
      if (!currentConvId) currentConvId = activeId ?? undefined;
      if (!currentConvId || !conversations.some(c => c.id === currentConvId)) {
        currentConvId = uid('c');
        const title = text.slice(0, 40) || 'New Chat';
        setConversations(prev => [{
          id: currentConvId!,
          title,
          messages: [],
          createdAt: ts(),
          updatedAt: ts(),
        }, ...prev]);
      }
      setActiveId(currentConvId);
    }

    const userMsg = createUserMessage(text, attachments);
    const assistantMsg = createAssistantMessage('', undefined);
    const assistantMsgId = assistantMsg.id;

    setConversations(prev => {
      const existingIdx = prev.findIndex(c => c.id === currentConvId);
      if (existingIdx >= 0) {
        return prev.map((c, idx) => idx === existingIdx ? {
          ...c,
          title: c.messages.length === 0 ? (text.slice(0, 40) || c.title) : c.title,
          suggestedFollowups: [],
          messages: [...c.messages, userMsg, assistantMsg],
          updatedAt: ts(),
        } : c);
      }
      const title = text.slice(0, 40) || 'New Chat';
      return [{
        id: currentConvId!,
        title,
        messages: [userMsg, assistantMsg],
        createdAt: ts(),
        updatedAt: ts(),
      }, ...prev];
    });

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: await buildAuthHeader(authToken(user.id)),
        },
        body: JSON.stringify({ query: text, session_id: currentConvId }),
      });

      if (res.ok) {
        const data = await res.json();
        const responseText = stripFollowupFooter(data.response || 'No response generated.');
        const followups = Array.isArray(data.suggested_followups) ? data.suggested_followups.slice(0, 3) : [];
        const cards = extractCardsFromBackendData(data.raw_data, text);

        await streamAssistantReply(
          currentConvId!,
          assistantMsgId,
          responseText,
          { suggestedFollowups: followups, agentName: data.agent_name, cards, evidence: data.evidence, contextUsed: data.context_used },
          setConversations,
        );
      } else {
        throw new Error(`Backend HTTP ${res.status}`);
      }
    } catch (err) {
      console.error('Backend chat failed:', err);
      const errMsg = err instanceof Error ? err.message : 'Connection failed';
      setConversations(prev => prev.map(c => {
        if (c.id !== currentConvId) return c;
        return {
          ...c,
          messages: c.messages.map(m => m.id === assistantMsgId ? {
            ...m,
            content: `⚠️ **Backend connection failed.** Ensure server is running at \`${API_BASE_URL}\`.\n\n> ${errMsg}`,
            streaming: false,
          } : m),
        };
      }));
    }
  }, [activeId, conversations, user]);

  const sendMessageInNewChat = useCallback((text: string) => {
    sendMessage(text, undefined, { forceNew: true });
  }, [sendMessage]);

  const regenerate = useCallback(async (messageId: string) => {
    if (!activeId || !user?.id) return;
    const conv = conversations.find(c => c.id === activeId);
    if (!conv) return;
    const idx = conv.messages.findIndex(m => m.id === messageId);
    if (idx < 0) return;
    const userMsg = conv.messages[idx - 1];
    const queryText = userMsg?.content ?? '';
    if (!queryText.trim()) return;

    setConversations(prev => prev.map(c => {
      if (c.id !== activeId) return c;
      return {
        ...c,
        suggestedFollowups: [],
        messages: c.messages.map((m, i) => i === idx ? { ...m, content: '', streaming: true, feedback: null, suggestedFollowups: undefined } : m),
      };
    }));

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: await buildAuthHeader(authToken(user.id)),
        },
        body: JSON.stringify({ query: queryText, session_id: activeId }),
      });
      if (res.ok) {
        const data = await res.json();
        const responseText = stripFollowupFooter(data.response || 'No response.');
        const followups = Array.isArray(data.suggested_followups) ? data.suggested_followups.slice(0, 3) : [];
        const cards = extractCardsFromBackendData(data.raw_data, queryText);
        await streamAssistantReply(
          activeId,
          messageId,
          responseText,
          { suggestedFollowups: followups, agentName: data.agent_name, cards, evidence: data.evidence },
          setConversations,
        );
        return;
      }
    } catch (e) {
      console.warn('Regenerate backend failed:', e);
    }

    setConversations(prev => prev.map(c => {
      if (c.id !== activeId) return c;
      return {
        ...c,
        messages: c.messages.map((m, i) => i === idx ? {
          ...m,
          content: '⚠️ **Could not fetch a verified response.** Please ensure the backend is running and try again.',
          streaming: false,
          suggestedFollowups: [],
        } : m),
      };
    }));
  }, [activeId, conversations, user]);

  const setFeedback = useCallback((messageId: string, feedback: 'up' | 'down') => {
    setConversations(prev => prev.map(c => {
      if (c.id !== activeId) return c;
      return {
        ...c,
        messages: c.messages.map(m => m.id === messageId ? { ...m, feedback } : m),
      };
    }));
  }, [activeId]);

  const activeConversation = useMemo(
    () => conversations.find(c => c.id === activeId) ?? null,
    [conversations, activeId]
  );

  const value = useMemo<AppState>(() => ({
    user, theme, conversations, activeId, activeConversation,
    sidebarOpen, rightPanelOpen,
    login, logout, updateUser, toggleTheme, setTheme,
    newConversation, selectConversation, deleteConversation, renameConversation, togglePin,
    sendMessage, sendMessageInNewChat, regenerate, setFeedback, setSidebarOpen, setRightPanelOpen,
  }), [
    user, theme, conversations, activeId, activeConversation,
    sidebarOpen, rightPanelOpen,
    login, logout, updateUser, toggleTheme, setTheme,
    newConversation, selectConversation, deleteConversation, renameConversation, togglePin,
    sendMessage, sendMessageInNewChat, regenerate, setFeedback,
  ]);

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
