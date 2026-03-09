import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getMe, login as apiLogin, signup as apiSignup, setToken, removeToken } from "./api";
import type { UserItem } from "./api";

type AuthContextValue = {
  user: UserItem | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserItem | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem("learning_ai_token");
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const u = await getMe();
      setUser(u);
    } catch {
      removeToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const { access_token } = await apiLogin(email, password);
      setToken(access_token);
      const u = await getMe();
      setUser(u);
    },
    []
  );

  const signup = useCallback(
    async (email: string, password: string, fullName?: string) => {
      const { access_token } = await apiSignup(email, password, fullName);
      setToken(access_token);
      const u = await getMe();
      setUser(u);
    },
    []
  );

  const logout = useCallback(() => {
    removeToken();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
