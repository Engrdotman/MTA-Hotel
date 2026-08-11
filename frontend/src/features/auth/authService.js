import { api } from "../../services/api.js";
import { clearTokens, getRefreshToken, setTokens } from "./tokenStorage.js";

export async function loginUser(credentials) {
  const response = await api.post("/auth/login/", credentials);
  setTokens({
    access: response.data.access,
    refresh: response.data.refresh,
  });
  return response.data.user;
}

export async function fetchCurrentUser() {
  const response = await api.get("/auth/me/");
  return response.data;
}

export async function logoutUser() {
  const refresh = getRefreshToken();

  try {
    if (refresh) {
      await api.post("/auth/logout/", { refresh });
    }
  } finally {
    clearTokens();
  }
}

export async function refreshAccessToken() {
  const refresh = getRefreshToken();

  if (!refresh) {
    throw new Error("Missing refresh token.");
  }

  const response = await api.post("/auth/token/refresh/", { refresh });
  setTokens({
    access: response.data.access,
    refresh: response.data.refresh,
  });

  return response.data.access;
}
