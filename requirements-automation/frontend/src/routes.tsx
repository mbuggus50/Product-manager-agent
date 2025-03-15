import React, { ReactNode } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';

// Import pages
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import NewRequirement from './pages/NewRequirement';
import RequirementDetail from './pages/RequirementDetail';
import Signup from './pages/Signup';
import RequirementHistory from './pages/RequirementHistory';
import RequirementStatus from './pages/RequirementStatus';

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
      <Route path='/' element={<Home />} />
      <Route path='/login' element={<Login />} />
      <Route path='/signup' element={<Signup />} />
      <Route path='/dashboard' element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path='/new' element={<ProtectedRoute><NewRequirement /></ProtectedRoute>} />
      <Route path='/requirements' element={<ProtectedRoute><RequirementHistory /></ProtectedRoute>} />
      <Route path='/requirements/:id' element={<ProtectedRoute><RequirementDetail /></ProtectedRoute>} />
      <Route path='/requirements/:id/status' element={<ProtectedRoute><RequirementStatus /></ProtectedRoute>} />
    </Routes>
  );
};

export default AppRoutes;
