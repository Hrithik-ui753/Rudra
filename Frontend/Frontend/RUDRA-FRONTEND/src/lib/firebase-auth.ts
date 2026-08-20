import {
  FirebaseError,
} from 'firebase/app';
import {
  GoogleAuthProvider,
  OAuthProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
  type User as FirebaseUser,
} from 'firebase/auth';
import { auth } from './firebase';

export const googleProvider = new GoogleAuthProvider();
googleProvider.addScope('email');
googleProvider.addScope('profile');
// Important: Set custom parameters to force account selection and consent
googleProvider.setCustomParameters({
  prompt: 'select_account consent',  // This forces account selection AND consent screen
});

export const microsoftProvider = new OAuthProvider('microsoft.com');
microsoftProvider.addScope('user.read');
microsoftProvider.setCustomParameters({
  prompt: 'select_account consent',  // Forces account selection AND consent screen
  tenant: 'common',
});

export const loginWithGoogle = async (): Promise<FirebaseUser> => {
  try {
    // Ensure provider is configured to always show account selection
    googleProvider.setCustomParameters({
      prompt: 'select_account consent',  // Forces both account selection AND consent screen
    });
    const result = await signInWithPopup(auth, googleProvider);
    return result.user;
  } catch (error: unknown) {
    throw new Error(formatAuthError(error));
  }
};

export const loginWithMicrosoft = async (): Promise<FirebaseUser> => {
  try {
    const result = await signInWithPopup(auth, microsoftProvider);
    return result.user;
  } catch (error: unknown) {
    throw new Error(formatAuthError(error));
  }
};

export const logout = async (): Promise<void> => {
  try {
    await firebaseSignOut(auth);
    // Clear any persisted Firebase auth state in this browser tab
    sessionStorage.clear();
  } catch (error: unknown) {
    throw new Error(formatAuthError(error));
  }
};

export const getCurrentUser = (): FirebaseUser | null => {
  return auth.currentUser;
};

export const getIdToken = async (forceRefresh: boolean = false): Promise<string | null> => {
  const user = auth.currentUser;
  if (!user) return null;
  return await user.getIdToken(forceRefresh);
};

/**
 * Build the Authorization header for backend API calls.
 *
 * When a Firebase user is signed in, the real Firebase ID token (JWT) is sent
 * so the backend can verify it (AUTH_DEV_MODE=false). When no Firebase session
 * exists (guest/demo login), falls back to the legacy `Bearer user_<id>` token
 * accepted by the backend in dev mode (AUTH_DEV_MODE=true).
 */
export const buildAuthHeader = async (fallback?: string): Promise<string> => {
  const token = await getIdToken();
  if (token) return `Bearer ${token}`;
  return fallback || 'Bearer user_guest';
};

export function formatAuthError(error: unknown): string {
  const str = String(error instanceof Error ? error.message : JSON.stringify(error));
  if (str.includes('unauthorized_client') || str.includes('client does not exist')) {
    return 'Microsoft OAuth Config Error: The Microsoft App ID / Secret is not configured or enabled in your Azure Portal & Firebase Console for consumer accounts.';
  }

  if (error instanceof FirebaseError) {
    switch (error.code) {
      case 'auth/popup-closed-by-user':
        return 'Sign-in popup was closed before completing authentication.';
      case 'auth/popup-blocked':
        return 'Sign-in popup was blocked by your browser. Please allow popups for this site.';
      case 'auth/network-request-failed':
        return 'Network error. Please check your internet connection.';
      case 'auth/invalid-credential':
      case 'auth/invalid-user-token':
      case 'auth/user-not-found':
        return 'Invalid credentials or expired session.';
      case 'auth/user-disabled':
        return 'This account has been disabled.';
      case 'auth/account-exists-with-different-credential':
        return 'An account already exists with this email using a different sign-in method.';
      case 'auth/operation-not-allowed':
        return 'Microsoft/Google provider is not enabled in Firebase Console (Authentication > Sign-in method).';
      case 'auth/unauthorized-domain':
        return 'This domain is not authorized in Firebase Console settings.';
      default:
        return error.message || 'An error occurred during authentication.';
    }
  }

  if (typeof error === 'object' && error !== null && 'code' in error && typeof (error as { code: unknown }).code === 'string') {
    const code = (error as { code: string }).code;
    if (code === 'auth/popup-closed-by-user') return 'Sign-in popup was closed before completing authentication.';
    if (code === 'auth/popup-blocked') return 'Sign-in popup was blocked by your browser. Please allow popups for this site.';
  }

  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected authentication error occurred.';
}
