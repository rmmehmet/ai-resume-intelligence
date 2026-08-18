import axios from "axios";

/**
 * Centralized Axios instance.
 *
 * The base URL is read from environment configuration so it can differ
 * between local development, staging, and production without code changes.
 *
 * Feature-specific API calls (auth, resumes, jobs, etc.) will be added
 * as their own modules in later phases - this file only provides the
 * shared, configured client.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;