import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Chip,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

import { Message, WebSocketMessage } from '../types';
import WebSocketService from '../services/websocket';
import MessageComponent from './MessageComponent';

interface ChatInterfaceProps {
  sessionId: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingAgent, setTypingAgent] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [wsService, setWsService] = useState<WebSocketService | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!sessionId) return;

    const ws = new WebSocketService(sessionId);
    setWsService(ws);

    // WebSocket event handlers
    ws.onMessage('connection_established', (data: WebSocketMessage) => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
      
      // Welcome message
      if (data.message) {
        const welcomeMessage: Message = {
          type: 'assistant',
          content: data.message || 'Aieditor\'a hoş geldiniz!',
          timestamp: new Date().toISOString(),
          agent_name: 'System'
        };
        setMessages([welcomeMessage]);
      }

      // Request message history
      ws.requestMessageHistory();
    });

    ws.onMessage('message', (data: WebSocketMessage) => {
      if (data.message) {
        setMessages(prev => [...prev, data.message!]);
      }
    });

    ws.onMessage('message_received', (data: WebSocketMessage) => {
      if (data.message) {
        setMessages(prev => [...prev, data.message!]);
      }
    });

    ws.onMessage('message_history', (data: WebSocketMessage) => {
      if (data.messages) {
        setMessages(data.messages);
      }
    });

    ws.onMessage('typing', (data: WebSocketMessage) => {
      setIsTyping(true);
      setTypingAgent(data.agent || 'AI');
    });

    ws.onMessage('typing_stop', () => {
      setIsTyping(false);
      setTypingAgent('');
    });

    ws.onMessage('error', (data: WebSocketMessage) => {
      console.error('WebSocket error:', data.error);
      const errorMessage: Message = {
        type: 'error',
        content: data.error || 'Bilinmeyen hata',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    });

    // Connect
    ws.connect().catch(console.error);

    return () => {
      ws.disconnect();
    };
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = () => {
    if (!inputValue.trim() || !wsService || !isConnected) return;

    const userMessage: Message = {
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    // Send via WebSocket
    wsService.sendMessage(inputValue.trim());
    
    setInputValue('');
    inputRef.current?.focus();
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'user':
        return <PersonIcon />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <BotIcon color="primary" />;
    }
  };

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'user':
        return 'primary.main';
      case 'error':
        return 'error.main';
      case 'system':
        return 'warning.main';
      default:
        return 'secondary.main';
    }
  };

  return (
    <Box display="flex" flexDirection="column" height="100%">
      {/* Connection Status */}
      <Box p={1} bgcolor="background.paper">
        <Chip
          size="small"
          label={isConnected ? 'Bağlı' : 'Bağlantı kuruluyor...'}
          color={isConnected ? 'success' : 'warning'}
          variant="outlined"
        />
      </Box>

      <Divider />

      {/* Messages Area */}
      <Box
        flex={1}
        overflow="auto"
        p={2}
        sx={{
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'rgba(255,255,255,0.1)',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'rgba(255,255,255,0.3)',
            borderRadius: '4px',
          },
        }}
      >
        {messages.map((message, index) => (
          <MessageComponent
            key={index}
            message={message}
            icon={getMessageIcon(message.type)}
            color={getMessageColor(message.type)}
          />
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <Box display="flex" alignItems="center" gap={2} mt={2}>
            <BotIcon color="primary" />
            <Box display="flex" alignItems="center" gap={1}>
              <CircularProgress size={16} />
              <Typography variant="body2" color="text.secondary">
                {typingAgent} yazıyor...
              </Typography>
            </Box>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      <Divider />

      {/* Input Area */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          bgcolor: 'background.paper',
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Box display="flex" gap={1} alignItems="flex-end">
          <TextField
            ref={inputRef}
            fullWidth
            multiline
            maxRows={4}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Mesajınızı yazın... (Enter ile gönder)"
            variant="outlined"
            size="small"
            disabled={!isConnected}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'background.default',
              },
            }}
          />
          <IconButton
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || !isConnected}
            color="primary"
            size="large"
          >
            <SendIcon />
          </IconButton>
        </Box>

        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          AI asistanınız kod yazma, dosya yönetimi ve terminal komutları konularında yardımcı olabilir.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ChatInterface;