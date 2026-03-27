/**
 * Auth Context - gestioneaza starea de autentificare a aplicatiei.
 * Persistenta cu localStorage, auto-load la mount.
 */
import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import api from '../lib/api';

interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  nhs_band: string | null;
  specialization: string | null;
  subscription_tier: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

interface RegisterData {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  nhs_band?: string;
  specialization?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = user !== null;

  // Incarca user din localStorage la mount
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    const token = localStorage.getItem('access_token');

    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('user');
      }
    }
    setIsLoading(false);
  }, []);

  const saveTokens = (data: { access_token: string; refresh_token: string }) => {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
  };

  const clearAuth = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const res = await api.get('/api/auth/me');
      const userData = res.data;
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch {
      clearAuth();
    }
  }, [clearAuth]);

  const login = async (email: string, password: string) => {
    const res = await api.post('/api/auth/login', { email, password });
    saveTokens(res.data);

    // Fetch profil complet
    const meRes = await api.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${res.data.access_token}` },
    });
    const userData = meRes.data;
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const register = async (data: RegisterData) => {
    const res = await api.post('/api/auth/register', data);
    saveTokens(res.data);

    const meRes = await api.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${res.data.access_token}` },
    });
    const userData = meRes.data;
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    // Fire-and-forget logout API call
    api.post('/api/auth/logout').catch(() => {});
    clearAuth();
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, isAuthenticated, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
