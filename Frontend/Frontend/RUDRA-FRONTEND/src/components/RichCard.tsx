import { useState } from 'react';
import type { CardData } from '@/types';
import {
  Bus, Clock, MapPin, BookCheck, AlertTriangle, Users, Mail, DoorOpen, GraduationCap,
  CalendarDays, BookOpen, BookMarked, ScrollText, FileText, Building2, CheckCircle2,
  Download, RefreshCw, ArrowRight, PartyPopper, IndianRupee, Briefcase, Bell, Check,
} from 'lucide-react';

export default function RichCard({ data }: { data: CardData }) {
  switch (data.type) {
    case 'timetable': return <TimetableCard data={data} />;
    case 'attendance': return <AttendanceCard data={data} />;
    case 'bus': return <BusCard data={data} />;
    case 'faculty': return <FacultyCard data={data} />;
    case 'placement': return <PlacementCard data={data} />;
    case 'event': return <EventCard data={data} />;
    case 'book': return <BookCard data={data} />;
    case 'circular': return <CircularCard data={data} />;
    case 'certificate': return <CertificateCard data={data} />;
    case 'hostel': return <HostelCard data={data} />;
    case 'notification': return <NotificationCard data={data} />;
    default: return null;
  }
}

function CardShell({ children, accent = 'brand' }: { children: React.ReactNode; accent?: string }) {
  return (
    <div className="mt-3 rounded-2xl surface-2 border border-app shadow-app overflow-hidden animate-slide-up">
      <div className="h-1 bg-gradient-to-r from-brand-600 to-brand-400" />
      <div className="p-4">{children}</div>
    </div>
  );
}

