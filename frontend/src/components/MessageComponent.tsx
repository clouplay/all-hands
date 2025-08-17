import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Code as CodeIcon,
  Terminal as TerminalIcon,
  Folder as FolderIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { Message } from '../types';

interface MessageComponentProps {
  message: Message;
  icon: React.ReactNode;
  color: string;
}

const MessageComponent: React.FC<MessageComponentProps> = ({ message, icon, color }) => {
  const isUser = message.type === 'user';
  const isError = message.type === 'error';
  const isAction = message.type === 'action';
  const isResult = message.type === 'result';

  const handleCopyContent = () => {
    navigator.clipboard.writeText(message.content);
  };

  const getActionIcon = () => {
    const action = message.metadata?.action;
    switch (action) {
      case 'code_generation':
      case 'code_analysis':
        return <CodeIcon fontSize="small" />;
      case 'command_execution':
        return <TerminalIcon fontSize="small" />;
      case 'file_read':
      case 'file_write':
      case 'file_list':
        return <FolderIcon fontSize="small" />;
      default:
        return null;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('tr-TR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const renderCodeBlock = ({ node, inline, className, children, ...props }: any) => {
    const match = /language-(\w+)/.exec(className || '');
    const language = match ? match[1] : '';

    if (!inline && language) {
      return (
        <Box position="relative" mb={2}>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            bgcolor="rgba(255,255,255,0.05)"
            px={2}
            py={1}
            borderRadius="4px 4px 0 0"
          >
            <Typography variant="caption" color="text.secondary">
              {language}
            </Typography>
            <IconButton
              size="small"
              onClick={() => navigator.clipboard.writeText(String(children))}
            >
              <CopyIcon fontSize="small" />
            </IconButton>
          </Box>
          <SyntaxHighlighter
            style={vscDarkPlus}
            language={language}
            PreTag="div"
            customStyle={{
              margin: 0,
              borderRadius: '0 0 4px 4px',
              fontSize: '14px',
            }}
            {...props}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
        </Box>
      );
    }

    return (
      <code
        className={className}
        style={{
          backgroundColor: 'rgba(255,255,255,0.1)',
          padding: '2px 4px',
          borderRadius: '3px',
          fontSize: '0.9em',
        }}
        {...props}
      >
        {children}
      </code>
    );
  };

  return (
    <Box
      display="flex"
      gap={2}
      mb={3}
      justifyContent={isUser ? 'flex-end' : 'flex-start'}
    >
      {!isUser && (
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            bgcolor: color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          {icon}
        </Box>
      )}

      <Paper
        elevation={1}
        sx={{
          maxWidth: '70%',
          minWidth: '200px',
          bgcolor: isUser ? 'primary.dark' : 'background.paper',
          border: isError ? '1px solid' : 'none',
          borderColor: isError ? 'error.main' : 'transparent',
        }}
      >
        {/* Message Header */}
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          px={2}
          py={1}
          bgcolor={isUser ? 'primary.main' : 'rgba(255,255,255,0.05)'}
        >
          <Box display="flex" alignItems="center" gap={1}>
            {(isAction || isResult) && getActionIcon()}
            <Typography variant="caption" fontWeight="bold">
              {isUser ? 'Siz' : message.agent_name || 'AI Asistan'}
            </Typography>
            {message.metadata?.action && (
              <Chip
                size="small"
                label={message.metadata.action}
                variant="outlined"
                sx={{ height: 20, fontSize: '0.7rem' }}
              />
            )}
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="caption" color="text.secondary">
              {formatTimestamp(message.timestamp)}
            </Typography>
            <Tooltip title="Kopyala">
              <IconButton size="small" onClick={handleCopyContent}>
                <CopyIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Message Content */}
        <Box px={2} py={2}>
          {isUser ? (
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {message.content}
            </Typography>
          ) : (
            <ReactMarkdown
              components={{
                code: renderCodeBlock,
                p: ({ children }) => (
                  <Typography variant="body1" paragraph>
                    {children}
                  </Typography>
                ),
                h1: ({ children }) => (
                  <Typography variant="h5" gutterBottom>
                    {children}
                  </Typography>
                ),
                h2: ({ children }) => (
                  <Typography variant="h6" gutterBottom>
                    {children}
                  </Typography>
                ),
                h3: ({ children }) => (
                  <Typography variant="subtitle1" gutterBottom>
                    {children}
                  </Typography>
                ),
                ul: ({ children }) => (
                  <Box component="ul" sx={{ pl: 2, mb: 2 }}>
                    {children}
                  </Box>
                ),
                ol: ({ children }) => (
                  <Box component="ol" sx={{ pl: 2, mb: 2 }}>
                    {children}
                  </Box>
                ),
                li: ({ children }) => (
                  <Typography component="li" variant="body1">
                    {children}
                  </Typography>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </Box>

        {/* Message Metadata */}
        {message.metadata && Object.keys(message.metadata).length > 0 && (
          <Box px={2} pb={2}>
            <Typography variant="caption" color="text.secondary">
              {message.metadata.command && `Komut: ${message.metadata.command}`}
              {message.metadata.file_path && `Dosya: ${message.metadata.file_path}`}
              {message.metadata.exit_code !== undefined && ` (Çıkış kodu: ${message.metadata.exit_code})`}
            </Typography>
          </Box>
        )}
      </Paper>

      {isUser && (
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            bgcolor: color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          {icon}
        </Box>
      )}
    </Box>
  );
};

export default MessageComponent;