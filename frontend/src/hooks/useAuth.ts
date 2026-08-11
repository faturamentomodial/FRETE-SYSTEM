import { useMutation } from "@tanstack/react-query";

import { authService } from "../services/authService";
import { useAuthStore } from "../stores/authStore";
import type { LoginRequest } from "../types/auth";

export function useAuth() {
  const { token, logout } = useAuthStore();
  const setToken = useAuthStore((s) => s.setToken);

  const loginMutation = useMutation({
    mutationFn: (payload: LoginRequest) => authService.login(payload),
    onSuccess: (data) => setToken(data.access_token),
  });

  return {
    isAuthenticated: Boolean(token),
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error as Error | null,
    logout,
  };
}
