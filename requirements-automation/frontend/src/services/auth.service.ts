import api from './api';

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    username: string;
    email: string;
    firstName?: string;
    lastName?: string;
  };
}

export interface User {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
}

// Auth service
const authService = {
  // Login user - supports both object and individual parameters
  login: async (usernameOrCredentials: string | LoginRequest, password?: string): Promise<AuthResponse> => {
    let credentials: LoginRequest;
    
    // Handle both forms of login (object or individual parameters)
    if (typeof usernameOrCredentials === 'string' && password) {
      credentials = {
        username: usernameOrCredentials,
        password: password
      };
    } else if (typeof usernameOrCredentials === 'object') {
      credentials = usernameOrCredentials;
    } else {
      throw new Error('Invalid login parameters');
    }
    
    const response = await api.post<AuthResponse>('/api/auth/login', credentials);
    
    // Store token in localStorage
    if (response && response.token) {
      localStorage.setItem('authToken', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  },
  
  // Register user
  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/auth/register', userData);
    
    // Store token in localStorage
    if (response && response.token) {
      localStorage.setItem('authToken', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  },
  
  // Logout user
  logout: (): void => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  },
  
  // Get current user info
  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  },
  
  // Check if user is logged in
  isAuthenticated: (): boolean => {
    const token = localStorage.getItem('authToken');
    return !!token;
  }
};

export default authService;