"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { User, LoginRequest } from "@/types";
import { authApi } from "@/lib/api";
import { setAuthTokens, clearAuthTokens, getAccessToken } from "@/lib/api/client";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated on mount (skip on login page)
    const checkAuth = async () => {
      // Don't check auth on login page to avoid unnecessary API calls
      if (typeof window !== "undefined" && window.location.pathname === "/login") {
        setIsLoading(false);
        return;
      }

      // Only check auth if we have a token
      if (!getAccessToken()) {
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await authApi.getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        setUser(null);
        clearAuthTokens();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const tokenResponse = await authApi.login(credentials);
      // Store tokens in memory
      setAuthTokens(tokenResponse.access_token, tokenResponse.refresh_token);

      // Fetch current user info
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
      router.push("/dashboard");
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Even if logout fails, continue to clear local state
      console.error("Logout error:", error);
    } finally {
      // Clear tokens and user state
      clearAuthTokens();
      setUser(null);
      router.push("/login");
    }
  };

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
