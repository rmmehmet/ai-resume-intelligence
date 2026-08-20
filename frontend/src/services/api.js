import axios from "axios";

/**
 * Centralized Axios instance.
 *
 * The base URL is read from environment configuration so it can differ
 * between local development, staging, and production without code changes.
 *
 * A request interceptor attaches the stored auth token (if any) to every
 * outgoing request. A response interceptor clears the token and redirects
 * to /login on 401s, so an expired/invalid session is handled in one place
 * instead of every component that calls the API.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const TOKEN_STORAGE_KEY = "resumeiq_token";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      if (window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;