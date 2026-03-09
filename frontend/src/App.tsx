import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./ThemeContext";
import { AuthProvider } from "./AuthContext";
import Layout from "./Layout";
import ProtectedRoute from "./ProtectedRoute";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import UploadPage from "./pages/UploadPage";
import DocumentListPage from "./pages/DocumentListPage";
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
                path="upload"
                element={
                  <ProtectedRoute>
                    <UploadPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="documents"
                element={
                  <ProtectedRoute>
                    <DocumentListPage />
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
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
