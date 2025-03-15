import React, { ReactNode } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to='/login' replace />;
  }
  
  return <>{children}</>;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path='/' element={<div>Home Page</div>} />
      <Route path='/login' element={<div>Login Page</div>} />
      <Route path='/dashboard' element={<ProtectedRoute><div>Dashboard</div></ProtectedRoute>} />
    </Routes>
  );
};

export default AppRoutes;
