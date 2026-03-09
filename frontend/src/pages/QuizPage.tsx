import { useEffect, useState } from "react";
import { getQuestions } from "../api";
import type { QuestionItem } from "../api";

const USER_ID = 1;

export default function QuizPage() {
  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [feedback, setFeedback] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getQuestions(USER_ID)
      .then((q) => {
        setQuestions(q);
        setScore({ correct: 0, total: q.length });
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  function submitAnswer() {
    if (questions.length === 0 || index >= questions.length) return;
    const q = questions[index];
    const isCorrect =
      answer.trim().toLowerCase() === q.correct_answer.trim().toLowerCase();
    setScore((s) => ({ ...s, correct: s.correct + (isCorrect ? 1 : 0) }));
    setFeedback(isCorrect ? "Correct!" : `Wrong. Answer: ${q.correct_answer}`);
  }

  function next() {
    setFeedback(null);
    setAnswer("");
    setIndex((i) => i + 1);
  }

  if (loading) return <div className="page"><p>Loading quiz…</p></div>;
  if (error) return <div className="page"><p className="error">{error}</p></div>;
  if (questions.length === 0)
    return (
      <div className="page">
        <h1>Quiz</h1>
        <p>No questions yet. Upload documents and wait for processing to generate questions.</p>
      </div>
    );

  const done = index >= questions.length;
  const current = questions[index];

  return (
    <div className="page">
      <h1>Quiz</h1>
      <p className="muted">
        {done ? "Done!" : `Question ${index + 1} of ${questions.length}`} · Score: {score.correct} / {score.total}
      </p>

      {done ? (
        <div className="quiz-result">
          <h2>Result</h2>
          <p>You got {score.correct} out of {score.total} correct.</p>
          <button type="button" onClick={() => { setIndex(0); setScore({ correct: 0, total: questions.length }); setFeedback(null); setAnswer(""); }}>
            Restart quiz
          </button>
        </div>
      ) : (
        <div className="quiz-card">
          <p className="question-text">{current.question_text}</p>
          <div className="quiz-answer">
            <input
              type="text"
              placeholder="Your answer"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submitAnswer()}
            />
            <button type="button" onClick={submitAnswer} disabled={feedback !== null}>
              Submit
            </button>
          </div>
          {feedback && (
            <div className={`feedback ${feedback.startsWith("Correct") ? "correct" : "wrong"}`}>
              {feedback}
              <button type="button" onClick={next}>Next</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
