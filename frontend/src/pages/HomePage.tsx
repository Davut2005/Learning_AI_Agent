import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <div className="page home">
      <h1>Learning AI Tracker & Quiz</h1>
      <p>Upload documents or YouTube links, then take quizzes on extracted concepts.</p>
      <div className="home-links">
        <Link to="/upload">Upload content</Link>
        <Link to="/documents">View documents</Link>
        <Link to="/quiz">Take quiz</Link>
        <Link to="/dashboard">Dashboard</Link>
      </div>
    </div>
  );
}
