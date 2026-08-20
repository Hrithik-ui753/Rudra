import { useState, type FormEvent } from 'react';
import {
  GraduationCap, Mail, Lock, Eye, EyeOff, ArrowRight, Building2, Sparkles,
  ShieldCheck, Bot, MessageSquare, User as UserIcon, Hash, BookOpen, CalendarDays, Briefcase,
  Loader2, AlertCircle
} from 'lucide-react';
import { useApp, API_BASE_URL } from '@/context/AppContext';
import useAuth from '@/hooks/useAuth';
import { branches, departments, designations, years, semesters, sections } from '@/data/mock';
import type { Role, User } from '@/types';

type AuthTab = 'login' | 'signup';
type AuthMode = 'form' | 'complete';

export default function AuthPage() {
  const { login } = useApp();
  const { loginGoogle, loginMicrosoft, error: authContextError, clearError } = useAuth();
  const [tab, setTab] = useState<AuthTab>('login');
  const [mode, setMode] = useState<AuthMode>('form');
  const [role, setRole] = useState<Role>('student');
  const [pendingUser, setPendingUser] = useState<User | null>(null);
  const [showPw, setShowPw] = useState(false);
  const [loadingProvider, setLoadingProvider] = useState<'google' | 'microsoft' | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  // Form states for login/signup
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [teacherMail, setTeacherMail] = useState('');
  const [password, setPassword] = useState('');

  const activeError = localError || authContextError;

  const doLogin = async (userObj: User) => {
    let finalUser = { ...userObj };
    try {
      const endpoint = tab === 'signup' ? '/api/auth/register' : '/api/auth/login';
      const authRes = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: finalUser.email,
          role: finalUser.role,
          name: finalUser.name,
          branch: finalUser.branch || finalUser.department,
          department: finalUser.department || finalUser.branch,
          roll_no: finalUser.rollNo,
          year: finalUser.year,
          section: finalUser.section
        }),
      });
      if (authRes.ok) {
        const authData = await authRes.json();
        if (authData?.user) {
          finalUser = {
            ...finalUser,
            name: authData.user.name || finalUser.name,
            role: (authData.user.role as Role) || finalUser.role,
            department: authData.user.department || finalUser.department,
            branch: authData.user.branch || finalUser.branch,
            rollNo: authData.user.roll_no || finalUser.rollNo,
            year: authData.user.year || finalUser.year,
            section: authData.user.section || finalUser.section,
          };
        }
      }
    } catch (e) {
      console.warn('Backend auth call fallback:', e);
    }

    if (finalUser.role === 'guest') {
      await login(finalUser);
    } else if (finalUser.role === 'student' && (!finalUser.branch || !finalUser.rollNo || !finalUser.year || !finalUser.section)) {
      setPendingUser(finalUser);
      setMode('complete');
    } else if (finalUser.role === 'faculty' && (!finalUser.department || !finalUser.teacherId || !finalUser.teacherMail)) {
      setPendingUser(finalUser);
      setMode('complete');
    } else {
      await login(finalUser);
    }
  };

  const handleFormSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    clearError();
    const userMail = role === 'student' ? (email || 'student@campus.edu') : (teacherMail || 'faculty@campus.edu');
    await doLogin({
      id: `u-${Date.now()}`,
      name: name || (role === 'student' ? 'Student User' : 'Dr. Faculty Member'),
      email: userMail,
      role: role,
      language: 'English',
    });
  };

  const handleGoogle = async () => {
    setLocalError(null);
    clearError();
    setLoadingProvider('google');
    try {
      const authUser = await loginGoogle();
      if (authUser) {
        doLogin({
          id: authUser.uid,
          name: authUser.displayName || 'Google User',
          email: authUser.email || 'google.user@campus.edu',
          avatar: authUser.photoURL || undefined,
          role: role === 'faculty' ? 'faculty' : 'student',
          language: authUser.language,
        });
      }
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Google sign-in failed. Please try again.');
    } finally {
      setLoadingProvider(null);
    }
  };

  const handleMicrosoft = async () => {
    setLocalError(null);
    clearError();
    setLoadingProvider('microsoft');
    try {
      const authUser = await loginMicrosoft();
      if (authUser) {
        doLogin({
          id: authUser.uid,
          name: authUser.displayName || 'Microsoft User',
          email: authUser.email || 'ms.user@campus.edu',
          avatar: authUser.photoURL || undefined,
          role: role === 'faculty' ? 'faculty' : 'student',
          language: authUser.language,
        });
      }
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Microsoft sign-in failed. Please try again.');
    } finally {
      setLoadingProvider(null);
    }
  };

  const handleGuest = async () => {
    await doLogin({ id: 'u-guest', name: 'Guest User', email: '', role: 'guest' });
  };

  const completeProfile = async (patch: Partial<User>) => {
    if (pendingUser) await login({ ...pendingUser, ...patch });
  };

  if (mode === 'complete' && pendingUser) {
    return <ProfileCompletion user={pendingUser} onComplete={completeProfile} />;
  }

  return (
    <div className="min-h-screen flex">
      {/* Left brand panel - About App */}
      <div className="hidden lg:flex w-[45%] relative overflow-hidden bg-gradient-to-br from-brand-800 via-brand-700 to-brand-950">
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(circle at 20% 30%, white 1px, transparent 1px)', backgroundSize: '32px 32px' }} />
        <div className="absolute -top-20 -right-20 w-96 h-96 rounded-full bg-brand-400/20 blur-3xl animate-float" />
        <div className="absolute bottom-0 -left-10 w-80 h-80 rounded-full bg-accent-400/10 blur-3xl" />
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-white/15 backdrop-blur flex items-center justify-center">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="font-bold text-lg leading-tight">Rudra-AI</div>
              <div className="text-xs text-brand-100">Vasavi College of Engineering</div>
            </div>
          </div>

          <div className="space-y-6">
            <h1 className="text-4xl font-bold leading-tight">
              The end of<br />browsing portals.
            </h1>
            <p className="text-brand-100 text-lg max-w-md">
              Attendance, timetable, bus, library, placements, certificates — all answered in one conversation.
            </p>
            <div className="space-y-3 pt-2">
              {[
                { icon: MessageSquare, text: 'Ask anything, get instant answers' },
                { icon: Bot, text: 'One intelligent assistant, not many apps' },
                { icon: ShieldCheck, text: 'Secure, personalized, role-aware' },
              ].map((f, i) => (
                <div key={i} className="flex items-center gap-3 text-sm text-brand-50">
                  <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
                    <f.icon className="w-4 h-4" />
                  </div>
                  {f.text}
                </div>
              ))}
            </div>
          </div>

          <div className="text-xs text-brand-200 font-medium">
            Built for Vasavi College of Engineering
          </div>
        </div>
      </div>

      {/* Right auth panel */}
      <div className="flex-1 flex items-center justify-center p-6 surface overflow-y-auto max-h-screen">
        <div className="w-full max-w-md animate-slide-up py-4">
          <div className="lg:hidden flex items-center gap-3 mb-6">
            <div className="w-11 h-11 rounded-2xl bg-brand-700 flex items-center justify-center text-white">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div className="font-bold text-lg">Rudra-AI</div>
          </div>

          {/* Sign In / Sign Up Tabs */}
          <div className="flex rounded-xl surface-2 p-1 border border-app mb-6">
            <button
              onClick={() => setTab('login')}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition ${tab === 'login' ? 'bg-brand-700 text-white shadow' : 'text-muted hover:text-brand-600'}`}
            >
              Sign In
            </button>
            <button
              onClick={() => setTab('signup')}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition ${tab === 'signup' ? 'bg-brand-700 text-white shadow' : 'text-muted hover:text-brand-600'}`}
            >
              Sign Up
            </button>
          </div>

          <h2 className="text-2xl font-bold">
            {tab === 'login' ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p className="text-muted text-sm mt-1">
            {tab === 'login'
              ? 'Sign in to access your campus AI assistant'
              : 'Create an account to get started'}
          </p>

          {activeError && (
            <div className="mt-3 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 text-xs flex items-start gap-2 animate-fade-in">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="font-medium">{activeError}</p>
              </div>
              <button
                type="button"
                onClick={() => { setLocalError(null); clearError(); }}
                className="text-muted hover:text-foreground text-xs font-bold"
              >
                ✕
              </button>
            </div>
          )}

          {/* Role selector */}
          <div className="flex items-center gap-2 mt-4 mb-5">
            <button
              type="button"
              onClick={() => setRole('student')}
              className={`flex-1 py-2.5 px-3 rounded-xl border text-xs font-medium flex items-center justify-center gap-2 transition ${role === 'student' ? 'border-brand-600 bg-brand-50/50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 font-semibold' : 'border-app surface-2 text-muted'}`}
            >
              <GraduationCap className="w-4 h-4" />
              Student
            </button>
            <button
              type="button"
              onClick={() => setRole('faculty')}
              className={`flex-1 py-2.5 px-3 rounded-xl border text-xs font-medium flex items-center justify-center gap-2 transition ${role === 'faculty' ? 'border-brand-600 bg-brand-50/50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 font-semibold' : 'border-app surface-2 text-muted'}`}
            >
              <Building2 className="w-4 h-4" />
              Teacher / Faculty
            </button>
          </div>

          <form onSubmit={handleFormSubmit} className="space-y-4">
            {tab === 'signup' && (
              <div>
                <label className="text-xs font-medium text-muted">Full Name</label>
                <div className="relative mt-1">
                  <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                  <input
                    type="text" required value={name} onChange={e => setName(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl surface-2 border border-app focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none text-sm transition"
                    placeholder={role === 'student' ? 'Aarav Mehta' : 'Dr. Vikram Singh'}
                  />
                </div>
              </div>
            )}

            <div>
              <label className="text-xs font-medium text-muted">
                {role === 'student' ? 'Email Address' : 'Teacher Mail'}
              </label>
              <div className="relative mt-1">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                <input
                  type="email" required
                  value={role === 'student' ? email : teacherMail}
                  onChange={e => role === 'student' ? setEmail(e.target.value) : setTeacherMail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl surface-2 border border-app focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none text-sm transition"
                  placeholder={role === 'student' ? 'aarav.mehta@campus.edu' : 'vikram.singh@campus.edu'}
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-muted">Password</label>
              <div className="relative mt-1">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                <input
                  type={showPw ? 'text' : 'password'} required value={password} onChange={e => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl surface-2 border border-app focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none text-sm transition"
                  placeholder="••••••••"
                />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-brand-600">
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button type="submit" className="w-full py-3 rounded-xl bg-brand-700 hover:bg-brand-800 text-white font-semibold text-sm transition flex items-center justify-center gap-2 group mt-2 shadow-md">
              {tab === 'login' ? 'Sign In' : 'Continue to Setup Questions'}
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition" />
            </button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <div className="h-px flex-1 bg-app border-app" />
            <span className="text-xs text-muted">or continue with</span>
            <div className="h-px flex-1 bg-app border-app" />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <button
              onClick={handleMicrosoft}
              disabled={loadingProvider !== null}
              className="flex flex-col items-center gap-1 py-2.5 rounded-xl surface-2 border border-app hover:border-brand-500 hover:shadow-app transition group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loadingProvider === 'microsoft' ? (
                <Loader2 className="w-5 h-5 text-brand-700 animate-spin" />
              ) : (
                <Building2 className="w-5 h-5 text-brand-700 group-hover:scale-110 transition" />
              )}
              <span className="text-[11px] font-medium">Microsoft</span>
            </button>
            <button
              onClick={handleGoogle}
              disabled={loadingProvider !== null}
              className="flex flex-col items-center gap-1 py-2.5 rounded-xl surface-2 border border-app hover:border-brand-500 hover:shadow-app transition group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loadingProvider === 'google' ? (
                <Loader2 className="w-5 h-5 text-brand-700 animate-spin" />
              ) : (
                <GoogleIcon />
              )}
              <span className="text-[11px] font-medium">Google</span>
            </button>
            <button
              onClick={handleGuest}
              disabled={loadingProvider !== null}
              className="flex flex-col items-center gap-1 py-2.5 rounded-xl surface-2 border border-app hover:border-brand-500 hover:shadow-app transition group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles className="w-5 h-5 text-accent-500 group-hover:scale-110 transition" />
              <span className="text-[11px] font-medium">Guest</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="w-5 h-5">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  );
}

