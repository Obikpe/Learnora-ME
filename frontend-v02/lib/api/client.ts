const BASE = "";

type CacheEntry = { expiresAt: number; value: unknown };
const memoryCache = new Map<string, CacheEntry>();
const inFlight = new Map<string, Promise<unknown>>();
const CACHE_PREFIX = "learnora_api_cache_v1:";

export const token = () => {
  if (typeof window === "undefined") return "";
  if (sessionStorage.getItem("phx_logged_out") === "1" || localStorage.getItem("phx_logged_out") === "1") return "";
  localStorage.removeItem("phx_token");
  const value = sessionStorage.getItem("phx_token") || "";
  if (value && value !== "cookie-session") {
    sessionStorage.removeItem("phx_token");
    return "";
  }
  return value;
};

export const setToken = (_v: string) => {
  if (typeof window === "undefined") return;
  invalidateRequestCache();
  for (let index = sessionStorage.length - 1; index >= 0; index--) {
    const key = sessionStorage.key(index);
    if (key?.startsWith("learnora_current_user_cache:")) sessionStorage.removeItem(key);
  }
  localStorage.removeItem("phx_token");
  sessionStorage.removeItem("phx_logged_out");
  localStorage.removeItem("phx_logged_out");
  localStorage.setItem("phx_session_hint", "1");
  sessionStorage.setItem("phx_session_epoch", String(Date.now()) + "-" + Math.random().toString(36).slice(2));
  sessionStorage.setItem("phx_token", "cookie-session");
};

export const organisationContext = () => typeof window === "undefined" ? "" : localStorage.getItem("learnora_organisation_id") || "";
export const setOrganisationContext = (id: string) => { if (typeof window !== "undefined") { localStorage.setItem("learnora_organisation_id", id); invalidateRequestCache(); } };
export const clearOrganisationContext = () => { if (typeof window !== "undefined") { localStorage.removeItem("learnora_organisation_id"); invalidateRequestCache(); } };

function clearStoredCache() {
  if (typeof window === "undefined") return;
  try {
    for (let index = sessionStorage.length - 1; index >= 0; index--) {
      const key = sessionStorage.key(index);
      if (key?.startsWith(CACHE_PREFIX) || key?.startsWith("learnora_current_user_cache:")) sessionStorage.removeItem(key);
    }
  } catch {}
}

export function invalidateRequestCache() {
  memoryCache.clear();
  inFlight.clear();
  clearStoredCache();
}

export const clearToken = async (): Promise<boolean> => {
  if (typeof window === "undefined") return true;
  invalidateRequestCache();
  for (let index = sessionStorage.length - 1; index >= 0; index--) {
    const key = sessionStorage.key(index);
    if (key?.startsWith("learnora_current_user_cache:")) sessionStorage.removeItem(key);
  }
  for (let index = sessionStorage.length - 1; index >= 0; index--) {
    const key = sessionStorage.key(index);
    if (key && (key.startsWith("learnora_") || key.startsWith("phx_"))) sessionStorage.removeItem(key);
  }
  sessionStorage.removeItem("phx_token");
  sessionStorage.removeItem("phx_session_epoch");
  localStorage.removeItem("phx_token");
  localStorage.removeItem("phx_session_hint");
  localStorage.removeItem("learnora_organisation_id");
  sessionStorage.setItem("phx_logged_out", "1");
  localStorage.setItem("phx_logged_out", "1");
  clearOrganisationContext();
  try {
    const response = await fetch("/api/auth/logout", {
      method: "POST",
      credentials: "same-origin",
      keepalive: true,
      cache: "no-store",
    });
    return response.ok;
  } catch {
    return false;
  }
};

