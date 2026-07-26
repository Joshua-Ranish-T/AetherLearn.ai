import React, { createContext, useContext, useEffect, useState } from 'react';
import { onAuthStateChanged, User as FirebaseUser } from 'firebase/auth';
import { auth, signInWithGoogle, signOutUser, isFirebaseConfigured } from '../lib/firebase';
import { toast } from 'react-hot-toast';

export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  getIdToken: () => Promise<string>;
}

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  isMockUser: boolean;
}

const MOCK_DEV_USER: AuthUser = {
  uid: 'local_dev_user',
  email: 'dev@localhost',
  displayName: 'Local Developer',
  photoURL: '',
  getIdToken: async () => 'mock_dev_token',
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  loginWithGoogle: async () => {},
  logout: async () => {},
  isMockUser: true,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isMockUser, setIsMockUser] = useState<boolean>(!isFirebaseConfigured);

  useEffect(() => {
    const requireAuth = import.meta.env.VITE_REQUIRE_AUTH === 'true';
    if (!auth || !isFirebaseConfigured) {
      if (requireAuth) {
        setUser(null);
        setIsMockUser(false);
        setLoading(false);
        return;
      }
      // In local dev mode without Firebase config, default to mock developer user
      setUser(MOCK_DEV_USER);
      setIsMockUser(true);
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, (firebaseUser: FirebaseUser | null) => {
      if (firebaseUser) {
        setUser({
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          displayName: firebaseUser.displayName || 'Google User',
          photoURL: firebaseUser.photoURL,
          getIdToken: () => firebaseUser.getIdToken(),
        });
        setIsMockUser(false);
      } else {
        // If require_auth is false or unset in dev, fallback to mock user when logged out
        if (!requireAuth) {
          setUser(MOCK_DEV_USER);
          setIsMockUser(true);
        } else {
          setUser(null);
          setIsMockUser(false);
        }
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const loginWithGoogle = async () => {
    try {
      setLoading(true);
      const res = await signInWithGoogle();
      if (res && 'getIdToken' in res) {
        if (typeof res.getIdToken === 'function') {
          const token = await res.getIdToken();
          setUser({
            uid: res.uid,
            email: res.email || 'dev@localhost',
            displayName: res.displayName || 'Google User',
            photoURL: res.photoURL || '',
            getIdToken: async () => token,
          });
          setIsMockUser(res.uid === 'local_dev_user');
          toast.success(`Signed in as ${res.displayName || 'User'}`);
        }
      }
    } catch (error: any) {
      console.error('Failed to sign in:', error);
      toast.error(error?.message || 'Failed to sign in with Google');
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await signOutUser();
      const requireAuth = import.meta.env.VITE_REQUIRE_AUTH === 'true';
      if (!requireAuth) {
        setUser(MOCK_DEV_USER);
        setIsMockUser(true);
        toast.success('Signed out (switched to Local Dev mode)');
      } else {
        setUser(null);
        setIsMockUser(false);
        toast.success('Signed out successfully');
      }
    } catch (error: any) {
      console.error('Failed to sign out:', error);
      toast.error('Failed to sign out');
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginWithGoogle, logout, isMockUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
