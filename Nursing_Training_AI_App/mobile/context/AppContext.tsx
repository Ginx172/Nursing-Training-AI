import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import * as SecureStore from 'expo-secure-store';

interface User {
  id: string;
  name: string;
  email: string;
  nmcNumber?: string;
  currentBand: string;
  sector: string;
  specialty: string;
  token?: string;
}

interface UserProgress {
  questionsCompleted: number;
  accuracy: number;
  streak: number;
  progressToNextBand: number;
  strengths: string[];
  weaknesses: string[];
}

interface AppContextType {
  user: User | null;
  userProgress: UserProgress | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
  updateProgress: (progress: Partial<UserProgress>) => void;
  updateUser: (userData: Partial<User>) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider = ({ children }: AppProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProgress, setUserProgress] = useState<UserProgress | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Load user data on app start
  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const userData = await SecureStore.getItemAsync('user');
      const progressData = await SecureStore.getItemAsync('progress');
      
      if (userData) {
        setUser(JSON.parse(userData));
        setIsAuthenticated(true);
      }
      
      if (progressData) {
        setUserProgress(JSON.parse(progressData));
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      
      // TODO: Replace with actual API call
      const response = await fetch('YOUR_API_URL/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      
      if (data.success) {
        const userData = data.user;
        setUser(userData);
        setIsAuthenticated(true);
        
        // Save to secure storage
        await SecureStore.setItemAsync('user', JSON.stringify(userData));
        await SecureStore.setItemAsync('token', data.token);
        
        // Load user progress
        await loadUserProgress(userData.id);
      } else {
        throw new Error('Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: any) => {
    try {
      setIsLoading(true);
      
      // TODO: Replace with actual API call
      const response = await fetch('YOUR_API_URL/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });

      const data = await response.json();
      
      if (data.success) {
        // Auto-login after successful registration
        await login(userData.email, userData.password);
      } else {
        throw new Error('Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      
      // Clear user data
      setUser(null);
      setUserProgress(null);
      setIsAuthenticated(false);
      
      // Clear secure storage
      await SecureStore.deleteItemAsync('user');
      await SecureStore.deleteItemAsync('token');
      await SecureStore.deleteItemAsync('progress');
      
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserProgress = async (userId: string) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`YOUR_API_URL/progress/${userId}`);
      const data = await response.json();
      
      if (data.success) {
        setUserProgress(data.progress);
        await SecureStore.setItemAsync('progress', JSON.stringify(data.progress));
      }
    } catch (error) {
      console.error('Error loading progress:', error);
    }
  };

  const updateProgress = async (progress: Partial<UserProgress>) => {
    try {
      const updatedProgress = { ...userProgress, ...progress } as UserProgress;
      setUserProgress(updatedProgress);
      
      // Save to secure storage
      await SecureStore.setItemAsync('progress', JSON.stringify(updatedProgress));
      
      // TODO: Sync with backend
      if (user?.id) {
        await fetch(`YOUR_API_URL/progress/${user.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedProgress)
        });
      }
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const updateUser = async (userData: Partial<User>) => {
    try {
      const updatedUser = { ...user, ...userData } as User;
      setUser(updatedUser);
      
      // Save to secure storage
      await SecureStore.setItemAsync('user', JSON.stringify(updatedUser));
      
      // TODO: Sync with backend
      if (updatedUser.id) {
        await fetch(`YOUR_API_URL/users/${updatedUser.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedUser)
        });
      }
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const value = {
    user,
    userProgress,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    updateProgress,
    updateUser
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

