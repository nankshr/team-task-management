import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor to add Authorization header
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.accessToken && config.headers) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for token refresh
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Don't retry if:
        // - It's the refresh endpoint itself (would cause infinite loop)
        // - It's the login endpoint (login failures shouldn't trigger refresh)
        // - Already retried (prevent infinite loops)
        // - On login page (no point refreshing when not logged in)
        // - No refresh token available
        const isOnLoginPage = typeof window !== "undefined" && window.location.pathname === "/login";

        if (
          (error.response?.status === 401 || error.response?.status === 403) &&
          !originalRequest._retry &&
          !originalRequest.url?.includes("/api/auth/refresh") &&
          !originalRequest.url?.includes("/api/auth/login") &&
          !isOnLoginPage &&
          this.refreshToken
        ) {
          originalRequest._retry = true;

          try {
            const response = await this.client.post("/api/auth/refresh", {}, {
              headers: {
                Authorization: `Bearer ${this.refreshToken}`,
              },
            });

            const { access_token, refresh_token } = response.data;
            this.setTokens(access_token, refresh_token);

            // Retry the original request with new token
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
            }
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            this.clearTokens();
            if (typeof window !== "undefined" && window.location.pathname !== "/login") {
              window.location.href = "/login";
            }
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  public setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
  }

  public clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
  }

  public getAccessToken(): string | null {
    return this.accessToken;
  }

  public getInstance(): AxiosInstance {
    return this.client;
  }
}

const apiClientInstance = new APIClient();

export const apiClient = apiClientInstance.getInstance();
export const setAuthTokens = (accessToken: string, refreshToken: string) =>
  apiClientInstance.setTokens(accessToken, refreshToken);
export const clearAuthTokens = () => apiClientInstance.clearTokens();
export const getAccessToken = () => apiClientInstance.getAccessToken();
