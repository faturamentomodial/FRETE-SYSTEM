import { apiClient } from "../api/client";
import type { DashboardData } from "../types/dashboard";

export const dashboardService = {
  async obter(): Promise<DashboardData> {
    const { data } = await apiClient.get<DashboardData>("/dashboard");
    return data;
  },
};
