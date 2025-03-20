import axios, { AxiosResponse, AxiosRequestConfig } from 'axios';

// Base API configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5555';

// Create an axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false, // Change to true if your API uses cookies for auth
});

// Request interceptor for handling auth
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('authToken');
    
    // If token exists, add to headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Handle 401 (Unauthorized)
    if (error.response && error.response.status === 401) {
      // Clear token if it's expired or invalid
      localStorage.removeItem('authToken');
      // Redirect to login page if needed
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// Generic request function
const request = async <T>(config: AxiosRequestConfig): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await api(config);
    return response.data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Utility functions for common methods
const httpClient = {
  get: <T>(url: string, params?: any) => request<T>({ method: 'get', url, params }),
  post: <T>(url: string, data?: any) => request<T>({ method: 'post', url, data }),
  put: <T>(url: string, data?: any) => request<T>({ method: 'put', url, data }),
  delete: <T>(url: string) => request<T>({ method: 'delete', url }),
};

export default httpClient;