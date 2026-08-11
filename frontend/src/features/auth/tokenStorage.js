const ACCESS_TOKEN_KEY = "mta_hotel_access_token";
const REFRESH_TOKEN_KEY = "mta_hotel_refresh_token";

export function getAccessToken() {
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens({ access, refresh }) {
  if (access) {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, access);
  }

  if (refresh) {
    window.localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  }
}

export function clearTokens() {
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}
