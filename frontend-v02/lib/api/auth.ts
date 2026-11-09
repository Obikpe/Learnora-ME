import { request } from "./client";

let cachedUser: any = null;
let cachedForToken = "";
let cachedAt = 0;
let currentUserRequest: Promise<any> | null = null;
const USER_CACHE_PREFIX = "learnora_current_user_cache:";

function restoreCachedUser(token: string) {
  if (cachedUser && cachedForToken === token) return cachedUser;
  if (typeof window === "undefined") return null;
  try {
    const epoch = sessionStorage.getItem("phx_session_epoch") || "implicit";
    const raw = sessionStorage.getItem(USER_CACHE_PREFIX + epoch);
    if (!raw) return null;
    const saved = JSON.parse(raw);
    if (!saved?.user || typeof saved.savedAt !== "number") return null;
    cachedUser = saved.user;
    cachedAt = saved.savedAt;
    cachedForToken = token;
    return cachedUser;
  } catch { return null; }
}

function activeToken() {
  if (typeof window === "undefined") return "";
  if (sessionStorage.getItem("phx_logged_out") === "1" || localStorage.getItem("phx_logged_out") === "1") return "";
  const stored = sessionStorage.getItem("phx_token") || "";
  if (stored && stored !== "cookie-session") sessionStorage.removeItem("phx_token");
  return "cookie-session:" + (sessionStorage.getItem("phx_session_epoch") || "implicit");
}

/** Synchronous cache read for client-side route transitions. */
export function getCachedCurrentUser() {
  const token = activeToken();
  return token ? restoreCachedUser(token) : null;
}

export const login = (email: string, password: string) =>
  request<any>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });

export const register = (name: string, email: string, password: string, marketingEmailOptIn = false) =>
  request<any>("/auth/register", { method: "POST", body: JSON.stringify({
    name, email, password, marketing_email_opt_in: marketingEmailOptIn,
  }) });

export function currentUser(): Promise<any> {
  const token = activeToken();
  if (!token) {
    cachedUser = null;
    cachedForToken = "";
    return Promise.reject(new Error("Your session has expired. Please sign in again."));
  }

  if (cachedUser && cachedForToken === token && Date.now() - cachedAt < 120_000) return Promise.resolve(cachedUser);
  restoreCachedUser(token);
  if (cachedUser && cachedForToken === token && Date.now() - cachedAt < 120_000) return Promise.resolve(cachedUser);
  if (currentUserRequest && cachedForToken === token) return currentUserRequest;

  cachedForToken = token;
  const pending = request<any>("/auth/me")
    .then((user) => {
      if (activeToken() === token) {
        cachedUser = user;
        cachedAt = Date.now();
        try {
          const epoch = sessionStorage.getItem("phx_session_epoch") || "implicit";
          sessionStorage.setItem(USER_CACHE_PREFIX + epoch, JSON.stringify({ savedAt: cachedAt, user }));
        } catch {}
      }
      return user;
    })
    .catch((error) => {
      if (cachedForToken === token) {
        cachedUser = null;
        cachedAt = 0;
        cachedForToken = "";
      }
      throw error;
    });

  currentUserRequest = pending;
  pending.then(
    () => { if (currentUserRequest === pending) currentUserRequest = null; },
    () => { if (currentUserRequest === pending) currentUserRequest = null; }
  );

  return pending;
}

export const forgotPassword = (email: string) =>
  request<any>("/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) });