function ProfileCompletion({ user, onComplete }: { user: User; onComplete: (patch: Partial<User>) => void }) {
  const isFaculty = user.role === 'faculty';
  const [rollNoVal, setRollNoVal] = useState(user.rollNo ?? '');
  const [teacherIdVal, setTeacherIdVal] = useState(user.teacherId ?? '');
  const [teacherMailVal, setTeacherMailVal] = useState(user.teacherMail ?? user.email ?? '');
  const [form, setForm] = useState<Record<string, string>>({
    branch: user.branch ?? branches[0],
    year: user.year ?? years[0],
    section: user.section ?? sections[0],
    department: user.department ?? departments[0],
    designation: user.designation ?? designations[0],
  });

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (isFaculty) {
      onComplete({
        ...form,
        teacherMail: teacherMailVal || user.email,
        teacherId: teacherIdVal || 'TCH-1001',
      });
    } else {
      onComplete({
        ...form,
        rollNo: rollNoVal || '1602-22-733-001',
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 surface">
      <div className="w-full max-w-lg animate-slide-up">
        <div className="text-center mb-6">
          <div className="w-16 h-16 rounded-2xl bg-brand-700 mx-auto flex items-center justify-center text-white mb-4 shadow-lg">
            <GraduationCap className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold">Complete Your Setup Questions</h2>
          <p className="text-muted text-sm mt-1">Please answer these mandatory campus profile questions to enter.</p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          {!isFaculty ? (
            <>
              <div>
                <label className="text-xs font-medium text-muted">Roll Number</label>
                <div className="relative mt-1">
                  <Hash className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                  <input
                    type="text" required value={rollNoVal} onChange={e => setRollNoVal(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl surface-2 border border-app outline-none text-sm"
                    placeholder="e.g. 1602-22-733-042"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-muted">Branch</label>
                <div className="relative mt-1">
                  <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                  <select
                    value={form.branch} onChange={e => setForm(s => ({ ...s, branch: e.target.value }))}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl surface-2 border border-app text-sm appearance-none"
                  >
                    {branches.map(b => <option key={b} value={b}>{b}</option>)}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-muted">Year</label>
                  <div className="relative mt-1">
                    <CalendarDays className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                    <select
                      value={form.year} onChange={e => setForm(s => ({ ...s, year: e.target.value }))}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl surface-2 border border-app text-sm appearance-none"
                    >
                      {years.map(y => <option key={y} value={y}>{y}</option>)}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-muted">Section</label>
                  <div className="relative mt-1">
                    <Hash className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                    <select
                      value={form.section} onChange={e => setForm(s => ({ ...s, section: e.target.value }))}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl surface-2 border border-app text-sm appearance-none"
                    >
                      {sections.map(sec => <option key={sec} value={sec}>Section {sec}</option>)}
                    </select>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <>
              <div>
                <label className="text-xs font-medium text-muted">Teacher Mail</label>
                <div className="relative mt-1">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                  <input
                    type="email" required value={teacherMailVal} onChange={e => setTeacherMailVal(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl surface-2 border border-app text-sm"
                    placeholder="teacher@campus.edu"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-muted">Teacher ID</label>
                <div className="relative mt-1">
                  <Hash className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                  <input
                    type="text" required value={teacherIdVal} onChange={e => setTeacherIdVal(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl surface-2 border border-app text-sm"
                    placeholder="e.g. TCH-1004"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-muted">Department Name</label>
                <div className="relative mt-1">
                  <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                  <select
                    value={form.department} onChange={e => setForm(s => ({ ...s, department: e.target.value }))}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl surface-2 border border-app text-sm appearance-none"
                  >
                    {departments.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
              </div>
            </>
          )}

          <button type="submit" className="w-full py-3 rounded-xl bg-brand-700 hover:bg-brand-800 text-white font-semibold text-sm transition flex items-center justify-center gap-2 group mt-2 shadow">
            Submit Setup Answers & Enter Chat
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition" />
          </button>
        </form>
      </div>
    </div>
  );
}
