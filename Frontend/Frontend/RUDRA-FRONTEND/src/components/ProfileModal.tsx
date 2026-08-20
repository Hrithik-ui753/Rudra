import { useState } from 'react';
import { X, Camera, Save, GraduationCap, Mail, Building2, CalendarDays, BookOpen, Bus, Briefcase, Globe, Hash, IdCard } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { branches, years, semesters, sections, careerInterests, languages, departments, designations } from '@/data/mock';

export default function ProfileModal({ onClose }: { onClose: () => void }) {
  const { user, updateUser } = useApp();
  const [form, setForm] = useState({
    name: user?.name ?? '',
    email: user?.email ?? '',
    rollNo: user?.rollNo ?? '',
    teacherMail: user?.teacherMail ?? user?.email ?? '',
    teacherId: user?.teacherId ?? '',
    branch: user?.branch ?? '',
    year: user?.year ?? '',
    semester: user?.semester ?? '',
    section: user?.section ?? '',
    department: user?.department ?? '',
    designation: user?.designation ?? '',
    busRoute: user?.busRoute ?? '',
    careerInterest: user?.careerInterest ?? '',
    language: user?.language ?? '',
  });
  const [saved, setSaved] = useState(false);

  const isFaculty = user?.role === 'faculty';
  const isGuest = user?.role === 'guest';

  const save = () => {
    updateUser(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in-fast" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div className="relative w-full max-w-lg surface rounded-2xl border border-app shadow-app-lg overflow-hidden animate-scale-in max-h-[88vh] flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-app">
          <span className="font-semibold text-sm">Profile Details</span>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-app text-muted"><X className="w-4 h-4" /></button>
        </div>

        <div className="flex-1 overflow-y-auto p-5">
          {/* Avatar Header */}
          <div className="flex items-center gap-4 mb-6">
            <div className="relative">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-500 to-brand-800 text-white flex items-center justify-center text-2xl font-bold shadow">
                {form.name?.[0] ?? 'U'}
              </div>
              <button className="absolute -bottom-1 -right-1 w-7 h-7 rounded-full surface border border-app flex items-center justify-center hover:bg-app transition">
                <Camera className="w-3.5 h-3.5 text-muted" />
              </button>
            </div>
            <div>
              <div className="text-lg font-bold">{form.name || 'User'}</div>
              <div className="text-xs text-brand-600 dark:text-brand-400 font-semibold uppercase tracking-wider">
                {user?.role === 'faculty' ? 'Teacher / Faculty' : user?.role === 'student' ? 'Student' : 'Guest'}
              </div>
              {form.rollNo && <div className="text-xs text-muted mt-0.5">Roll No: {form.rollNo}</div>}
              {form.teacherId && <div className="text-xs text-muted mt-0.5">ID: {form.teacherId}</div>}
            </div>
          </div>

          <div className="space-y-4">
            <Field icon={GraduationCap} label="Full Name">
              <input value={form.name} onChange={e => setForm(s => ({ ...s, name: e.target.value }))} className="input" />
            </Field>

            {!isGuest && (
              isFaculty ? (
                <>
                  <Field icon={Mail} label="Teacher Mail">
                    <input value={form.teacherMail} onChange={e => setForm(s => ({ ...s, teacherMail: e.target.value, email: e.target.value }))} className="input" placeholder="teacher@campus.edu" />
                  </Field>
                  <Field icon={IdCard} label="Teacher ID">
                    <input value={form.teacherId} onChange={e => setForm(s => ({ ...s, teacherId: e.target.value }))} className="input" placeholder="e.g. TCH-1004" />
                  </Field>
                  <Field icon={Building2} label="Department Name">
                    <Select value={form.department} onChange={v => setForm(s => ({ ...s, department: v }))} options={departments} />
                  </Field>
                  <Field icon={Briefcase} label="Designation">
                    <Select value={form.designation} onChange={v => setForm(s => ({ ...s, designation: v }))} options={designations} />
                  </Field>
                </>
              ) : (
                <>
                  <Field icon={Mail} label="Student Email">
                    <input value={form.email} onChange={e => setForm(s => ({ ...s, email: e.target.value }))} className="input" />
                  </Field>
                  <Field icon={IdCard} label="Roll Number">
                    <input value={form.rollNo} onChange={e => setForm(s => ({ ...s, rollNo: e.target.value }))} className="input" placeholder="e.g. 1602-22-733-042" />
                  </Field>
                  <Field icon={BookOpen} label="Branch">
                    <Select value={form.branch} onChange={v => setForm(s => ({ ...s, branch: v }))} options={branches} />
                  </Field>
                  <div className="grid grid-cols-2 gap-3">
                    <Field icon={CalendarDays} label="Year">
                      <Select value={form.year} onChange={v => setForm(s => ({ ...s, year: v }))} options={years} />
                    </Field>
                    <Field icon={Hash} label="Semester">
                      <Select value={form.semester} onChange={v => setForm(s => ({ ...s, semester: v }))} options={semesters} />
                    </Field>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Field icon={Hash} label="Section">
                      <Select value={form.section} onChange={v => setForm(s => ({ ...s, section: v }))} options={sections} />
                    </Field>
                    <Field icon={Bus} label="Bus Route">
                      <input value={form.busRoute} onChange={e => setForm(s => ({ ...s, busRoute: e.target.value }))} className="input" placeholder="e.g. Route 7" />
                    </Field>
                  </div>
                  <Field icon={Briefcase} label="Career Interest">
                    <Select value={form.careerInterest} onChange={v => setForm(s => ({ ...s, careerInterest: v }))} options={careerInterests} />
                  </Field>
                </>
              )
            )}
            <Field icon={Globe} label="Preferred Language">
              <Select value={form.language} onChange={v => setForm(s => ({ ...s, language: v }))} options={languages} />
            </Field>
          </div>
        </div>

        <div className="p-4 border-t border-app flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 rounded-xl surface-2 border border-app text-sm hover:bg-app transition">Cancel</button>
          <button onClick={save} className="px-4 py-2 rounded-xl bg-brand-700 text-white text-sm font-medium hover:bg-brand-800 transition flex items-center gap-2">
            <Save className="w-4 h-4" /> {saved ? 'Saved!' : 'Save Changes'}
          </button>
        </div>
      </div>

      <style>{`.input{width:100%;padding:0.5rem 0.75rem;border-radius:0.625rem;background:var(--surface-2);border:1px solid var(--border);outline:none;font-size:0.875rem;}.input:focus{border-color:var(--color-brand-500);}`}</style>
    </div>
  );
}

function Field({ icon: Icon, label, children }: { icon: any; label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="text-xs font-medium text-muted flex items-center gap-1.5 mb-1.5">
        <Icon className="w-3.5 h-3.5" /> {label}
      </label>
      {children}
    </div>
  );
}

function Select({ value, onChange, options }: { value: string; onChange: (v: string) => void; options: string[] }) {
  return (
    <select value={value} onChange={e => onChange(e.target.value)} className="input" style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.625rem', background: 'var(--surface-2)', border: '1px solid var(--border)', outline: 'none', fontSize: '0.875rem' }}>
      <option value="">Select...</option>
      {options.map(o => <option key={o} value={o}>{o}</option>)}
    </select>
  );
}
