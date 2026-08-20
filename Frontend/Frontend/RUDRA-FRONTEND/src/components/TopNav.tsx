import { Menu, Search, Bell, Moon, Sun, PanelRight, GraduationCap } from 'lucide-react';
import { useApp } from '@/context/AppContext';

interface Props {
  onOpenSearch: () => void;
  onOpenNotifications: () => void;
  onOpenProfile: () => void;
  onOpenSettings: () => void;
}

export default function TopNav({ onOpenSearch, onOpenNotifications, onOpenProfile, onOpenSettings }: Props) {
  const { theme, toggleTheme, sidebarOpen, setSidebarOpen, rightPanelOpen, setRightPanelOpen, user } = useApp();

  return (
    <header className="h-14 flex items-center justify-between px-3 sm:px-4 glass border-b border-app sticky top-0 z-20">
      <div className="flex items-center gap-2">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 rounded-lg hover:bg-app text-muted transition">
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-brand-700 flex items-center justify-center text-white">
            <GraduationCap className="w-4.5 h-4.5" />
          </div>
          <div className="hidden sm:block">
            <div className="font-bold text-sm leading-tight">Rudra-AI</div>
            <div className="text-[10px] text-muted">Vasavi College of Engineering</div>
          </div>
        </div>
      </div>

      <button onClick={onOpenSearch} className="flex-1 max-w-md mx-4 flex items-center gap-2 px-3 py-2 rounded-xl surface-2 border border-app hover:border-brand-500 transition text-sm text-muted group">
        <Search className="w-4 h-4 group-hover:text-brand-600 transition" />
        <span className="hidden sm:inline">Search conversations, faculty, courses...</span>
        <span className="sm:hidden">Search...</span>
        <kbd className="ml-auto hidden sm:inline text-[10px] px-1.5 py-0.5 rounded border border-app">⌘K</kbd>
      </button>

      <div className="flex items-center gap-1">
        <button onClick={onOpenNotifications} className="relative p-2 rounded-lg hover:bg-app text-muted hover:text-brand-600 transition">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-[var(--surface)]" />
        </button>
        <button onClick={toggleTheme} className="p-2 rounded-lg hover:bg-app text-muted hover:text-brand-600 transition">
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        <button onClick={() => setRightPanelOpen(!rightPanelOpen)} className={`p-2 rounded-lg hover:bg-app transition ${rightPanelOpen ? 'text-brand-600' : 'text-muted'}`}>
          <PanelRight className="w-5 h-5" />
        </button>
        <button onClick={onOpenProfile} className="ml-1 w-8 h-8 rounded-full bg-brand-700 text-white flex items-center justify-center text-xs font-semibold hover:ring-2 hover:ring-brand-500/40 transition">
          {user?.name?.[0] ?? 'U'}
        </button>
      </div>
    </header>
  );
}
