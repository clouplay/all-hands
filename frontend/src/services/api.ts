import axios from 'axios';
import { Session, Message, Agent, LLMProvider, ApiResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:12000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class ApiService {
  // Health check
  static async healthCheck(): Promise<ApiResponse> {
    try {
      const response = await api.get('/health');
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  // Session management
  static async createSession(userId?: string): Promise<ApiResponse<{ session_id: string }>> {
    try {
      const response = await api.post('/sessions', { user_id: userId });
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  static async getSession(sessionId: string): Promise<ApiResponse<Session>> {
    try {
      const response = await api.get(`/sessions/${sessionId}`);
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  static async getSessionMessages(sessionId: string, limit: number = 50): Promise<ApiResponse<{ messages: Message[]; total_count: number }>> {
    try {
      const response = await api.get(`/sessions/${sessionId}/messages`, {
        params: { limit }
      });
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  static async sendMessage(sessionId: string, content: string, metadata?: Record<string, any>): Promise<ApiResponse<{ message_sent: Message; responses: Message[] }>> {
    try {
      const response = await api.post(`/sessions/${sessionId}/messages`, {
        content,
        metadata
      });
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  static async deleteSession(sessionId: string): Promise<ApiResponse> {
    try {
      const response = await api.delete(`/sessions/${sessionId}`);
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  // Agent management
  static async getAgents(): Promise<ApiResponse<{ agents: Record<string, Agent>; available_agents: string[] }>> {
    try {
      const response = await api.get('/agents');
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  // LLM providers
  static async getLLMProviders(): Promise<ApiResponse<{ providers: Record<string, LLMProvider>; available: string[] }>> {
    try {
      const response = await api.get('/llm/providers');
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  // System stats
  static async getStats(): Promise<ApiResponse<{
    session_count: number;
    active_sessions: number;
    available_agents: number;
    available_llm_providers: number;
    timestamp: string;
  }>> {
    try {
      const response = await api.get('/stats');
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }
}

export default api;