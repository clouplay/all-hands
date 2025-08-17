import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, Alert, Snackbar } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';

import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { ApiService } from './services/api';
import { v4 as uuidv4 } from 'uuid';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
  typography: {
    fontFamily: '"Roboto Mono", "Courier New", monospace',
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      setIsLoading(true);
      
      // Health check
      const healthResponse = await ApiService.healthCheck();
      if (healthResponse.error) {
        throw new Error('Backend bağlantısı kurulamadı');
      }

      // Create session
      const sessionResponse = await ApiService.createSession();
      if (sessionResponse.error || !sessionResponse.data) {
        throw new Error('Oturum oluşturulamadı');
      }

      setSessionId(sessionResponse.data.session_id);
      setError('');
    } catch (err: any) {
      console.error('Initialization error:', err);
      setError(err.message || 'Uygulama başlatılırken hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseError = () => {
    setError('');
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          bgcolor="background.default"
        >
          <div>Aieditor yükleniyor...</div>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box display="flex" height="100vh" bgcolor="background.default">
          {/* Sidebar */}
          <Sidebar 
            open={sidebarOpen} 
            onClose={() => setSidebarOpen(false)}
            sessionId={sessionId}
          />

          {/* Main Content */}
          <Box flex={1} display="flex" flexDirection="column">
            {/* Header */}
            <Header 
              onMenuClick={toggleSidebar}
              sessionId={sessionId}
            />

            {/* Chat Interface */}
            <Box flex={1} overflow="hidden">
              {sessionId && (
                <ChatInterface sessionId={sessionId} />
              )}
            </Box>
          </Box>

          {/* Error Snackbar */}
          <Snackbar
            open={!!error}
            autoHideDuration={6000}
            onClose={handleCloseError}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          >
            <Alert 
              onClose={handleCloseError} 
              severity="error" 
              sx={{ width: '100%' }}
            >
              {error}
            </Alert>
          </Snackbar>
        </Box>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;