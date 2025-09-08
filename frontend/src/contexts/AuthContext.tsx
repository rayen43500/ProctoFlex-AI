import React, { createContext, useContext } from 'react';

export const API_BASE = 'http://localhost:8000/api/v1';

export function getAuthHeaders(): HeadersInit {
  try {
    const token = localStorage.getItem('pf_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
}

export const AuthContext = createContext({});
export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <AuthContext.Provider value={{}}>{children}</AuthContext.Provider>;
};
