import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  subscription_plan: string;
  is_admin?: boolean;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  setUser: (user: User) => void;
  // Kept for backward compatibility if any legacy component calls it, though persist handles hydration now.
  loadAuthFromStorage: () => void; 
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: (user, token) => {
        // Keep explicit token for API interceptors
        localStorage.setItem('access_token', token);
        set({ user, token, isAuthenticated: true });
      },
      
      logout: () => {
        localStorage.removeItem('access_token');
        set({ user: null, token: null, isAuthenticated: false });
      },
      
      setUser: (user) => set({ user }),
      
      loadAuthFromStorage: () => {
        // Zustand persist automatically hydrates this store on mount. 
        // This is a no-op fallback to prevent crashes if _app.tsx aggressively calls it.
        const token = localStorage.getItem('access_token');
        if (!token) set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
      // only persist these fields
      partialize: (state) => ({ 
        user: state.user, 
        token: state.token, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);
