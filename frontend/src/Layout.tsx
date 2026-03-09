import { Outlet, Link } from "react-router-dom";

export default function Layout() {
  return (
    <div className="layout">
      <nav className="nav">
        <Link to="/">Learning AI</Link>
        <Link to="/upload">Upload</Link>
        <Link to="/documents">Documents</Link>
        <Link to="/quiz">Quiz</Link>
        <Link to="/dashboard">Dashboard</Link>
      </nav>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
