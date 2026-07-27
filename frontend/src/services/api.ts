import axios from 'axios';
import { auth, isFirebaseConfigured } from '../lib/firebase';

// Use relative URLs in development so requests go through Vite's proxy
// (avoids cross-origin ERR_CONNECTION_RESET issues).
// In production, set VITE_API_URL to the actual backend URL.
const BASE_URL = import.meta.env.VITE_API_URL || '';

// Storage files (videos, audio, transcripts) are served by the backend's
// static file mount. Vite's SPA fallback intercepts /storage requests,
// so we must point directly at the backend for binary file access.
const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Resolve a storage path (e.g. "/storage/projects/.../video.mp4")
 * to a full URL pointing at the backend.
 * Returns empty string for falsy inputs.
 */
export function resolveStorageUrl(path: string | undefined | null): string {
  if (!path) return '';
  // If it's already a full URL, return as-is
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  // Prepend backend URL for relative storage paths
  return `${BACKEND_URL}${path.startsWith('/') ? '' : '/'}${path}`;
}

export const apiClient = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000,
});

// Request interceptor
apiClient.interceptors.request.use(
  async (config) => {
    try {
      if (auth) {
        // Wait for Firebase auth state to initialize from storage if not ready
        await auth.authStateReady();
      }
      if (auth && auth.currentUser) {
        const token = await auth.currentUser.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
      } else if (!isFirebaseConfigured) {
        // In local development mode without Firebase config, attach mock token
        config.headers.Authorization = `Bearer mock_dev_token`;
      }
      // If Firebase is configured but user is logged out, do not send mock token
    } catch (e) {
      console.warn('Could not attach auth token:', e);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred';
    
    console.error('API Error:', { 
      status: error.response?.status,
      message,
      url: error.config?.url,
    });
    
    return Promise.reject(new Error(message));
  }
);

export const SSE_BASE_URL = `${BASE_URL}/api/v1`;

