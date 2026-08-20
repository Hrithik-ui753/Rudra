import { useEffect, useRef, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { AppProvider, useApp } from '@/context/AppContext';
import { AuthProvider } from '@/context/AuthContext';
import useAuth from '@/hooks/useAuth';
import AuthPage from '@/components/AuthPage';
import Sidebar from '@/components/Sidebar';
import TopNav from '@/components/TopNav';
import ChatWindow from '@/components/ChatWindow';
import PromptComposer from '@/components/PromptComposer';
import RightPanel from '@/components/RightPanel';
import MobileNav from '@/components/MobileNav';
import NotificationsModal from '@/components/NotificationsModal';
import SearchModal from '@/components/SearchModal';
import ProfileModal from '@/components/ProfileModal';
import SettingsModal from '@/components/SettingsModal';

type Modal = 'none' | 'search' | 'notifications' | 'profile' | 'settings';

function Workspace() {
  const { user, login } = useApp();
  const { currentUser, loading: authLoading } = useAuth();
  const [modal, setModal] = useState<Modal>('none');
  const restoredUid = useRef<string | null>(null);

  // Restore Firebase session once — no duplicate login loops
  useEffect(() => {
    if (!currentUser) {
      restoredUid.current = null;
      return;
    }
    if (user?.id === currentUser.uid) return;
    if (restoredUid.current === currentUser.uid) return;

    restoredUid.current = currentUser.uid;
    login({
      id: currentUser.uid,
      name: currentUser.displayName || 'Campus User',
      email: currentUser.email || '',
      avatar: currentUser.photoURL || undefined,
      role: currentUser.role,
      rollNo: currentUser.rollNo,
      branch: currentUser.branch,
      year: currentUser.year,
      semester: currentUser.semester,
      section: currentUser.section,
      language: currentUser.language,
    });
  }, [currentUser, user, login]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setModal(m => m === 'search' ? 'none' : 'search');
      }
      if (e.key === 'Escape') setModal('none');
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  if (authLoading) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center surface gap-3">
        <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
        <p className="text-sm text-muted font-medium">Checking session...</p>
      </div>
    );
  }

  if (!user) return <AuthPage />;

  return (
    <div className="h-screen flex overflow-hidden">
      <Sidebar onOpenSettings={() => setModal('settings')} onOpenProfile={() => setModal('profile')} />
      <div className="flex-1 flex flex-col min-w-0">
        <TopNav
          onOpenSearch={() => setModal('search')}
          onOpenNotifications={() => setModal('notifications')}
          onOpenProfile={() => setModal('profile')}
          onOpenSettings={() => setModal('settings')}
        />
        <ChatWindow />
        <PromptComposer />
      </div>
      <RightPanel />
      <MobileNav
        onOpenNotifications={() => setModal('notifications')}
        onOpenProfile={() => setModal('profile')}
      />

      {modal === 'search' && <SearchModal onClose={() => setModal('none')} />}
      {modal === 'notifications' && <NotificationsModal onClose={() => setModal('none')} />}
      {modal === 'profile' && <ProfileModal onClose={() => setModal('none')} />}
      {modal === 'settings' && <SettingsModal onClose={() => setModal('none')} onOpenProfile={() => setModal('profile')} />}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <Workspace />
      </AppProvider>
    </AuthProvider>
  );
}
