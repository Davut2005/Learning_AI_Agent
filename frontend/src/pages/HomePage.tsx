import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function HomePage() {
  const { user } = useAuth();
  return (
    <div className="page home">
      <h1>Learning AI Tracker & Quiz</h1>
      <p>Upload documents or YouTube links, then take quizzes on extracted concepts.</p>
      {user ? (
        <div className="home-links">
          <Link to="/upload">Upload content</Link>
          <Link to="/documents">View documents</Link>
          <Link to="/quiz">Take quiz</Link>
          <Link to="/dashboard">Dashboard</Link>
        </div>
      ) : (
        <div className="home-links">
          <Link to="/login">Log in</Link>
          <Link to="/signup">Sign up</Link>
        </div>
      )}
    </div>
  );
}
