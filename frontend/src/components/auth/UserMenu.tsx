import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { LogIn, LogOut, User as UserIcon, Cloud, ShieldAlert } from 'lucide-react';

export function UserMenu() {
  const { user, loading, loginWithGoogle, logout, isMockUser } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full glass animate-pulse">
        <div className="w-4 h-4 rounded-full bg-white/20" />
        <span className="text-xs text-muted-foreground">Checking auth...</span>
      </div>
    );
  }

  if (!user || (isMockUser && user.uid === 'local_dev_user')) {
    return (
      <button
        onClick={loginWithGoogle}
        className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-xs shadow-lg shadow-blue-500/20 transition-all transform hover:scale-105 active:scale-95"
        title="Sign in with Google to save projects to Cloud"
      >
        <LogIn className="w-3.5 h-3.5" />
        <span>Sign in with Google</span>
      </button>
    );
  }

  return (
    <div className="flex items-center gap-2 glass rounded-full pl-2 pr-3 py-1 border border-white/10 hover:border-white/20 transition-all">
      {user.photoURL ? (
        <img
          src={user.photoURL}
          alt={user.displayName || 'User'}
          className="w-6 h-6 rounded-full object-cover border border-white/20 shadow-sm"
        />
      ) : (
        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
          {user.displayName ? user.displayName[0].toUpperCase() : <UserIcon className="w-3.5 h-3.5" />}
        </div>
      )}
      <div className="flex flex-col text-left max-w-[110px]">
        <span className="text-xs font-medium text-foreground truncate">
          {user.displayName || 'User'}
        </span>
        <span className="text-[10px] text-emerald-400 flex items-center gap-0.5 leading-none">
          <Cloud className="w-2.5 h-2.5" /> Cloud Sync
        </span>
      </div>
      <button
        onClick={logout}
        className="ml-1 p-1 rounded-full hover:bg-white/10 text-muted-foreground hover:text-red-400 transition-colors"
        title="Sign out"
      >
        <LogOut className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
