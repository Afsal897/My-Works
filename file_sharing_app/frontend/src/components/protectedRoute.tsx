import { useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import api from '../api';

const ProtectedRoute = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

    const checkAuth = async () => {
      try {
        await api.get('/validate_token');
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
        console.log('error here')
      }
    };

    checkAuth();

  if (isAuthenticated === null) {
    return <div>Loading...</div>; // or a spinner
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/" />;
};

export default ProtectedRoute;
