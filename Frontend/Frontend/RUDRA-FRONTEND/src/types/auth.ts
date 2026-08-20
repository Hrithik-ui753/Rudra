import type { Role } from '../types';

export interface AuthUser {
  uid: string;
  displayName: string | null;
  email: string | null;
  photoURL: string | null;
  provider: string;
  role: Role;
  rollNo?: string;
  teacherId?: string;
  teacherMail?: string;
  branch?: string;
  year?: string;
  semester?: string;
  section?: string;
  department?: string;
  designation?: string;
  busRoute?: string;
  careerInterest?: string;
  language?: string;
}

export interface AuthContextType {
  currentUser: AuthUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  loginGoogle: () => Promise<AuthUser | null>;
  loginMicrosoft: () => Promise<AuthUser | null>;
  logout: () => Promise<void>;
  clearError: () => void;
}
