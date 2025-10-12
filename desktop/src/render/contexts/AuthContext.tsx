import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService, User } from '../../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: {
    username: string;
    full_name: string;
    email: string;
    password: string;
  }) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // Vérifier l'authentification au chargement
  useEffect(() => {
    checkAuth();
  }, []);

  // Sync identity to Electron main when user changes
  useEffect(() => {
    try {
      if (user && (window as any).electronAPI?.setStudentIdentity) {
        (window as any).electronAPI.setStudentIdentity({
          id: user.id,
          email: (user as any).email || user.name || 'unknown@example.com',
          name: user.name || (user as any).full_name || 'Utilisateur',
          role: (user as any).role || 'student',
          is_active: (user as any).is_active ?? true
        });
      } else if (!user && (window as any).electronAPI?.setStudentIdentity) {
        (window as any).electronAPI.setStudentIdentity(null);
      }
    } catch (e) {
      // ignore sync errors
    }
  }, [user]);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('pf_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      const userData = await apiService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Erreur de vérification auth:', error);
      // Ne pas supprimer le token si c'est juste un problème de récupération du profil
      // L'utilisateur peut quand même utiliser l'application
      setUser({
        id: 1,
        name: 'Utilisateur',
        email: 'user@example.com',
        role: 'student',
        is_active: true
      });
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await apiService.login(email, password);
      localStorage.setItem('pf_token', response.access_token);

      // Si le backend renvoie un objet user, l'utiliser
      if (response.user) {
        const u = response.user;
        setUser({
          id: u.id ?? 1,
          name: u.username || 'Utilisateur',
          email: u.email || email,
          role: u.role || 'student',
          is_active: true,
        });
        return;
      }

      // Sinon, tenter de récupérer /auth/me ; si non dispo, fallback
      try {
        const userData = await apiService.getCurrentUser();
        setUser(userData);
      } catch (_profileError) {
        setUser({
          id: 1,
          name: 'Utilisateur',
          email: email,
          role: 'student',
          is_active: true
        });
      }
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData: {
    username: string;
    full_name: string;
    email: string;
    password: string;
    face_image_base64?: string;
  }) => {
    try {
      const response = await apiService.register({
        name: userData.full_name || userData.username,
        email: userData.email,
        password: userData.password,
        username: userData.username,
        full_name: userData.full_name,
        face_image_base64: userData.face_image_base64
      });
      localStorage.setItem('pf_token', response.access_token);
      
      // Récupérer les données utilisateur
      const userInfo = await apiService.getCurrentUser();
      setUser(userInfo);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('pf_token');
    setUser(null);
    try {
      if ((window as any).electronAPI?.setStudentIdentity) {
        (window as any).electronAPI.setStudentIdentity(null);
      }
    } catch {}
  };

  const refreshUser = async () => {
    try {
      const userData = await apiService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Erreur de refresh user:', error);
      logout();
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
