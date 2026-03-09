import { useState } from "react";
import { uploadFile, uploadYoutube } from "../api";

const DEFAULT_USER_ID = 1;

export default function UploadPage() {
  const [userId] = useState(DEFAULT_USER_ID);
  const [file, setFile] = useState<File | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [loading, setLoading] = useState<"file" | "youtube" | null>(null);
  const [message, setMessage] = useState<{ type: "ok" | "err"; text: string } | null>(null);

  async function handleFileSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setMessage({ type: "err", text: "Select a file" });
      return;
    }
    setMessage(null);
    setLoading("file");
    try {
      const res = await uploadFile(file, userId);
      setMessage({ type: "ok", text: `Uploaded: ${res.document.title}. Processing in background.` });
      setFile(null);
    } catch (err) {
      setMessage({ type: "err", text: err instanceof Error ? err.message : "Upload failed" });
    } finally {
      setLoading(null);
    }
  }

  async function handleYoutubeSubmit(e: React.FormEvent) {
    e.preventDefault();
    const url = youtubeUrl.trim();
    if (!url) {
      setMessage({ type: "err", text: "Enter a YouTube URL" });
      return;
    }
    setMessage(null);
    setLoading("youtube");
    try {
      await uploadYoutube(url, userId);
      setMessage({ type: "ok", text: "YouTube transcript ingested. Processing in background." });
      setYoutubeUrl("");
    } catch (err) {
      setMessage({ type: "err", text: err instanceof Error ? err.message : "Ingest failed" });
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="page">
      <h1>Upload</h1>
      <p className="muted">Add content for learning. Use user_id = {userId} (change in code if needed).</p>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <section className="upload-section">
        <h2>File upload</h2>
        <p>PDF, DOCX, TXT, or Markdown.</p>
        <form onSubmit={handleFileSubmit}>
          <input
            type="file"
            accept=".pdf,.docx,.txt,.md"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <button type="submit" disabled={loading !== null}>
            {loading === "file" ? "Uploading…" : "Upload file"}
          </button>
        </form>
      </section>

      <section className="upload-section">
        <h2>YouTube link</h2>
        <p>Paste a YouTube video URL to ingest its transcript.</p>
        <form onSubmit={handleYoutubeSubmit}>
          <input
            type="url"
            placeholder="https://www.youtube.com/watch?v=..."
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            disabled={loading !== null}
          />
          <button type="submit" disabled={loading !== null}>
            {loading === "youtube" ? "Ingesting…" : "Ingest YouTube"}
          </button>
        </form>
      </section>
    </div>
  );
}
