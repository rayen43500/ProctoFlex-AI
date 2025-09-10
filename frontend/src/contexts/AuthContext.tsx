import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

export const API_BASE = 'http://localhost:8000/api/v1';

export function getAuthHeaders(): HeadersInit {
  try {
    const token = localStorage.getItem('pf_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
}

export type AuthUser = {
  id?: number;
  username?: string;
  email?: string;
  full_name?: string;
  role?: string;
};

export type AuthContextType = {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: AuthUser | null;
  token: string | null;
  login: (emailOrUsername: string, password: string) => Promise<boolean>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);

  // Bootstrap from storage
  useEffect(() => {
    try {
      const storedToken = localStorage.getItem('pf_token');
      const storedUser = localStorage.getItem('pf_user');
      if (storedToken) setToken(storedToken);
      if (storedUser) setUser(JSON.parse(storedUser));
    } catch {}
    setIsLoading(false);
  }, []);

  const login = async (emailOrUsername: string, password: string) => {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: emailOrUsername, password }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      const accessToken: string | undefined = data?.access_token;
      const backendUser: AuthUser | undefined = data?.user;
      if (!accessToken) return false;

      localStorage.setItem('pf_token', accessToken);
      setToken(accessToken);
      if (backendUser) {
        localStorage.setItem('pf_user', JSON.stringify(backendUser));
        setUser(backendUser);
      } else {
        // Fallback for simplified backend responses
        const inferred: AuthUser = {
          username: emailOrUsername,
          email: emailOrUsername.includes('@') ? emailOrUsername : undefined,
        };
        localStorage.setItem('pf_user', JSON.stringify(inferred));
        setUser(inferred);
      }
      return true;
    } catch {
      return false;
    }
  };

  const logout = () => {
    try {
      localStorage.removeItem('pf_token');
      localStorage.removeItem('pf_user');
    } catch {}
    setToken(null);
    setUser(null);
  };

  const value = useMemo<AuthContextType>(() => ({
    isAuthenticated: !!token,
    isLoading,
    user,
    token,
    login,
    logout,
  }), [isLoading, token, user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export { AuthContext };
