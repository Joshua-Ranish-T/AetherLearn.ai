// Firebase client initialization and Google Auth provider
import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || '',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || '',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || '',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '',
};

export const isFirebaseConfigured = Boolean(
  firebaseConfig.apiKey &&
  firebaseConfig.projectId &&
  firebaseConfig.apiKey !== 'your-api-key-here' &&
  firebaseConfig.projectId !== 'your-project-id'
);

// Initialize Firebase only if configured
const app = isFirebaseConfigured
  ? (!getApps().length ? initializeApp(firebaseConfig) : getApp())
  : null;

export const auth = app ? getAuth(app) : null;
export const googleProvider = new GoogleAuthProvider();

if (googleProvider) {
  googleProvider.setCustomParameters({
    prompt: 'select_account',
  });
}

/**
 * Sign in with Google using a popup window.
 * Returns user object or mock user if Firebase is not configured in local dev mode.
 */
export async function signInWithGoogle() {
  if (!auth) {
    if (import.meta.env.VITE_REQUIRE_AUTH === 'true') {
      throw new Error('Firebase Authentication is required in production mode. Please provide valid Firebase configuration in .env.');
    }
    console.warn('Firebase not configured. Signing in with mock local developer account.');
    return {
      uid: 'local_dev_user',
      email: 'dev@localhost',
      displayName: 'Local Developer',
      photoURL: '',
      getIdToken: async () => 'mock_dev_token',
    };
  }
  try {
    const result = await signInWithPopup(auth, googleProvider);
    return result.user;
  } catch (error) {
    console.error('Google sign-in error:', error);
    throw error;
  }
}

/**
 * Sign out the current user.
 */
export async function signOutUser() {
  if (!auth) {
    return;
  }
  return signOut(auth);
}
