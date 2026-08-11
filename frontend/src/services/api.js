import axios from "axios";

import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "../features/auth/tokenStorage.js";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

let refreshRequest = null;
let unauthorizedHandler = null;

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler;
}

api.interceptors.request.use((config) => {
  const access = getAccessToken();

  if (access) {
    config.headers.Authorization = `Bearer ${access}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    if (
      status !== 401 ||
      originalRequest?._retry ||
      originalRequest?.url?.includes("/auth/login/") ||
      originalRequest?.url?.includes("/auth/token/refresh/")
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshRequest) {
        const refresh = getRefreshToken();

        if (!refresh) {
          throw new Error("Missing refresh token.");
        }

        refreshRequest = api
          .post("/auth/token/refresh/", { refresh })
          .then((response) => {
            setTokens({
              access: response.data.access,
              refresh: response.data.refresh,
            });
            return response.data.access;
          })
          .finally(() => {
            refreshRequest = null;
          });
      }

      const access = await refreshRequest;
      originalRequest.headers.Authorization = `Bearer ${access}`;
      return api(originalRequest);
    } catch (refreshError) {
      clearTokens();
      unauthorizedHandler?.();
      return Promise.reject(refreshError);
    }
  },
);
