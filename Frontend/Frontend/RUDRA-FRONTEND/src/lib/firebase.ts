import { getApp, getApps, initializeApp } from 'firebase/app';
import { getAuth, browserLocalPersistence, type Auth } from 'firebase/auth';

const getEnv = (key: string): string => {
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return (import.meta.env[key] as string) || '';
  }
  return '';
};

const apiKey = getEnv('NEXT_PUBLIC_FIREBASE_API_KEY') || getEnv('VITE_FIREBASE_API_KEY') || 'AIzaSyBkyhzbJ4q1KNVoKvAOypgfMuQsAl0u-mc';
const authDomain = getEnv('NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN') || getEnv('VITE_FIREBASE_AUTH_DOMAIN') || 'rudra-ff130.firebaseapp.com';
const projectId = getEnv('NEXT_PUBLIC_FIREBASE_PROJECT_ID') || getEnv('VITE_FIREBASE_PROJECT_ID') || 'rudra-ff130';
const storageBucket = getEnv('NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET') || getEnv('VITE_FIREBASE_STORAGE_BUCKET') || 'rudra-ff130.firebasestorage.app';
const messagingSenderId = getEnv('NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID') || getEnv('VITE_FIREBASE_MESSAGING_SENDER_ID') || '762725633555';
const appId = getEnv('NEXT_PUBLIC_FIREBASE_APP_ID') || getEnv('VITE_FIREBASE_APP_ID') || '1:762725633555:web:6a4f155bcc3d219e63b9e6';
const measurementId = getEnv('NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID') || getEnv('VITE_FIREBASE_MEASUREMENT_ID') || 'G-RQDP9NK227';

const firebaseConfig = {
  apiKey,
  authDomain,
  projectId,
  storageBucket,
  messagingSenderId,
  appId,
  measurementId,
};

// Prevent duplicate initialization
const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);

// Configure auth with proper settings
let authInstance: Auth;
try {
  authInstance = getAuth(app);
  // Persist the Firebase session in localStorage so the user stays signed in
  // across page reloads instead of being forced to re-authenticate every time.
  authInstance.setPersistence(browserLocalPersistence);
} catch (err) {
  console.warn('Firebase getAuth warning:', err);
  authInstance = getAuth(app);
}

export const auth = authInstance;
export default app;
