import { useEffect, useState } from 'react';
import { CalendarDays, Bell, Upload, ScrollText, Bus, Link2, Clock, X } from 'lucide-react';
import { useApp, API_BASE_URL, authToken } from '@/context/AppContext';
import { buildAuthHeader } from '@/lib/firebase-auth';
import { upcomingEvents, todaySchedule, recentCirculars, helpfulLinks } from '@/data/mock';

const iconMap: Record<string, any> = { CalendarDays, Bell, Upload, ScrollText, Bus, Link2, ExternalLink: Link2, Download: Link2, Phone: Link2, MessageSquare: Link2 };

export default function RightPanel() {
  const { rightPanelOpen, setRightPanelOpen, user } = useApp();
  const [events, setEvents] = useState<any[]>(upcomingEvents);

  useEffect(() => {
    let active = true;
    async function fetchBackendEvents() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/events`, {
          headers: { Authorization: await buildAuthHeader(authToken(user?.id)) }
        });
        if (res.ok) {
          const data = await res.json();
          if (active && Array.isArray(data.events) && data.events.length > 0) {
            const mapped = data.events.slice(0, 4).map((e: any) => ({
              id: e.id || `evt-${Math.random()}`,
              date: e.date ? `${e.date.split('-')[1] || 'AUG'} ${e.date.split('-')[2] || '15'}` : 'AUG 15',
              title: e.title || 'Campus Event',
              time: e.start_time || '09:30 AM',
              venue: e.location || 'Campus',
              tag: e.category || 'Academic'
            }));
            setEvents(mapped);
          }
        }
      } catch (err) {
        console.warn('Backend events fetch failed, using default events:', err);
      }
    }
    fetchBackendEvents();
    return () => { active = false; };
  }, [user?.id]);

  if (!rightPanelOpen) return null;

  return (
    <aside className="hidden xl:flex w-80 flex-shrink-0 surface border-l border-app flex-col animate-slide-in-right">
      <div className="h-14 flex items-center justify-between px-4 border-b border-app">
        <div className="font-semibold text-sm">Campus Context</div>
        <button onClick={() => setRightPanelOpen(false)} className="text-muted hover:text-brand-600 p-1">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Today's Schedule */}
        <Section icon={Clock} title="Today's Schedule" accent="text-brand-600">
          <div className="space-y-2">
            {todaySchedule.map(s => (
              <div key={s.id} className="flex gap-3 p-2.5 rounded-lg surface-2 border border-app hover:border-brand-500 transition">
                <div className="text-xs font-mono text-muted pt-0.5 w-12">{s.time}</div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{s.course}</div>
                  <div className="text-[11px] text-muted">{s.room} · {s.faculty}</div>
                </div>
              </div>
            ))}
          </div>
        </Section>

        {/* Upcoming Events */}
        <Section icon={CalendarDays} title="Upcoming Events" accent="text-accent-500">
          <div className="space-y-2">
            {events.slice(0, 3).map(e => (
              <div key={e.id} className="p-2.5 rounded-lg surface-2 border border-app hover:border-brand-500 transition">
                <div className="flex items-start gap-3">
                  <div className="flex flex-col items-center justify-center w-10 h-10 rounded-lg bg-brand-50 dark:bg-brand-700/15 text-brand-700 dark:text-brand-300 flex-shrink-0">
                    <span className="text-[9px] uppercase">{e.date.split(' ')[0]}</span>
                    <span className="text-sm font-bold leading-none">{e.date.split(' ')[1]}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">{e.title}</div>
                    <div className="text-[11px] text-muted">{e.time} · {e.venue}</div>
                    <span className="inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-accent-100 dark:bg-accent-500/15 text-accent-700 dark:text-accent-300">{e.tag}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Section>

        {/* Recent Circulars */}
        <Section icon={ScrollText} title="Recent Circulars" accent="text-rose-500">
          <div className="space-y-2">
            {recentCirculars.map(c => (
              <div key={c.id} className="p-2.5 rounded-lg surface-2 border border-app hover:border-brand-500 transition">
                <div className="text-sm font-medium leading-snug">{c.title}</div>
                <div className="text-[11px] text-muted mt-0.5">{c.ref} · {c.date}</div>
              </div>
            ))}
          </div>
        </Section>

        {/* Helpful Links */}
        <Section icon={Link2} title="Helpful Links" accent="text-sky-500">
          <div className="grid grid-cols-1 gap-1.5">
            {helpfulLinks.map(l => {
              const Icon = iconMap[l.icon] ?? Link2;
              return (
                <button key={l.id} className="flex items-center gap-2 p-2 rounded-lg surface-2 border border-app hover:border-brand-500 transition text-left text-sm">
                  <Icon className="w-4 h-4 text-muted" />
                  <span className="flex-1">{l.label}</span>
                </button>
              );
            })}
          </div>
        </Section>
      </div>
    </aside>
  );
}

function Section({ icon: Icon, title, accent, children }: { icon: any; title: string; accent: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${accent}`} />
        <div className="text-xs font-semibold uppercase tracking-wide text-muted">{title}</div>
      </div>
      {children}
    </div>
  );
}
