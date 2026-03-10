import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  createLearningPath,
  addDocumentToPath,
  addYouTubeToPath,
} from "../api";

type UrlEntry = { id: number; value: string };

let urlCounter = 0;

export default function CreatePathPage() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [hoursPerDay, setHoursPerDay] = useState(1);
  const [files, setFiles] = useState<File[]>([]);
  const [urlEntries, setUrlEntries] = useState<UrlEntry[]>([{ id: ++urlCounter, value: "" }]);
  const [submitting, setSubmitting] = useState(false);
  const [progress, setProgress] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function addUrlEntry() {
    setUrlEntries((prev) => [...prev, { id: ++urlCounter, value: "" }]);
  }

  function removeUrlEntry(id: number) {
    setUrlEntries((prev) => prev.filter((e) => e.id !== id));
  }

  function updateUrlEntry(id: number, value: string) {
    setUrlEntries((prev) => prev.map((e) => (e.id === id ? { ...e, value } : e)));
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const picked = Array.from(e.target.files || []);
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name + f.size));
      return [...prev, ...picked.filter((f) => !existing.has(f.name + f.size))];
    });
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function removeFile(index: number) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  const validUrls = urlEntries.map((e) => e.value.trim()).filter(Boolean);
  const hasAnySources = files.length > 0 || validUrls.length > 0;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) { setError("Please enter a path title."); return; }
    setError(null);
    setSubmitting(true);
    setProgress([]);

    try {
      // 1. Create the learning path
      setProgress(["Creating your learning path…"]);
      const path = await createLearningPath({
        title: title.trim(),
        description: description.trim() || undefined,
        hours_per_day: hoursPerDay,
      });

      // 2. Upload files
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setProgress((p) => [...p, `Uploading "${file.name}" (${i + 1}/${files.length})…`]);
        try {
          await addDocumentToPath(path.id, file);
        } catch (err) {
          setProgress((p) => [...p, `  ⚠ ${(err as Error).message}`]);
        }
      }

      // 3. Add YouTube URLs
      for (let i = 0; i < validUrls.length; i++) {
        const url = validUrls[i];
        const short = url.length > 60 ? url.slice(0, 57) + "…" : url;
        setProgress((p) => [...p, `Adding YouTube URL (${i + 1}/${validUrls.length}): ${short}`]);
        try {
          await addYouTubeToPath(path.id, url);
        } catch (err) {
          setProgress((p) => [...p, `  ⚠ ${(err as Error).message}`]);
        }
      }

      setProgress((p) => [...p, "Done! Redirecting to your roadmap…"]);
      setTimeout(() => navigate(`/paths/${path.id}`), 800);
    } catch (err) {
      setError((err as Error).message);
      setSubmitting(false);
    }
  }

  return (
    <div className="page create-path-page">
      <h1>Create a Learning Path</h1>
      <p className="muted">
        Describe what you want to learn, set your daily study time, and add your materials.
        We'll build a personalised day-by-day roadmap for you.
      </p>

      {error && <div className="message err">{error}</div>}

      {submitting ? (
        <div className="progress-panel">
          <div className="progress-spinner" />
          <ul className="progress-log">
            {progress.map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
        </div>
      ) : (
        <form className="create-path-form" onSubmit={handleSubmit}>
          {/* ── Path details ─────────────────────────────────── */}
          <section className="cp-section">
            <h2>Path details</h2>

            <label className="cp-label">
              Title <span className="required">*</span>
              <input
                type="text"
                placeholder="e.g. Machine Learning Fundamentals"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={512}
                required
              />
            </label>

            <label className="cp-label">
              What do you want to learn?
              <textarea
                placeholder="Describe your learning goal. The AI uses this to write your day titles."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </label>

            <div className="cp-label">
              <span>
                Daily study time&ensp;
                <strong className="accent">{hoursPerDay} hour{hoursPerDay !== 1 ? "s" : ""}</strong>
              </span>
              <div className="hours-row">
                <span className="hours-bound">30 min</span>
                <input
                  type="range"
                  min={0.5}
                  max={8}
                  step={0.5}
                  value={hoursPerDay}
                  onChange={(e) => setHoursPerDay(Number(e.target.value))}
                  className="hours-slider"
                />
                <span className="hours-bound">8 hrs</span>
              </div>
              <p className="cp-hint">
                We estimate ~15 min per content chunk, so {hoursPerDay} hr/day ≈{" "}
                <strong>{Math.max(1, Math.round(hoursPerDay * 4))} chunks</strong> per session.
              </p>
            </div>
          </section>

          {/* ── Documents ─────────────────────────────────────── */}
          <section className="cp-section">
            <h2>Documents <span className="optional">(optional)</span></h2>
            <p className="cp-hint">PDF, DOCX, TXT, or Markdown files.</p>

            <div className="file-drop-area" onClick={() => fileInputRef.current?.click()}>
              <span className="file-drop-icon">📄</span>
              <span>Click to select files</span>
              <span className="cp-hint">or drag & drop</span>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.md,text/plain,text/markdown"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
            </div>

            {files.length > 0 && (
              <ul className="file-list">
                {files.map((f, i) => (
                  <li key={i} className="file-item">
                    <span className="file-name">{f.name}</span>
                    <span className="file-size">{(f.size / 1024).toFixed(0)} KB</span>
                    <button
                      type="button"
                      className="file-remove"
                      onClick={() => removeFile(i)}
                      aria-label="Remove file"
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* ── YouTube URLs ──────────────────────────────────── */}
          <section className="cp-section">
            <h2>YouTube URLs <span className="optional">(optional)</span></h2>
            <p className="cp-hint">Paste video URLs — we'll extract the transcript automatically.</p>

            <div className="url-list">
              {urlEntries.map((entry) => (
                <div key={entry.id} className="url-row">
                  <input
                    type="url"
                    placeholder="https://youtube.com/watch?v=…"
                    value={entry.value}
                    onChange={(e) => updateUrlEntry(entry.id, e.target.value)}
                  />
                  {urlEntries.length > 1 && (
                    <button
                      type="button"
                      className="url-remove"
                      onClick={() => removeUrlEntry(entry.id)}
                      aria-label="Remove URL"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button type="button" className="btn-add-url" onClick={addUrlEntry}>
              + Add another URL
            </button>
          </section>

          {/* ── Submit ────────────────────────────────────────── */}
          <button
            type="submit"
            className="btn-primary btn-submit"
            disabled={!title.trim()}
          >
            {hasAnySources ? "Create path & start processing" : "Create path"}
          </button>
          {!hasAnySources && (
            <p className="cp-hint" style={{ marginTop: "0.5rem" }}>
              You can add documents later from the path page.
            </p>
          )}
        </form>
      )}
    </div>
  );
}
