import { create } from 'zustand';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  subscription_plan: string;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  setUser: (user: User) => void;
  loadAuthFromStorage: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('access_token') : null,
  isAuthenticated: typeof window !== 'undefined' ? !!localStorage.getItem('access_token') : false,
  
  login: (user, token) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ user, token, isAuthenticated: true });
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    set({ user: null, token: null, isAuthenticated: false });
  },
  
  setUser: (user) => set({ user }),
  
  loadAuthFromStorage: () => {
    try {
      const savedToken = localStorage.getItem('access_token');
      const savedUser = localStorage.getItem('user');
      
      if (savedToken && savedUser) {
        const user = JSON.parse(savedUser);
        set({ user, token: savedToken, isAuthenticated: true });
      }
    } catch (e) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  },
}));
