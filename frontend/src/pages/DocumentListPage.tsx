import { useEffect, useState } from "react";
import { getDocuments } from "../api";
import type { DocumentItem } from "../api";

const USER_ID = 1;

export default function DocumentListPage() {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDocuments(USER_ID)
      .then(setDocs)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page"><p>Loading documents…</p></div>;
  if (error) return <div className="page"><p className="error">{error}</p></div>;

  return (
    <div className="page">
      <h1>Document list</h1>
      <p className="muted">Your uploaded documents .</p>
      {docs.length === 0 ? (
        <p>No documents yet. Upload a file or add a YouTube link from the Upload page.</p>
      ) : (
        <ul className="doc-list">
          {docs.map((d) => (
            <li key={d.id}>
              <strong>{d.title}</strong>
              <span className="doc-meta">ID: {d.id} · {d.source}</span>
              <span className="doc-date">{new Date(d.created_at).toLocaleDateString()}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