function cacheLifetime(path: string) {
  if (/^\/public\/(courses|tracks)(\/|$)/.test(path)) return 5 * 60_000;
  if (path === "/access/mode") return 5 * 60_000;
  if (path === "/learner/onboarding") return 2 * 60_000;
  if (/^\/progress\/(learning-summary|learning-sessions)([?\/]|$)/.test(path)) return 0;
  if (path === "/progress/me") return 60_000;
  if (path === "/evidence/me" || path === "/credentials/me") return 30_000;
  if (/^\/(notifications|ai|billing|payments|webhooks|admin|analytics|audit|reports)(\/|$)/.test(path)) return 0;
  return 20_000;
}

function mutationInvalidatesCache(path: string) {
  return !/^\/(ai|notifications|analytics|usage)(\/|$)/.test(path);
}

function cacheKey(path: string) {
  const isPublic = path.startsWith("/public/") || path === "/access/mode";
  if (isPublic) return CACHE_PREFIX + "public:" + path;
  if (typeof window === "undefined") return "";
  const epoch = sessionStorage.getItem("phx_session_epoch") || "implicit-session";
  return CACHE_PREFIX + epoch + ":" + organisationContext() + ":" + path;
}

function readCache<T>(key: string): T | undefined {
  const now = Date.now();
  const memory = memoryCache.get(key);
  if (memory && memory.expiresAt > now) return memory.value as T;
  if (memory) memoryCache.delete(key);
  if (typeof window === "undefined") return undefined;
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return undefined;
    const entry = JSON.parse(raw) as CacheEntry;
    if (!entry || entry.expiresAt <= now) { sessionStorage.removeItem(key); return undefined; }
    memoryCache.set(key, entry);
    return entry.value as T;
  } catch { return undefined; }
}

function writeCache(key: string, value: unknown, lifetime: number) {
  if (!key || !lifetime) return;
  const entry = { expiresAt: Date.now() + lifetime, value };
  memoryCache.set(key, entry);
  if (typeof window === "undefined") return;
  try {
    const serialised = JSON.stringify(entry);
    if (serialised.length <= 180_000) sessionStorage.setItem(key, serialised);
  } catch {}
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method || "GET").toUpperCase();
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const t = token();
  if (t && t !== "cookie-session") headers.set("Authorization", "Bearer " + t);
  const org = organisationContext();
  if (org && !headers.has("X-Organisation-ID")) headers.set("X-Organisation-ID", org);

  const lifetime = method === "GET" ? cacheLifetime(path) : 0;
  const key = lifetime ? cacheKey(path) : "";
  if (key) {
    const cached = readCache<T>(key);
    if (cached !== undefined) return cached;
    const pending = inFlight.get(key);
    if (pending) return pending as Promise<T>;
  }

  const url = BASE + "/api" + path;
  const pending = (async () => {
    const response = await fetch(url, {
      ...init,
      method,
      headers,
      cache: "no-store",
      credentials: "same-origin",
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401 && typeof window !== "undefined") {
        invalidateRequestCache();
        sessionStorage.removeItem("phx_token");
        sessionStorage.removeItem("phx_session_epoch");
        sessionStorage.setItem("phx_logged_out", "1");
        localStorage.setItem("phx_logged_out", "1");
        localStorage.removeItem("phx_session_hint");
      }
      const safeServerMessage =
        typeof body.detail === "string" && body.detail !== "Internal Server Error" ? body.detail
        : typeof body.message === "string" ? body.message
        : typeof body.error === "string" ? body.error
        : "";
      const message = safeServerMessage ||
        (response.status >= 500
          ? "Something went wrong while loading your information. Please try again. If the problem continues, contact Learnora support."
          : "We could not complete that request. Please try again.");
      const error = new Error(message) as Error & { status?: number };
      error.status = response.status;
      throw error;
    }
    if (key) writeCache(key, body, lifetime);
    else if (method !== "GET" && mutationInvalidatesCache(path)) invalidateRequestCache();
    return body as T;
  })();

  if (key) {
    inFlight.set(key, pending);
    pending.finally(() => { if (inFlight.get(key) === pending) inFlight.delete(key); }).catch(() => {});
  }
  return pending;
}
