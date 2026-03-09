const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const AUTH_TOKEN_KEY = "learning_ai_token";

export function getToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function removeToken(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

function authHeaders(): HeadersInit {
  const token = getToken();
  const h: HeadersInit = {};
  if (token) (h as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  return h;
}

export type DocumentItem = {
  id: number;
  user_id: number;
  title: string;
  source: string;
  created_at: string;
  updated_at: string;
};

export type QuestionItem = {
  id: number;
  concept_id: number;
  question_text: string;
  correct_answer: string;
  options: { difficulty?: string } | null;
};

export type UserItem = {
  id: number;
  email: string;
  full_name: string | null;
};

export async function login(email: string, password: string): Promise<{ access_token: string }> {
  const r = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(err.detail || "Login failed");
  }
  return r.json();
}

export async function signup(
  email: string,
  password: string,
  fullName?: string
): Promise<{ access_token: string }> {
  const r = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName || null }),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: "Signup failed" }));
    throw new Error(err.detail || "Signup failed");
  }
  return r.json();
}

export async function getMe(): Promise<UserItem> {
  const r = await fetch(`${API_BASE}/auth/me`, { headers: authHeaders() });
  if (!r.ok) throw new Error("Not authenticated");
  return r.json();
}

export async function uploadFile(file: File): Promise<{ document: DocumentItem }> {
  const form = new FormData();
  form.append("file", file);
  const r = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    const msg =
      r.status === 503
        ? "Service temporarily unavailable. The database may be offline—check your connection or try again later."
        : r.status === 401
          ? "Please log in again."
          : (err.detail || "Upload failed");
    throw new Error(msg);
  }
  return r.json();
}

export async function uploadYoutube(url: string): Promise<{ document_id: number }> {
  const form = new FormData();
  form.append("youtube_url", url);
  const r = await fetch(`${API_BASE}/documents/youtube`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    const msg =
      r.status === 503
        ? "Service temporarily unavailable. The database may be offline."
        : r.status === 401
          ? "Please log in again."
          : (err.detail || "YouTube ingest failed");
    throw new Error(msg);
  }
  return r.json();
}

export async function getDocuments(): Promise<DocumentItem[]> {
  const r = await fetch(`${API_BASE}/documents`, { headers: authHeaders() });
  if (!r.ok) {
    if (r.status === 401) throw new Error("Please log in again.");
    throw new Error("Failed to load documents");
  }
  return r.json();
}

export async function getQuestions(documentId?: number): Promise<QuestionItem[]> {
  let url = `${API_BASE}/questions`;
  if (documentId != null) url += `?document_id=${documentId}`;
  const r = await fetch(url, { headers: authHeaders() });
  if (!r.ok) {
    if (r.status === 401) throw new Error("Please log in again.");
    throw new Error("Failed to load questions");
  }
  return r.json();
}
