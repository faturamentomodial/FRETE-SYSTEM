import { apiClient } from "../api/client";
import type { LoginRequest, TokenResponse } from "../types/auth";

export const authService = {
  async login(payload: LoginRequest): Promise<TokenResponse> {
    const { data } = await apiClient.post<TokenResponse>("/auth/login", payload);
    return data;
  },
};
