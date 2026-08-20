import { useState } from 'react';
import { X, Moon, Globe, Mic, Bell, Download, Trash2, LogOut, Check, ChevronRight } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import useAuth from '@/hooks/useAuth';

export default function SettingsModal({ onClose, onOpenProfile }: { onClose: () => void; onOpenProfile: () => void }) {
  const { theme, setTheme, logout: appLogout, user } = useApp();
  const { logout: firebaseLogout } = useAuth();
  const [prefs, setPrefs] = useState({ exam: true, workshop: true, placement: true, attendance: true, bus: true, certificate: true });
  const [exported, setExported] = useState(false);
  const [cleared, setCleared] = useState(false);

  const exportChat = () => { setExported(true); setTimeout(() => setExported(false), 1500); };
  const clearChat = () => { setCleared(true); setTimeout(() => setCleared(false), 1500); };

  const handleLogout = async () => {
    try { await firebaseLogout(); } catch { /* ignore */ }
    appLogout();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in-fast" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div className="relative w-full max-w-lg surface rounded-2xl border border-app shadow-app-lg overflow-hidden animate-scale-in max-h-[88vh] flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-app">
          <span className="font-semibold text-sm">Settings</span>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-app text-muted"><X className="w-4 h-4" /></button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-5">
          {/* Appearance */}
          <Group title="Appearance">
            <Row icon={Moon} label="Dark Mode">
              <Toggle on={theme === 'dark'} onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} />
            </Row>
          </Group>

          {/* Preferences */}
          <Group title="Preferences">
            <Row icon={Globe} label="Language" value="English" onClick={() => onOpenProfile()} />
            <Row icon={Mic} label="Voice Input" value="Enabled" />
          </Group>

          {/* Notifications */}
          <Group title="Notification Preferences">
            <div className="grid grid-cols-2 gap-2">
              {[
                { key: 'exam', label: 'Exam Reminders' },
                { key: 'workshop', label: 'Workshops' },
                { key: 'placement', label: 'Placement Deadlines' },
                { key: 'attendance', label: 'Attendance Warnings' },
                { key: 'bus', label: 'Bus Delays' },
                { key: 'certificate', label: 'Certificate Updates' },
              ].map(n => (
                <div key={n.key} className="flex items-center justify-between p-2.5 rounded-xl surface-2 border border-app">
                  <span className="text-xs flex items-center gap-1.5"><Bell className="w-3.5 h-3.5 text-muted" />{n.label}</span>
                  <Toggle on={(prefs as any)[n.key]} onClick={() => setPrefs(p => ({ ...p, [n.key]: !(p as any)[n.key] }))} />
                </div>
              ))}
            </div>
          </Group>

          {/* Data */}
          <Group title="Data Management">
            <button onClick={exportChat} className="w-full flex items-center justify-between p-3 rounded-xl surface-2 border border-app hover:border-brand-500 transition text-left">
              <span className="text-sm flex items-center gap-2"><Download className="w-4 h-4 text-brand-600" /> Export Chat History</span>
              {exported ? <Check className="w-4 h-4 text-emerald-500" /> : <ChevronRight className="w-4 h-4 text-muted" />}
            </button>
            <button onClick={clearChat} className="w-full flex items-center justify-between p-3 rounded-xl surface-2 border border-app hover:border-rose-400 transition text-left">
              <span className="text-sm flex items-center gap-2 text-rose-500"><Trash2 className="w-4 h-4" /> Clear Chat History</span>
              {cleared ? <Check className="w-4 h-4 text-emerald-500" /> : <ChevronRight className="w-4 h-4 text-muted" />}
            </button>
          </Group>

          {/* Account */}
          <Group title="Account">
            <button onClick={onOpenProfile} className="w-full flex items-center justify-between p-3 rounded-xl surface-2 border border-app hover:border-brand-500 transition text-left">
              <span className="text-sm">Edit Profile</span>
              <ChevronRight className="w-4 h-4 text-muted" />
            </button>
            <button onClick={handleLogout} className="w-full flex items-center justify-between p-3 rounded-xl surface-2 border border-app hover:border-rose-400 transition text-left">
              <span className="text-sm flex items-center gap-2 text-rose-500"><LogOut className="w-4 h-4" /> Logout {user?.email ? `(${user.email})` : ''}</span>
              <ChevronRight className="w-4 h-4 text-muted" />
            </button>
          </Group>
        </div>
      </div>
    </div>
  );
}

function Group({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-[11px] font-semibold uppercase tracking-wide text-muted mb-2">{title}</div>
      <div className="space-y-1.5">{children}</div>
    </div>
  );
}

function Row({ icon: Icon, label, value, onClick, children }: { icon: any; label: string; value?: string; onClick?: () => void; children?: React.ReactNode }) {
  return (
    <button onClick={onClick} className="w-full flex items-center justify-between p-3 rounded-xl surface-2 border border-app hover:border-brand-500 transition text-left">
      <span className="text-sm flex items-center gap-2"><Icon className="w-4 h-4 text-muted" />{label}</span>
      {children ?? <span className="text-xs text-muted flex items-center gap-1">{value} <ChevronRight className="w-3.5 h-3.5" /></span>}
    </button>
  );
}

function Toggle({ on, onClick }: { on: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`w-10 h-6 rounded-full transition relative ${on ? 'bg-brand-600' : 'bg-app border border-app'}`}>
      <span className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition ${on ? 'left-[18px]' : 'left-0.5'}`} />
    </button>
  );
}
