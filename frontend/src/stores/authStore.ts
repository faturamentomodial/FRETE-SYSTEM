import { create } from "zustand";

interface AuthState {
  token: string | null;
  setToken: (token: string) => void;
  logout: () => void;
}

const STORAGE_KEY = "frete-system:token";

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem(STORAGE_KEY),
  setToken: (token: string) => {
    localStorage.setItem(STORAGE_KEY, token);
    set({ token });
  },
  logout: () => {
    localStorage.removeItem(STORAGE_KEY);
    set({ token: null });
  },
}));
