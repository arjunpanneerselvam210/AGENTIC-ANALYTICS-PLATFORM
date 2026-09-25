import React, { createContext, useContext, useState, useEffect } from 'react';
import type { UserProfile } from '../types/auth';
import { authApi } from '../services/authApi';

export const getRoleSlug = (role?: string): string => {
  switch (role?.toUpperCase()) {
    case 'CEO':
      return 'ceo';
    case 'SALES_MANAGER':
      return 'sales';
    case 'HR_MANAGER':
      return 'hr';
    case 'FINANCE_MANAGER':
      return 'finance';
    case 'INVENTORY_MANAGER':
      return 'inventory';
    case 'ERP_MANAGER':
      return 'erp';
    default:
      return 'ceo';
  }
};

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<UserProfile>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('freshmart_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initialize and restore authenticated session
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('freshmart_token');
      if (savedToken) {
        try {
          const profile = await authApi.getMe();
          const enriched = { ...profile, name: profile.full_name };
          setUser(enriched);
          setToken(savedToken);
        } catch (err) {
          console.warn('Session expired or backend unreachable, clearing stored credentials:', err);
          localStorage.removeItem('freshmart_token');
          localStorage.removeItem('freshmart_user');
          setUser(null);
          setToken(null);
        }
      } else {
        setUser(null);
        setToken(null);
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username: string, password: string): Promise<UserProfile> => {
    setIsLoading(true);
    try {
      const res = await authApi.login(username, password);
      localStorage.setItem('freshmart_token', res.access_token);
      setToken(res.access_token);

      const profile = await authApi.getMe();
      const enriched = { ...profile, name: profile.full_name };
      setUser(enriched);
      localStorage.setItem('freshmart_user', JSON.stringify(enriched));
      setIsLoading(false);
      return enriched;
    } catch (err) {
      setIsLoading(false);
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('freshmart_token');
    localStorage.removeItem('freshmart_user');
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
