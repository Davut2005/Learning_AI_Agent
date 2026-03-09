import { useEffect, useState } from "react";
import { getDocuments, getQuestions } from "../api";

const USER_ID = 1;

export default function DashboardPage() {
  const [docCount, setDocCount] = useState(0);
  const [questionCount, setQuestionCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDocuments(USER_ID), getQuestions(USER_ID)])
      .then(([docs, questions]) => {
        setDocCount(docs.length);
        setQuestionCount(questions.length);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page"><p>Loading…</p></div>;

  return (
    <div className="page">
      <h1>Learning progress</h1>
      <p className="muted">Overview of your learning content and quiz readiness.</p>
      <div className="dashboard-cards">
        <div className="card-stat">
          <span className="stat-value">{docCount}</span>
          <span className="stat-label">Documents</span>
        </div>
        <div className="card-stat">
          <span className="stat-value">{questionCount}</span>
          <span className="stat-label">Quiz questions</span>
        </div>
      </div>
      <p className="muted small">
        Upload documents and YouTube links to generate concepts and questions. Processing runs in the background.
      </p>
    </div>
  );
}
