'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { User, AuthResponse } from './types';
import { api } from './api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, firstName?: string, lastName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const refreshUser = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }
      const userData = await api.get<User>('/api/auth/me/');
      setUser(userData);
      localStorage.setItem('user_data', JSON.stringify(userData));
    } catch {
      setUser(null);
      api.clearTokens();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const data = await api.post<AuthResponse>('/api/auth/login/', { username, password });
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user_data', JSON.stringify(data.user));
      setUser(data.user);
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const register = async (
    username: string,
    email: string,
    password: string,
    firstName?: string,
    lastName?: string
  ) => {
    setLoading(true);
    try {
      const data = await api.post<AuthResponse>('/api/auth/register/', {
        username,
        email,
        password,
        first_name: firstName,
        last_name: lastName,
      });
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user_data', JSON.stringify(data.user));
      setUser(data.user);
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    const refresh = localStorage.getItem('refresh_token');
    try {
      if (refresh) {
        await api.post('/api/auth/logout/', { refresh });
      }
    } catch {
      // Ignore logout backend errors
    } finally {
      api.clearTokens();
      setUser(null);
      router.push('/login');
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
