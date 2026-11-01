import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import type {
  AuthContextType,
  LoginPayload,
  RegisterPayload,
  User,
} from '../types';
import { AuthContext } from './authContextDef';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshUser = useCallback(async (): Promise<User | null> => {
    try {
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
      return currentUser;
    } catch {
      setUser(null);
      return null;
    }
  }, []);

  // Restore authenticated session on initial app mount
  useEffect(() => {
    let mounted = true;

    async function checkAuthSession() {
      try {
        const currentUser = await api.getCurrentUser();
        if (mounted) {
          setUser(currentUser);
        }
      } catch {
        if (mounted) {
          setUser(null);
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    }

    checkAuthSession();

    return () => {
      mounted = false;
    };
  }, []);

  const login = useCallback(async (payload: LoginPayload): Promise<User> => {
    const authenticatedUser = await api.login(payload);
    setUser(authenticatedUser);
    return authenticatedUser;
  }, []);

  const register = useCallback(async (payload: RegisterPayload): Promise<User> => {
    const registeredUser = await api.register(payload);
    setUser(registeredUser);
    return registeredUser;
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    try {
      await api.logout();
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo<AuthContextType>(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, register, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
