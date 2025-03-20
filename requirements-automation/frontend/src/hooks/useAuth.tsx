import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  username: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  login: async () => {},
  logout: () => {},
  error: null,
});

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Check for existing authentication on load
  useEffect(() => {
    const storedUser = localStorage.getItem('auth_user');
    const storedAuth = localStorage.getItem('is_authenticated');
    
    if (storedUser && storedAuth === 'true') {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (err) {
        console.error('Error parsing stored user:', err);
        // Clear invalid data
        localStorage.removeItem('auth_user');
        localStorage.removeItem('is_authenticated');
      }
    }
  }, []);

  const login = async (username: string, password: string) => {
    try {
      // For demo purposes, we'll accept any login
      // In a real implementation, this would call an API endpoint
      console.log(`Attempting to log in with username: ${username}`);
      
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Set user and authenticated state
      setUser({ username });
      setIsAuthenticated(true);
      setError(null);
      
      // Store in localStorage for persistent login
      localStorage.setItem('auth_user', JSON.stringify({ username }));
      localStorage.setItem('is_authenticated', 'true');
      
    } catch (err) {
      console.error('Login error:', err);
      setError('Authentication failed. Please check your credentials.');
      throw err;
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
    
    // Clear localStorage items
    localStorage.removeItem('auth_user');
    localStorage.removeItem('is_authenticated');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  return useContext(AuthContext);
}
