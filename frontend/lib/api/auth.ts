import { apiClient } from "./client";
import { LoginRequest, TokenResponse, User } from "@/types";

export const authApi = {
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(
      "/api/auth/login",
      credentials
    );
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post("/api/auth/logout");
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>("/api/auth/me");
    return response.data;
  },

  refreshToken: async (): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>("/api/auth/refresh");
    return response.data;
  },
};
