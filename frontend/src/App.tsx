import React, { useState, useEffect } from 'react';
import './App.css';

interface User {
  id: string;
  email: string;
  name: string;
  credits: number;
  role: string;
}

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/github/login-url');
      const data = await response.json();
      window.location.href = data.login_url;
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (isLoading) {
    return (
      <div className="app">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="app">
        <div className="login-container">
          <h1>🤖 Aieditor</h1>
          <p>AI-Powered Code Editor inspired by OpenHands</p>
          <button onClick={handleLogin} className="login-btn">
            Login with GitHub
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 Aieditor</h1>
        <div className="user-info">
          <span>Welcome, {user.name}</span>
          <span className="credits">Credits: ${user.credits}</span>
          {user.role === 'admin' && <span className="admin-badge">Admin</span>}
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>
      
      <main className="main-content">
        <div className="chat-container">
          <h2>🚀 Welcome to Aieditor!</h2>
          <p>Your AI-powered development assistant is ready.</p>
          
          <div className="features">
            <div className="feature">
              <h3>🔐 Authentication System</h3>
              <p>✅ GitHub OAuth integration</p>
              <p>✅ JWT-based authentication</p>
              <p>✅ User management with roles</p>
            </div>
            
            <div className="feature">
              <h3>💰 Credit System</h3>
              <p>✅ $10 initial balance per user</p>
              <p>✅ Credit transaction tracking</p>
              <p>✅ Admin credit management</p>
            </div>
            
            <div className="feature">
              <h3>🤖 AI Agents</h3>
              <p>✅ OpenAI GPT-4 integration</p>
              <p>✅ Anthropic Claude integration</p>
              <p>✅ DeepSeek integration</p>
            </div>
            
            <div className="feature">
              <h3>⚡ Real-time Communication</h3>
              <p>✅ WebSocket support</p>
              <p>✅ Session management</p>
              <p>✅ Message persistence</p>
            </div>
          </div>
          
          {user.role === 'admin' && (
            <div className="admin-section">
              <h3>👑 Admin Panel</h3>
              <p>You have admin access to manage users and system settings.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;