function TimetableCard({ data }: { data: CardData }) {
  const slots = (data.slots as any[]) || [];
  const statusMap: Record<string, { label: string; cls: string }> = {
    done: { label: 'Done', cls: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300' },
    live: { label: 'Live now', cls: 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300 animate-pulse' },
    upcoming: { label: 'Upcoming', cls: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300' },
  };
  return (
    <CardShell accent="brand">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <CalendarDays className="w-4 h-4 text-brand-600" />
          <span className="font-semibold text-sm">Timetable — {String(data.day ?? 'Today')}</span>
        </div>
        <span className="text-[11px] text-muted">{slots.length} classes</span>
      </div>
      <div className="space-y-2">
        {slots.map((s, i) => {
          const st = statusMap[s.status] ?? { label: s.status, cls: 'bg-app text-muted' };
          return (
            <div key={i} className="flex items-center gap-3 p-2.5 rounded-xl surface border border-app hover:border-brand-500 transition">
              <div className="text-[11px] font-mono text-muted w-20 flex-shrink-0">{s.time}</div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{s.course}</div>
                <div className="text-[11px] text-muted flex items-center gap-1.5">
                  <MapPin className="w-3 h-3" />{s.room} · {s.faculty}
                </div>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${st.cls}`}>{st.label}</span>
            </div>
          );
        })}
      </div>
    </CardShell>
  );
}

function AttendanceCard({ data }: { data: CardData }) {
  const overall = (data.overall as number) || 0;
  const subjects = (data.subjects as any[]) || [];
  const strokeColor = overall >= 85 ? '#10b981' : overall >= 75 ? '#f59e0b' : '#ef4444';

  return (
    <CardShell accent="emerald">
      <div className="flex items-center gap-4 mb-4">
        <div className="relative w-20 h-20 flex-shrink-0">
          <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="var(--border)" strokeWidth="3.2" />
            <circle cx="18" cy="18" r="15.9" fill="none" stroke={strokeColor} strokeWidth="3.2" strokeDasharray={`${overall}, 100`} strokeLinecap="round" />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-lg font-bold">{overall}%</div>
              <div className="text-[9px] text-muted">Overall</div>
            </div>
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <BookCheck className="w-4 h-4 text-emerald-600" />
            <span className="font-semibold text-sm">Attendance Summary</span>
          </div>
          <p className="text-xs text-muted">{subjects.length} subjects tracked. {overall >= 75 ? 'You meet the mandatory 75% requirement.' : 'Below 75% threshold in some subjects.'}</p>
        </div>
      </div>
      <div className="space-y-2">
        {subjects.map((s, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm truncate font-medium">{s.name}</span>
                <span className={`text-xs font-semibold ${s.percent < 75 ? 'text-rose-500' : 'text-muted'}`}>{s.percent}%</span>
              </div>
              <div className="h-1.5 rounded-full bg-app overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-500 ${s.percent < 75 ? 'bg-rose-500' : s.percent < 85 ? 'bg-amber-500' : 'bg-emerald-500'}`} style={{ width: `${s.percent}%` }} />
              </div>
              <div className="text-[10px] text-muted mt-0.5">{s.attended}/{s.total} classes attended</div>
            </div>
            {s.warning && <span title="Low Attendance Warning"><AlertTriangle className="w-4 h-4 text-rose-500 flex-shrink-0" /></span>}
          </div>
        ))}
      </div>
    </CardShell>
  );
}

function BusCard({ data }: { data: CardData }) {
  const stops = (data.stops as any[]) || [];
  return (
    <CardShell accent="sky">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-sky-100 dark:bg-sky-500/15 flex items-center justify-center">
            <Bus className="w-5 h-5 text-sky-600" />
          </div>
          <div>
            <div className="font-semibold text-sm">{String(data.route)}</div>
            <div className="text-[11px] text-muted">Bus {String(data.busNumber)} · Driver: {String(data.driver)}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            {String(data.status)}
          </div>
          <div className="text-[11px] text-muted mt-1">ETA {String(data.eta)}</div>
        </div>
      </div>
      <div className="relative pl-6">
        <div className="absolute left-2 top-1 bottom-1 w-0.5 bg-app" />
        {stops.map((s, i) => (
          <div key={i} className="relative flex items-center gap-3 py-1.5">
            <div className={`absolute -left-4 w-3 h-3 rounded-full border-2 ${s.current ? 'bg-sky-500 border-sky-500 animate-pulse' : s.passed ? 'bg-emerald-500 border-emerald-500' : 'bg-[var(--surface)] border-app'}`} />
            <div className="flex-1 flex items-center justify-between">
              <span className={`text-sm ${s.current ? 'font-semibold text-sky-600 dark:text-sky-400' : s.passed ? 'text-muted line-through' : ''}`}>{s.name}</span>
              <span className="text-[11px] text-muted font-mono">{s.time}</span>
            </div>
          </div>
        ))}
      </div>
    </CardShell>
  );
}

function FacultyCard({ data }: { data: CardData }) {
  const members = (data.members as any[]) || [];
  return (
    <CardShell accent="cyan">
      <div className="flex items-center gap-2 mb-3">
        <Users className="w-4 h-4 text-cyan-600" />
        <span className="font-semibold text-sm">Faculty Directory — CSE Department</span>
      </div>
      <div className="space-y-2">
        {members.map((m, i) => (
          <div key={i} className="flex items-start gap-3 p-3 rounded-xl surface border border-app hover:border-brand-500 transition">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-brand-600 text-white flex items-center justify-center text-sm font-semibold flex-shrink-0">
              {m.avatar}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium">{m.name}</div>
              <div className="text-[11px] text-muted">{m.designation} · {m.dept}</div>
              <div className="flex flex-wrap gap-1 mt-1.5">
                {m.courses.map((c: string, j: number) => (
                  <span key={j} className="text-[10px] px-1.5 py-0.5 rounded bg-brand-50 dark:bg-brand-700/15 text-brand-700 dark:text-brand-300">{c}</span>
                ))}
              </div>
              <div className="flex items-center gap-3 mt-2 text-[11px] text-muted">
                <a href={`mailto:${m.email}`} className="flex items-center gap-1 hover:text-brand-600"><Mail className="w-3 h-3" />{m.email}</a>
                <span className="flex items-center gap-1"><DoorOpen className="w-3 h-3" />{m.cabin}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </CardShell>
  );
}

function PlacementCard({ data }: { data: CardData }) {
  const [drives, setDrives] = useState<any[]>((data.drives as any[]) || []);

  const handleApply = (idx: number) => {
    setDrives(prev => prev.map((d, i) => i === idx ? { ...d, applied: true } : d));
  };

  return (
    <CardShell accent="teal">
      <div className="flex items-center gap-2 mb-3">
        <Briefcase className="w-4 h-4 text-teal-600" />
        <span className="font-semibold text-sm">Active Placement Drives</span>
      </div>
      <div className="space-y-2">
        {drives.map((d, i) => (
          <div key={i} className={`p-3 rounded-xl border transition ${d.eligible ? 'surface border-app hover:border-brand-500' : 'surface-2 border-app opacity-60'}`}>
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="text-sm font-semibold">{d.company}</div>
                <div className="text-[11px] text-muted">{d.role}</div>
              </div>
              <div className="text-right">
                <div className="text-sm font-bold text-teal-600 flex items-center"><IndianRupee className="w-3.5 h-3.5" />{d.package.split(' ')[0]} LPA</div>
              </div>
            </div>
            <div className="flex items-center justify-between mt-2 text-[11px]">
              <span className="text-muted flex items-center gap-1"><CalendarDays className="w-3 h-3" />{d.date}</span>
              <span className={`px-2 py-0.5 rounded-full font-medium ${d.eligible ? 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300' : 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300'}`}>
                Deadline: {d.deadline}
              </span>
            </div>
            {!d.eligible && <div className="text-[10px] text-rose-500 mt-1">Not eligible — {d.reason}</div>}
            {d.eligible && (
              <div className="flex items-center gap-2 mt-2.5">
                {d.applied ? (
                  <button disabled className="flex-1 text-xs py-1.5 rounded-lg bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300 font-medium flex items-center justify-center gap-1">
                    <Check className="w-3.5 h-3.5" /> Applied
                  </button>
                ) : (
                  <button onClick={() => handleApply(i)} className="flex-1 text-xs py-1.5 rounded-lg bg-brand-700 text-white font-medium hover:bg-brand-800 transition flex items-center justify-center gap-1">
                    Apply Now <ArrowRight className="w-3 h-3" />
                  </button>
                )}
                <div className="flex gap-1">
                  {d.rounds.map((r: string, j: number) => (
                    <span key={j} className="text-[9px] px-1.5 py-1 rounded bg-app text-muted">{r}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </CardShell>
  );
}

function EventCard({ data }: { data: CardData }) {
  const events = (data.events as any[]) || [];
  return (
    <CardShell accent="pink">
      <div className="flex items-center gap-2 mb-3">
        <PartyPopper className="w-4 h-4 text-pink-600" />
        <span className="font-semibold text-sm">Upcoming Campus Events</span>
      </div>
      <div className="space-y-2">
        {events.map((e, i) => (
          <div key={i} className="flex items-start gap-3 p-3 rounded-xl surface border border-app hover:border-brand-500 transition">
            <div className="flex flex-col items-center justify-center w-12 h-12 rounded-xl bg-pink-50 dark:bg-pink-500/15 text-pink-700 dark:text-pink-300 flex-shrink-0">
              <span className="text-[9px] uppercase">{e.date.split(' ')[0]}</span>
              <span className="text-base font-bold leading-none">{e.date.split(' ')[1]}</span>
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium">{e.title}</div>
              <div className="text-[11px] text-muted flex items-center gap-2 mt-0.5">
                <Clock className="w-3 h-3" />{e.time} · <MapPin className="w-3 h-3" />{e.venue}
              </div>
              <span className="inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-pink-100 dark:bg-pink-500/15 text-pink-700 dark:text-pink-300">{e.tag}</span>
            </div>
          </div>
        ))}
      </div>
    </CardShell>
  );
}

function BookCard({ data }: { data: CardData }) {
  const [books, setBooks] = useState<any[]>((data.books as any[]) || []);

  const handleRenew = (idx: number) => {
    setBooks(prev => prev.map((b, i) => i === idx ? { ...b, due: 'Sep 10', overdue: false, renewed: true } : b));
  };

  return (
    <CardShell accent="amber">
      <div className="flex items-center gap-2 mb-3">
        <BookMarked className="w-4 h-4 text-amber-600" />
        <span className="font-semibold text-sm">Issued Books</span>
      </div>
      <div className="space-y-2">
        {books.map((b, i) => (
          <div key={i} className="flex items-start gap-3 p-3 rounded-xl surface border border-app hover:border-brand-500 transition">
            <div className="w-9 h-12 rounded bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center flex-shrink-0">
              <BookOpen className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium leading-snug">{b.title}</div>
              <div className="text-[11px] text-muted">{b.author}</div>
              <div className="text-[10px] text-muted font-mono mt-0.5">{b.id}</div>
              <div className="flex items-center gap-2 mt-1.5">
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${b.overdue ? 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300'}`}>
                  Due {b.due}{b.overdue ? ' · Overdue' : ''}
                </span>
                {b.renewed ? (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300 font-medium flex items-center gap-1">
                    <Check className="w-2.5 h-2.5" /> Renewed
                  </span>
                ) : b.renew && (
                  <button onClick={() => handleRenew(i)} className="text-[10px] px-2 py-0.5 rounded bg-brand-100 text-brand-700 dark:bg-brand-700/15 dark:text-brand-300 hover:bg-brand-200 transition flex items-center gap-1">
                    <RefreshCw className="w-2.5 h-2.5" /> Renew
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </CardShell>
  );
}

function CircularCard({ data }: { data: CardData }) {
  const circulars = (data.circulars as any[]) || [];
  const handleDownload = (title: string, body: string) => {
    const text = `OFFICIAL CIRCULAR\nTitle: ${title}\n\n${body}`;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/\s+/g, '_')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <CardShell accent="rose">
      <div className="flex items-center gap-2 mb-3">
        <ScrollText className="w-4 h-4 text-rose-600" />
        <span className="font-semibold text-sm">Latest Circulars</span>
      </div>
      <div className="space-y-2">
        {circulars.map((c, i) => (
          <div key={i} className="p-3 rounded-xl surface border border-app hover:border-brand-500 transition">
            <div className="flex items-start justify-between gap-2">
              <div className="text-sm font-medium leading-snug">{c.title}</div>
              <button onClick={() => handleDownload(c.title, c.body)} title="Download Circular">
                <Download className="w-4 h-4 text-muted hover:text-brand-600 cursor-pointer flex-shrink-0" />
              </button>
            </div>
            <p className="text-[11px] text-muted mt-1">{c.body}</p>
            <div className="text-[10px] text-muted font-mono mt-1.5">{c.ref} · {c.date}</div>
          </div>
        ))}
      </div>
    </CardShell>
  );
}

function CertificateCard({ data }: { data: CardData }) {
  const types = (data.types as string[]) || [];
  const [selectedType, setSelectedType] = useState(types[0] || 'Bonafide Certificate');
  const [purpose, setPurpose] = useState(String(data.purpose || 'Bank Loan'));
  const [history, setHistory] = useState<any[]>((data.history as any[]) || []);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    const newReq = {
      ref: `BNF-2025-0${Math.floor(1000 + Math.random() * 9000)}`,
      type: selectedType.replace(' Certificate', ''),
      date: 'Today',
      status: 'Pending Approval',
    };
    setHistory(prev => [newReq, ...prev]);
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 2000);
  };

  return (
    <CardShell accent="orange">
      <div className="flex items-center gap-2 mb-3">
        <FileText className="w-4 h-4 text-orange-600" />
        <span className="font-semibold text-sm">Request a Certificate</span>
      </div>
      <div className="space-y-3">
        <div>
          <div className="text-[11px] text-muted mb-1.5">Certificate Type</div>
          <div className="grid grid-cols-2 gap-1.5">
            {types.map((t, i) => (
              <button key={i} onClick={() => setSelectedType(t)} className={`text-xs py-2 px-2 rounded-lg border transition text-left ${selectedType === t ? 'bg-orange-100 text-orange-700 border-orange-300 dark:bg-orange-500/15 dark:text-orange-300 dark:border-orange-500/30 font-medium' : 'surface-2 border-app hover:border-orange-400'}`}>{t}</button>
            ))}
          </div>
        </div>
        <div>
          <div className="text-[11px] text-muted mb-1.5">Purpose</div>
          <input value={purpose} onChange={e => setPurpose(e.target.value)} className="w-full px-3 py-2 rounded-lg surface border border-app text-sm outline-none focus:border-orange-400" />
        </div>
        <button onClick={handleSubmit} className="w-full py-2.5 rounded-lg bg-orange-600 hover:bg-orange-700 text-white text-sm font-medium transition flex items-center justify-center gap-2">
          {submitted ? <><Check className="w-4 h-4" /> Request Submitted!</> : <>Submit Request <ArrowRight className="w-3.5 h-3.5" /></>}
        </button>
        {history.length > 0 && (
          <div>
            <div className="text-[11px] text-muted mb-1.5">Request History</div>
            {history.map((h, i) => (
              <div key={i} className="flex items-center justify-between p-2 mb-1.5 rounded-lg surface-2 border border-app text-xs">
                <div>
                  <div className="font-medium">{h.type}</div>
                  <div className="text-[10px] text-muted font-mono">{h.ref} · {h.date}</div>
                </div>
                <span className={`flex items-center gap-1 font-medium ${h.status === 'Approved' ? 'text-emerald-600' : 'text-amber-600'}`}>
                  <CheckCircle2 className="w-3.5 h-3.5" />{h.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </CardShell>
  );
}

function HostelCard({ data }: { data: CardData }) {
  const menu = data.messMenu as any[];
  return (
    <CardShell accent="indigo">
      <div className="flex items-center gap-2 mb-3">
        <Building2 className="w-4 h-4 text-indigo-600" />
        <span className="font-semibold text-sm">Hostel Details</span>
      </div>
      <div className="grid grid-cols-2 gap-2 mb-3">
        <Info label="Room" value={String(data.block)} />
        <Info label="Warden" value={String(data.warden)} />
        <Info label="Mess" value={String(data.mess)} />
      </div>
      <div className="text-[11px] text-muted mb-1.5">Mess Menu (This Week)</div>
      <div className="overflow-hidden rounded-xl border border-app">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-app">
              <th className="text-left p-2 font-medium">Day</th>
              <th className="text-left p-2 font-medium">Breakfast</th>
              <th className="text-left p-2 font-medium">Lunch</th>
              <th className="text-left p-2 font-medium">Dinner</th>
            </tr>
          </thead>
          <tbody>
            {menu.map((m, i) => (
              <tr key={i} className="border-t border-app">
                <td className="p-2 font-medium">{m.day}</td>
                <td className="p-2 text-muted">{m.breakfast}</td>
                <td className="p-2 text-muted">{m.lunch}</td>
                <td className="p-2 text-muted">{m.dinner}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </CardShell>
  );
}

function NotificationCard({ data }: { data: CardData }) {
  const items = data.items as any[];
  const iconMap: Record<string, any> = { exam: GraduationCap, placement: Briefcase, attendance: BookCheck };
  return (
    <CardShell accent="amber">
      <div className="flex items-center gap-2 mb-3">
        <Bell className="w-4 h-4 text-amber-600" />
        <span className="font-semibold text-sm">Recent Notifications</span>
      </div>
      <div className="space-y-2">
        {items.map((n, i) => {
          const Icon = iconMap[n.type] ?? Bell;
          return (
            <div key={i} className="flex items-start gap-3 p-2.5 rounded-xl surface border border-app hover:border-brand-500 transition">
              <div className="w-8 h-8 rounded-lg bg-amber-50 dark:bg-amber-500/15 flex items-center justify-center flex-shrink-0">
                <Icon className="w-4 h-4 text-amber-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium leading-snug">{n.title}</div>
                <div className="text-[10px] text-muted">{n.time}</div>
              </div>
            </div>
          );
        })}
      </div>
    </CardShell>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-2.5 rounded-lg surface border border-app">
      <div className="text-[10px] text-muted">{label}</div>
      <div className="text-sm font-medium truncate">{value}</div>
    </div>
  );
}
