import React, { useState, useEffect } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import theme from './theme';
import AuthHeader from './components/AuthHeader';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import Login from './components/Login';
import AdminPanel from './components/AdminPanel';
import { apiClient } from './services/apiClient';

type ViewMode = 'chat' | 'admin';

function AuthApp() {
  const [sessionId, setSessionId] = useState<string>('');
  const [selectedProvider, setSelectedProvider] = useState<string>('openai');
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [viewMode, setViewMode] = useState<ViewMode>('chat');

  useEffect(() => {
    // Check for existing authentication
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          // Set authorization header
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Verify token and get user info
          const response = await apiClient.get('/auth/me');
          setCurrentUser(response.data.user);
          setIsAuthenticated(true);
          
          // Create session after authentication
          await createSession();
        } catch (error) {
          console.error('Token verification failed:', error);
          localStorage.removeItem('auth_token');
          delete apiClient.defaults.headers.common['Authorization'];
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const createSession = async () => {
    try {
      const response = await apiClient.post('/sessions');
      setSessionId(response.data.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleLogin = (user: any, token: string) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
    
    // Set authorization header
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    // Create session after login
    createSession();
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    delete apiClient.defaults.headers.common['Authorization'];
    setCurrentUser(null);
    setIsAuthenticated(false);
    setSessionId('');
    setViewMode('chat');
  };

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider);
  };

  const handleAdminPanel = () => {
    setViewMode('admin');
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box 
          display="flex" 
          justifyContent="center" 
          alignItems="center" 
          height="100vh"
        >
          Loading...
        </Box>
      </ThemeProvider>
    );
  }

  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login onLogin={handleLogin} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh' }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
          <AuthHeader 
            selectedProvider={selectedProvider}
            onProviderChange={handleProviderChange}
            currentUser={currentUser}
            onLogout={handleLogout}
            onAdminPanel={handleAdminPanel}
          />
          <Box sx={{ display: 'flex', flex: 1 }}>
            {viewMode === 'chat' && (
              <Sidebar 
                open={true}
                onClose={() => {}}
                sessionId={sessionId}
              />
            )}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
              {viewMode === 'chat' && sessionId && (
                <ChatInterface 
                  sessionId={sessionId} 
                  selectedProvider={selectedProvider}
                />
              )}
              {viewMode === 'admin' && (
                <AdminPanel currentUser={currentUser} />
              )}
            </Box>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default AuthApp;