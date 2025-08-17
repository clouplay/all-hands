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
import { useQuery } from 'react-query';

import { ApiService } from '../services/api';

interface HeaderProps {
  onMenuClick: () => void;
  sessionId: string;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick, sessionId }) => {
  const [settingsAnchor, setSettingsAnchor] = useState<null | HTMLElement>(null);

  // System stats query
  const { data: stats } = useQuery(
    'system-stats',
    () => ApiService.getStats(),
    {
      refetchInterval: 30000, // 30 seconds
      select: (response) => response.data,
    }
  );

  // LLM providers query
  const { data: llmProviders } = useQuery(
    'llm-providers',
    () => ApiService.getLLMProviders(),
    {
      select: (response) => response.data,
    }
  );

  const handleSettingsClick = (event: React.MouseEvent<HTMLElement>) => {
    setSettingsAnchor(event.currentTarget);
  };

  const handleSettingsClose = () => {
    setSettingsAnchor(null);
  };

  const getDefaultProvider = () => {
    if (!llmProviders?.providers) return 'Yok';
    
    const defaultProvider = Object.entries(llmProviders.providers).find(
      ([_, provider]) => provider.is_default
    );
    
    return defaultProvider ? `${defaultProvider[0]} (${defaultProvider[1].model})` : 'Yok';
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

        {/* System Status */}
        <Box display="flex" alignItems="center" gap={1} mr={2}>
          {stats && (
            <>
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
            </>
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
              <Typography variant="subtitle2">LLM Provider</Typography>
              <Typography variant="caption" color="text.secondary">
                {getDefaultProvider()}
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