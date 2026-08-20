import apiClient, { TOKEN_STORAGE_KEY } from "./api";

export async function registerUser({ email, password, fullName }) {
  const { data } = await apiClient.post("/api/auth/register", {
    email,
    password,
    full_name: fullName || null,
  });
  return data;
}

export async function loginUser({ email, password }) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);

  const { data } = await apiClient.post("/api/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  localStorage.setItem(TOKEN_STORAGE_KEY, data.access_token);
  return data;
}

export function logoutUser() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get("/api/auth/me");
  return data;
}