import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Chip,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';

import { apiClient } from '../services/api';
import LLMProviderSelector from './LLMProviderSelector';

interface HeaderProps {
  onMenuClick: () => void;
  sessionId: string;
  selectedProvider?: string;
  onProviderChange?: (provider: string) => void;
}

const Header: React.FC<HeaderProps> = ({ 
  onMenuClick, 
  sessionId, 
  selectedProvider = '',
  onProviderChange = () => {}
}) => {
  const [settingsAnchor, setSettingsAnchor] = useState<null | HTMLElement>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiClient.get('/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleSettingsClick = (event: React.MouseEvent<HTMLElement>) => {
    setSettingsAnchor(event.currentTarget);
  };

  const handleSettingsClose = () => {
    setSettingsAnchor(null);
  };



  return (
    <AppBar position="static" elevation={0} sx={{ bgcolor: 'background.paper' }}>
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <PsychologyIcon sx={{ mr: 1 }} color="primary" />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Aieditor
        </Typography>

        {/* LLM Provider Selector */}
        <Box display="flex" alignItems="center" gap={2} mr={2}>
          <LLMProviderSelector
            selectedProvider={selectedProvider}
            onProviderChange={onProviderChange}
          />
          
          {/* System Status */}
          {stats && (
            <Box display="flex" alignItems="center" gap={1}>
              <Chip
                size="small"
                label={`${stats.active_sessions} aktif oturum`}
                variant="outlined"
                color="primary"
              />
              <Chip
                size="small"
                label={`${stats.available_agents} agent`}
                variant="outlined"
                color="secondary"
              />
            </Box>
          )}
        </Box>

        {/* Settings Menu */}
        <IconButton
          color="inherit"
          onClick={handleSettingsClick}
          aria-label="settings"
        >
          <SettingsIcon />
        </IconButton>

        <Menu
          anchorEl={settingsAnchor}
          open={Boolean(settingsAnchor)}
          onClose={handleSettingsClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem disabled>
            <Box>
              <Typography variant="subtitle2">Oturum ID</Typography>
              <Typography variant="caption" color="text.secondary">
                {sessionId.substring(0, 8)}...
              </Typography>
            </Box>
          </MenuItem>
          
          <MenuItem disabled>
            <Box>
              <Typography variant="subtitle2">Seçili Provider</Typography>
              <Typography variant="caption" color="text.secondary">
                {selectedProvider || 'Yok'}
              </Typography>
            </Box>
          </MenuItem>

          <Divider />

          <MenuItem onClick={handleSettingsClose}>
            <InfoIcon sx={{ mr: 1 }} />
            Hakkında
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;