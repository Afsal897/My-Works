import { createContext, useContext, useCallback, useState } from 'react';
import api from '../../api';
import { AxiosError } from 'axios';

type AuthContextType = {
  isAuthenticated: boolean;
  checkAuth: () => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuth = useCallback(async () => {
    try {
      await api.get('/validate_token');
      setIsAuthenticated(true);
    } catch (error) {
      const axiosError = error as AxiosError;
      if (axiosError.response?.status === 401) {
        throw new Error('Session expired');
      }
      throw new Error('Authentication failed');
    }
  }, []);

  const logout = () => {
    localStorage.clear();
    setIsAuthenticated(false);
    window.location.href = '/';
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, checkAuth, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);