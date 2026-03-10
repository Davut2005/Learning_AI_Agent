import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getLearningPaths, deleteLearningPath, type LearningPathSummary } from "../api";

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    processing: { label: "Processing…", cls: "badge-processing" },
    ready: { label: "Ready", cls: "badge-ready" },
    error: { label: "Error", cls: "badge-error" },
  };
  const { label, cls } = map[status] ?? { label: status, cls: "" };
  return <span className={`status-badge ${cls}`}>{label}</span>;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function PathsListPage() {
  const [paths, setPaths] = useState<LearningPathSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);

  async function load() {
    try {
      const data = await getLearningPaths();
      setPaths(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleDelete(id: number, title: string) {
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;
    setDeleting(id);
    try {
      await deleteLearningPath(id);
      setPaths((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setDeleting(null);
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>My Learning Paths</h1>
        <Link to="/paths/new" className="btn-primary btn-sm">+ New path</Link>
      </div>
      <p className="muted">Each path has a personalised day-by-day roadmap generated for you.</p>

      {loading && <p className="muted">Loading…</p>}
      {error && <div className="message err">{error}</div>}

      {!loading && paths.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🗺️</div>
          <p>No learning paths yet.</p>
          <Link to="/paths/new" className="btn-primary">Create your first path</Link>
        </div>
      )}

      <ul className="path-list">
        {paths.map((p) => (
          <li key={p.id} className="path-card">
            <div className="path-card-main">
              <div className="path-card-top">
                <Link to={`/paths/${p.id}`} className="path-title">{p.title}</Link>
                <StatusBadge status={p.status} />
              </div>
              {p.description && (
                <p className="path-description">{p.description}</p>
              )}
              <div className="path-meta">
                <span>⏱ {p.hours_per_day} hr/day</span>
                {p.total_days != null && p.total_days > 0 && (
                  <span>📅 {p.total_days} days</span>
                )}
                <span>📄 {p.document_count} source{p.document_count !== 1 ? "s" : ""}</span>
                <span className="doc-date">Created {formatDate(p.created_at)}</span>
              </div>
            </div>
            <div className="path-card-actions">
              <Link to={`/paths/${p.id}`} className="btn-sm">View roadmap →</Link>
              <button
                type="button"
                className="btn-sm btn-danger"
                onClick={() => handleDelete(p.id, p.title)}
                disabled={deleting === p.id}
              >
                {deleting === p.id ? "Deleting…" : "Delete"}
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
