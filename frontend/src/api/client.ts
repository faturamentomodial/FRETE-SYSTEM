import axios, { type AxiosError } from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  timeout: 20_000,
  withCredentials: true,
});

// Interceptor de erros: 401 remove a sessão e redireciona para login;
// 500 e indisponibilidade viram mensagens amigáveis, nunca stack traces.
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string; error?: { code: string; message: string } }>) => {
    if (error.response?.status === 401) {
      return Promise.reject(error);
    }

    if (!error.response) {
      return Promise.reject(new Error("Backend indisponível. Verifique sua conexão."));
    }

    const apiError = error.response.data?.error;
    return Promise.reject(new Error(apiError?.message || error.response.data?.detail || "Ocorreu um erro inesperado."));
  }
);
