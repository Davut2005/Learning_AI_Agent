import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./ThemeContext";
import { AuthProvider } from "./AuthContext";
import Layout from "./Layout";
import ProtectedRoute from "./ProtectedRoute";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import CreatePathPage from "./pages/CreatePathPage";
import PathsListPage from "./pages/PathsListPage";
import PathDetailPage from "./pages/PathDetailPage";
import QuizPage from "./pages/QuizPage";
import DashboardPage from "./pages/DashboardPage";
import "./App.css";

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="login" element={<LoginPage />} />
              <Route path="signup" element={<SignupPage />} />
              <Route
                path="paths"
                element={
                  <ProtectedRoute>
                    <PathsListPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="paths/new"
                element={
                  <ProtectedRoute>
                    <CreatePathPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="paths/:id"
                element={
                  <ProtectedRoute>
                    <PathDetailPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="quiz"
                element={
                  <ProtectedRoute>
                    <QuizPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              {/* Legacy redirects */}
              <Route path="upload" element={<Navigate to="/paths/new" replace />} />
              <Route path="documents" element={<Navigate to="/paths" replace />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
