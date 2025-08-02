import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          
          const { access } = response.data as { access: string };
          localStorage.setItem('access_token', access);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access}`;
          }
          
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface Todo {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
  due_date?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
  user: User;
}

// Auth API
export const authAPI = {
  register: async (data: { username: string; email: string; password: string; password_confirm: string }) => {
    const response = await api.post('/auth/register/', data);
    return response.data;
  },
  
  login: async (data: { username: string; password: string }) => {
    const response = await api.post('/auth/login/', data);
    return response.data;
  },
  
  getProfile: async () => {
    const response = await api.get('/auth/profile/');
    return response.data;
  },
  
  updateProfile: async (data: Partial<User>) => {
    const response = await api.put('/auth/profile/', data);
    return response.data;
  },
};

// Todos API
export const todosAPI = {
  getTodos: async (): Promise<Todo[]> => {
    const response = await api.get('/todos/');
    return response.data as Todo[];
  },
  
  createTodo: async (data: Omit<Todo, 'id' | 'created_at' | 'updated_at'>): Promise<Todo> => {
    const response = await api.post('/todos/', data);
    return response.data as Todo;
  },
  
  updateTodo: async (id: number, data: Partial<Todo>): Promise<Todo> => {
    const response = await api.put(`/todos/${id}/`, data);
    return response.data as Todo;
  },
  
  deleteTodo: async (id: number): Promise<void> => {
    await api.delete(`/todos/${id}/`);
  },
  
  toggleTodo: async (id: number): Promise<Todo> => {
    const response = await api.patch(`/todos/${id}/toggle/`);
    return response.data as Todo;
  },
};

export default api;
