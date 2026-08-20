import { useEffect, useState } from 'react';
import { useApp, API_BASE_URL, authToken } from '@/context/AppContext';
import { buildAuthHeader } from '@/lib/firebase-auth';
import { sampleNotifications } from '@/data/mock';
import { X, Bell, CheckCheck, GraduationCap, Briefcase, BookCheck, Bus, FileText, PartyPopper, CalendarDays } from 'lucide-react';
import type { AppNotification } from '@/types';

const iconMap: Record<string, any> = {
  exam: GraduationCap, placement: Briefcase, attendance: BookCheck, bus: Bus,
  certificate: FileText, leave: CheckCheck, workshop: PartyPopper, event: CalendarDays,
};

const colorMap: Record<string, string> = {
  exam: 'text-rose-500 bg-rose-50 dark:bg-rose-500/10',
  placement: 'text-teal-500 bg-teal-50 dark:bg-teal-500/10',
  attendance: 'text-amber-500 bg-amber-50 dark:bg-amber-500/10',
  bus: 'text-sky-500 bg-sky-50 dark:bg-sky-500/10',
  certificate: 'text-orange-500 bg-orange-50 dark:bg-orange-500/10',
  leave: 'text-emerald-500 bg-emerald-50 dark:bg-emerald-500/10',
  workshop: 'text-pink-500 bg-pink-50 dark:bg-pink-500/10',
  event: 'text-violet-500 bg-violet-50 dark:bg-violet-500/10',
};

export default function NotificationsModal({ onClose }: { onClose: () => void }) {
  const { user } = useApp();
  const [items, setItems] = useState<AppNotification[]>(sampleNotifications);

  useEffect(() => {
    let active = true;
    async function loadNotifications() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/notifications`, {
          headers: { Authorization: await buildAuthHeader(authToken(user?.id)) }
        });
        if (res.ok) {
          const data = await res.json();
          if (active && Array.isArray(data.notifications) && data.notifications.length > 0) {
            const mapped: AppNotification[] = data.notifications.map((n: any) => ({
              id: n.id,
              title: n.title,
              body: n.message,
              time: n.sent_at ? new Date(n.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recently',
              type: (n.type as any) || 'event',
              read: !!n.read_at,
            }));
            setItems(mapped);
          }
        }
      } catch (e) {
        console.warn('Backend notifications fetch failed, using default notifications:', e);
      }
    }
    loadNotifications();
    return () => { active = false; };
  }, [user?.id]);

  const unread = items.filter(n => !n.read).length;

  const markAll = async () => {
    setItems(prev => prev.map(n => ({ ...n, read: true })));
    try {
      await fetch(`${API_BASE_URL}/api/notifications/read-all`, {
        method: 'PATCH',
        headers: { Authorization: await buildAuthHeader(authToken(user?.id)) }
      });
    } catch { /* ignore */ }
  };

  const toggle = async (id: string) => {
    const target = items.find(n => n.id === id);
    setItems(prev => prev.map(n => n.id === id ? { ...n, read: !n.read } : n));
    if (target && !target.read) {
      try {
        await fetch(`${API_BASE_URL}/api/notifications/${id}/read`, {
          method: 'PATCH',
          headers: { Authorization: await buildAuthHeader(authToken(user?.id)) }
        });
      } catch { /* ignore */ }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end p-4 pt-16 sm:p-6 sm:pt-16 animate-fade-in-fast" onClick={onClose}>
      <div className="absolute inset-0 bg-black/30" />
      <div className="relative w-full max-w-sm surface rounded-2xl border border-app shadow-app-lg overflow-hidden animate-scale-in max-h-[80vh] flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-app">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-brand-600" />
            <span className="font-semibold text-sm">Notifications</span>
            {unread > 0 && <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-rose-500 text-white">{unread} new</span>}
          </div>
          <div className="flex items-center gap-1">
            <button onClick={markAll} className="text-xs text-brand-600 hover:underline flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-app">
              <CheckCheck className="w-3.5 h-3.5" /> Mark all read
            </button>
            <button onClick={onClose} className="p-1 rounded-lg hover:bg-app text-muted"><X className="w-4 h-4" /></button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {items.map(n => {
            const Icon = iconMap[n.type] ?? Bell;
            return (
              <div key={n.id} onClick={() => toggle(n.id)} className={`flex gap-3 p-3 rounded-xl cursor-pointer transition ${n.read ? 'opacity-60' : ''} hover:bg-app`}>
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${colorMap[n.type]}`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="text-sm font-medium leading-snug">{n.title}</div>
                    {!n.read && <span className="w-2 h-2 rounded-full bg-rose-500 flex-shrink-0 mt-1.5" />}
                  </div>
                  <p className="text-xs text-muted mt-0.5 line-clamp-2">{n.body}</p>
                  <div className="text-[10px] text-muted mt-1">{n.time}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
