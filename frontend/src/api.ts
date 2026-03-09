const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

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

export async function uploadFile(file: File, userId: number): Promise<{ document: DocumentItem }> {
  const form = new FormData();
  form.append("file", file);
  form.append("user_id", String(userId));
  const r = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: form,
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(err.detail || "Upload failed");
  }
  return r.json();
}

export async function uploadYoutube(url: string, userId: number): Promise<{ document_id: number }> {
  const form = new FormData();
  form.append("youtube_url", url);
  form.append("user_id", String(userId));
  const r = await fetch(`${API_BASE}/documents/youtube`, {
    method: "POST",
    body: form,
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(err.detail || "YouTube ingest failed");
  }
  return r.json();
}

export async function getDocuments(userId: number): Promise<DocumentItem[]> {
  const r = await fetch(`${API_BASE}/documents?user_id=${userId}`);
  if (!r.ok) throw new Error("Failed to load documents");
  return r.json();
}

export async function getQuestions(userId: number, documentId?: number): Promise<QuestionItem[]> {
  let url = `${API_BASE}/questions?user_id=${userId}`;
  if (documentId != null) url += `&document_id=${documentId}`;
  const r = await fetch(url);
  if (!r.ok) throw new Error("Failed to load questions");
  return r.json();
}
