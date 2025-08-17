import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  Container
} from '@mui/material';
import { GitHub } from '@mui/icons-material';
import { apiClient } from '../services/apiClient';

interface LoginProps {
  onLogin: (user: any, token: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check for GitHub OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const error = urlParams.get('error');

    if (error) {
      setError('GitHub authentication failed');
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
      return;
    }

    if (code) {
      handleGitHubCallback(code);
    }
  }, []);

  const handleGitHubCallback = async (code: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post('/auth/github/callback', { code });
      const { access_token, user } = response.data;

      // Store token
      localStorage.setItem('auth_token', access_token);
      
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
      
      // Call onLogin callback
      onLogin(user, access_token);
    } catch (err: any) {
      console.error('GitHub callback error:', err);
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get('/auth/github/login-url');
      const { login_url } = response.data;
      
      // Redirect to GitHub OAuth
      window.location.href = login_url;
    } catch (err: any) {
      console.error('GitHub login error:', err);
      setError(err.response?.data?.detail || 'Failed to initiate GitHub login');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="sm">
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="100vh"
        >
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Authenticating...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
      >
        <Card sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            <Box textAlign="center" mb={3}>
              <Typography variant="h4" component="h1" gutterBottom>
                🤖 Aieditor
              </Typography>
              <Typography variant="body1" color="text.secondary">
                AI-Powered Code Editor
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<GitHub />}
              onClick={handleGitHubLogin}
              disabled={loading}
              sx={{ py: 1.5 }}
            >
              Sign in with GitHub
            </Button>

            <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ mt: 3 }}>
              Sign in to access AI-powered coding assistance with $10 free credits
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default Login;