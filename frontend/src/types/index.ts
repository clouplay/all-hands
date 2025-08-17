export interface Message {
  type: 'user' | 'assistant' | 'system' | 'error' | 'action' | 'result';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
  agent_name?: string;
  session_id?: string;
}

export interface Session {
  session_id: string;
  user_id?: string;
  created_at: string;
  last_activity: string;
  message_count: number;
  workspace_path?: string;
}

export interface Agent {
  name: string;
  description: string;
  active: boolean;
  last_used?: string;
}

export interface LLMProvider {
  model: string;
  type: string;
  is_default: boolean;
}

export interface WebSocketMessage {
  type: 'connection_established' | 'message' | 'message_received' | 'typing' | 'typing_stop' | 'error' | 'message_history' | 'pong';
  message?: Message;
  messages?: Message[];
  session_id?: string;
  timestamp?: string;
  error?: string;
  agent?: string;
  total_count?: number;
}

export interface FileInfo {
  name: string;
  type: 'file' | 'directory';
  size: number;
  path: string;
}

export interface CodeBlock {
  language: string;
  code: string;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}