import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { onAuthStateChanged, type User as FirebaseUser } from 'firebase/auth';
import { auth } from '../lib/firebase';
import { loginWithGoogle, loginWithMicrosoft, logout as firebaseSignOut } from '../lib/firebase-auth';
import type { AuthContextType, AuthUser } from '../types/auth';

const AuthContext = createContext<AuthContextType | null>(null);

export function mapFirebaseUserToAuthUser(fbUser: FirebaseUser): AuthUser {
  const providerData = fbUser.providerData[0];
  const providerId = providerData?.providerId || 'firebase';

  return {
    uid: fbUser.uid,
    displayName: fbUser.displayName || providerData?.displayName || 'Campus User',
    email: fbUser.email || providerData?.email || '',
    photoURL: fbUser.photoURL || providerData?.photoURL || null,
    provider: providerId,
    role: 'student',
    rollNo: '1602-22-733-042',
    branch: 'Computer Science & Engineering',
    year: '3rd Year',
    semester: 'Semester 5',
    section: 'A',
    language: 'English',
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let unsubscribe = () => {};
    // Timeout safeguard so app never stays stuck on loading spinner
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2000);

    try {
      unsubscribe = onAuthStateChanged(
        auth,
        (user) => {
          clearTimeout(timer);
          if (user) {
            const authUser = mapFirebaseUserToAuthUser(user);
            setCurrentUser(authUser);
          } else {
            setCurrentUser(null);
          }
          setLoading(false);
        },
        (err) => {
          clearTimeout(timer);
          console.warn('Firebase Auth State Change Error:', err);
          setError(err.message);
          setLoading(false);
        }
      );
    } catch (err: unknown) {
      clearTimeout(timer);
      console.warn('Firebase Auth Subscription Catch:', err);
      setLoading(false);
    }

    return () => {
      clearTimeout(timer);
      unsubscribe();
    };
  }, []);

  const loginGoogle = async (): Promise<AuthUser | null> => {
    setLoading(true);
    setError(null);
    try {
      const fbUser = await loginWithGoogle();
      const authUser = mapFirebaseUserToAuthUser(fbUser);
      setCurrentUser(authUser);
      return authUser;
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : 'Google login failed';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loginMicrosoft = async (): Promise<AuthUser | null> => {
    setLoading(true);
    setError(null);
    try {
      const fbUser = await loginWithMicrosoft();
      const authUser = mapFirebaseUserToAuthUser(fbUser);
      setCurrentUser(authUser);
      return authUser;
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : 'Microsoft login failed';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await firebaseSignOut();
      setCurrentUser(null);
      // Clear any stored auth state to ensure fresh login next time
      // This helps show account selection screen on next login
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : 'Logout failed';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => setError(null);

  const value: AuthContextType = {
    currentUser,
    loading,
    isAuthenticated: !!currentUser,
    error,
    loginGoogle,
    loginMicrosoft,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
