import { useCallback, useEffect, useMemo, useState } from "react";

import { setUnauthorizedHandler } from "../../services/api.js";
import { AuthContext } from "./authContext.js";
import {
  fetchCurrentUser,
  loginUser,
  logoutUser,
} from "./authService.js";
import { clearTokens, getAccessToken } from "./tokenStorage.js";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const clearAuth = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    const nextUser = await fetchCurrentUser();
    setUser(nextUser);
    return nextUser;
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      clearAuth();
      window.location.assign("/login");
    });
  }, [clearAuth]);

  useEffect(() => {
    async function bootstrapAuth() {
      if (!getAccessToken()) {
        setIsLoading(false);
        return;
      }

      try {
        await refreshUser();
      } catch {
        clearAuth();
      } finally {
        setIsLoading(false);
      }
    }

    bootstrapAuth();
  }, [clearAuth, refreshUser]);

  async function login(credentials) {
    const nextUser = await loginUser(credentials);
    setUser(nextUser);
    return nextUser;
  }

  async function logout() {
    await logoutUser();
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
      refreshUser,
    }),
    [isLoading, refreshUser, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
