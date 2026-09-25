import React, { createContext, useContext, useState, useEffect } from 'react';
import type { UserProfile } from '../types/auth';
import { authApi } from '../services/authApi';
import { formatISTDateTime } from '../utils/dateUtils';

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
  refreshProfile: () => Promise<UserProfile | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    try {
      const savedUser = localStorage.getItem('freshmart_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState<string | null>(localStorage.getItem('freshmart_token'));
  const [isLoading, setIsLoading] = useState<boolean>(() => !localStorage.getItem('freshmart_user'));

  const refreshProfile = async (): Promise<UserProfile | null> => {
    const savedToken = localStorage.getItem('freshmart_token');
    if (!savedToken) return null;
    try {
      const profile = await authApi.getMe();
      const enriched = { ...profile, name: profile.full_name };
      setUser(enriched);
      localStorage.setItem('freshmart_user', JSON.stringify(enriched));
      return enriched;
    } catch (err) {
      console.warn('Failed to refresh user profile:', err);
      return null;
    }
  };

  // Initialize and restore authenticated session
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('freshmart_token');
      if (savedToken) {
        try {
          const profile = await authApi.getMe();
          const enriched = { ...profile, name: profile.full_name };
          setUser(enriched);
          localStorage.setItem('freshmart_user', JSON.stringify(enriched));
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
    // Preserve and auto-archive active chat session to user's persistent archive
    try {
      const userKey = user?.username || user?.role;
      if (userKey) {
        // Check active session first
        const activeRaw = localStorage.getItem(`freshmart_active_session_${userKey}`);
        let activeConvId = `conv-${Date.now()}`;
        let activeHist: any[] = [];

        if (activeRaw) {
          try {
            const parsed = JSON.parse(activeRaw);
            activeConvId = parsed.conversationId || activeConvId;
            activeHist = parsed.history || [];
          } catch {}
        }

        if (activeHist.length > 0) {
          const archRaw = localStorage.getItem(`freshmart_session_history_${userKey}`);
          const arch = archRaw ? JSON.parse(archRaw) : [];
          const newArchive = {
            id: activeConvId,
            startedAt: formatISTDateTime(new Date()),
            title: activeHist[activeHist.length - 1]?.question || activeHist[0]?.question || 'Analytics Investigation',
            queriesCount: activeHist.length,
            items: activeHist,
          };
          const updated = [newArchive, ...arch.filter((s: any) => s.id !== activeConvId).slice(0, 29)];
          localStorage.setItem(`freshmart_session_history_${userKey}`, JSON.stringify(updated));
        }
      }
    } catch (e) {
      console.warn('Failed auto-archiving on logout:', e);
    }

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
        refreshProfile,
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
