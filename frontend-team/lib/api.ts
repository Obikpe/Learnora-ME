const BASE = "";
type CacheEntry = { expiresAt: number; value: unknown };
const memoryCache = new Map<string, CacheEntry>();
const pendingRequests = new Map<string, Promise<unknown>>();
const CACHE_PREFIX = "learnora_team_api_cache_v1:";

export const token = () => {
  if (typeof window === "undefined") return "";
  localStorage.removeItem("learnora_team_token");
  const stored = sessionStorage.getItem("learnora_team_token") || "";
  if (stored && stored !== "cookie-session") { sessionStorage.removeItem("learnora_team_token"); return ""; }
  return stored;
};

export const setToken = (_value: string) => {
  if (typeof window === "undefined") return;
  localStorage.removeItem("learnora_team_token");
  sessionStorage.removeItem("learnora_team_logged_out");
  sessionStorage.setItem("learnora_team_session_epoch", String(Date.now()) + "-" + Math.random().toString(36).slice(2));
  sessionStorage.setItem("learnora_team_token", "cookie-session");
  sessionStorage.setItem("learnora_team_last_activity", String(Date.now()));
};

export function invalidateApiCache() {
  memoryCache.clear();
  pendingRequests.clear();
  if (typeof window === "undefined") return;
  try {
    for (let index = sessionStorage.length - 1; index >= 0; index--) {
      const key = sessionStorage.key(index);
      if (key?.startsWith(CACHE_PREFIX)) sessionStorage.removeItem(key);
    }
  } catch {}
}

export const clearToken = () => {
  if (typeof window === "undefined") return;
  invalidateApiCache();
  sessionStorage.removeItem("learnora_team_token");
  sessionStorage.removeItem("learnora_team_session_epoch");
  localStorage.removeItem("learnora_team_token");
  sessionStorage.setItem("learnora_team_logged_out", "1");
  sessionStorage.removeItem("learnora_team_last_activity");
  void fetch("/api/internal/auth/logout", { method: "POST", credentials: "same-origin", keepalive: true }).catch(() => {});
};

export class ApiRequestError extends Error {
  status: number;
  constructor(message: string, status: number) { super(message); this.name = "ApiRequestError"; this.status = status; }
}

function cacheableGet(path: string) {
  if (/^\/(ai|notifications|billing|payments|webhooks|audit|security|logs)(\/|$)/.test(path)) return 0;
  if (path.startsWith("/content/")) return 30_000;
  return 15_000;
}

function readCached<T>(key: string): T | undefined {
  const now = Date.now();
  const value = memoryCache.get(key);
  if (value && value.expiresAt > now) return value.value as T;
  if (value) memoryCache.delete(key);
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return undefined;
    const entry = JSON.parse(raw) as CacheEntry;
    if (!entry || entry.expiresAt <= now) { sessionStorage.removeItem(key); return undefined; }
    memoryCache.set(key, entry);
    return entry.value as T;
  } catch { return undefined; }
}

function storeCached(key: string, value: unknown, lifetime: number) {
  const entry = { expiresAt: Date.now() + lifetime, value };
  memoryCache.set(key, entry);
  try {
    const serialised = JSON.stringify(entry);
    if (serialised.length <= 120_000) sessionStorage.setItem(key, serialised);
  } catch {}
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method || "GET").toUpperCase();
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body) headers.set("Content-Type", "application/json");
  const accessToken = token();
  if (accessToken && accessToken !== "cookie-session") headers.set("Authorization", `Bearer ${accessToken}`);

  const lifetime = method === "GET" ? cacheableGet(path) : 0;
  const cacheKey = lifetime && typeof window !== "undefined"
    ? CACHE_PREFIX + (sessionStorage.getItem("learnora_team_session_epoch") || "implicit-session") + ":" + path
    : "";
  if (cacheKey) {
    const cached = readCached<T>(cacheKey);
    if (cached !== undefined) return cached;
    const pending = pendingRequests.get(cacheKey);
    if (pending) return pending as Promise<T>;
  }

  const pending = (async () => {
    let response: Response;
    try {
      response = await fetch(`${BASE}/api/internal${path}`, {
        ...init, method, headers, cache: "no-store", credentials: "same-origin",
      });
    } catch {
      throw new ApiRequestError("Cannot reach Learnora's backend. Check your connection and try again.", 0);
    }
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401 && typeof window !== "undefined") {
        invalidateApiCache();
        sessionStorage.removeItem("learnora_team_token");
        sessionStorage.removeItem("learnora_team_session_epoch");
        sessionStorage.setItem("learnora_team_logged_out", "1");
      }
      const message = typeof body.detail === "string" ? body.detail
        : typeof body.message === "string" ? body.message
        : `Internal request failed (${response.status})`;
      throw new ApiRequestError(message, response.status);
    }
    if (cacheKey) storeCached(cacheKey, body, lifetime);
    else if (method !== "GET") invalidateApiCache();
    return body as T;
  })();

  if (cacheKey) {
    pendingRequests.set(cacheKey, pending);
    pending.finally(() => { if (pendingRequests.get(cacheKey) === pending) pendingRequests.delete(cacheKey); }).catch(() => {});
  }
  return pending;
}

export const teamLogin = (email: string, password: string) =>
  request<any>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
export const teamMe = () => request<any>("/auth/me");
export const staff = () => request<any>("/staff");
export const staffRoles = () => request<any>("/staff/roles/catalog");
export const departments = () => request<any>("/departments");
export const teams = () => request<any>("/teams");
export const teamMembers = (id: string) => request<any>(`/teams/${encodeURIComponent(id)}/members`);
export const aiHealth = () => request<any>("/ai/health");
export const aiProfiles = () => request<any>("/ai/profiles");
export const updateAiProfile = (key: string, payload: any) =>
  request<any>(`/ai/profiles/${encodeURIComponent(key)}`, { method: "PATCH", body: JSON.stringify(payload) });
export const testAiProfile = (key: string) =>
  request<any>(`/ai/profiles/${encodeURIComponent(key)}/test`, { method: "POST" });
