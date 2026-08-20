import { MessageSquare, Bell, CalendarDays, User } from 'lucide-react';
import { useApp } from '@/context/AppContext';

interface Props {
  onOpenNotifications: () => void;
  onOpenProfile: () => void;
}

export default function MobileNav({ onOpenNotifications, onOpenProfile }: Props) {
  const { newConversation, setSidebarOpen, setRightPanelOpen } = useApp();

  return (
    <nav className="lg:hidden fixed bottom-0 inset-x-0 z-20 glass border-t border-app flex items-center justify-around py-2 px-2">
      <button onClick={() => setSidebarOpen(true)} className="flex flex-col items-center gap-0.5 p-2 text-muted hover:text-brand-600 transition">
        <MessageSquare className="w-5 h-5" />
        <span className="text-[10px]">Chats</span>
      </button>
      <button onClick={newConversation} className="flex flex-col items-center gap-0.5 p-2 text-brand-600">
        <div className="w-10 h-10 -mt-6 rounded-full bg-brand-700 text-white flex items-center justify-center shadow-app-lg">
          <MessageSquare className="w-5 h-5" />
        </div>
        <span className="text-[10px]">New</span>
      </button>
      <button onClick={onOpenNotifications} className="flex flex-col items-center gap-0.5 p-2 text-muted hover:text-brand-600 transition relative">
        <Bell className="w-5 h-5" />
        <span className="text-[10px]">Alerts</span>
        <span className="absolute top-1 right-3 w-2 h-2 rounded-full bg-rose-500" />
      </button>
      <button onClick={onOpenProfile} className="flex flex-col items-center gap-0.5 p-2 text-muted hover:text-brand-600 transition">
        <User className="w-5 h-5" />
        <span className="text-[10px]">Profile</span>
      </button>
    </nav>
  );
}
