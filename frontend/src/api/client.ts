import axios, { type AxiosError } from "axios";

import { useAuthStore } from "../stores/authStore";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  timeout: 20_000,
});

// Interceptor de autenticação: injeta o token JWT em toda requisição.
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor de erros: 401 remove a sessão e redireciona para login;
// 500 e indisponibilidade viram mensagens amigáveis, nunca stack traces.
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error?: { code: string; message: string } }>) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = "/login";
      return Promise.reject(error);
    }

    if (!error.response) {
      return Promise.reject(new Error("Backend indisponível. Verifique sua conexão."));
    }

    const apiError = error.response.data?.error;
    return Promise.reject(new Error(apiError?.message || "Ocorreu um erro inesperado."));
  }
);
