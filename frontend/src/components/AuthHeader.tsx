import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Tooltip,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import {
  Menu as MenuIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
  Person as PersonIcon,
  AdminPanelSettings as AdminIcon,
  Logout as LogoutIcon,
  AccountBalance as CreditsIcon,
  Psychology as PsychologyIcon
} from '@mui/icons-material';
import LLMProviderSelector from './LLMProviderSelector';

interface AuthHeaderProps {
  selectedProvider: string;
  onProviderChange: (provider: string) => void;
  currentUser?: any;
  onLogout: () => void;
  onAdminPanel: () => void;
}

const AuthHeader: React.FC<AuthHeaderProps> = ({ 
  selectedProvider, 
  onProviderChange, 
  currentUser,
  onLogout,
  onAdminPanel
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleUserMenuClose();
    onLogout();
  };

  const handleAdminPanel = () => {
    handleUserMenuClose();
    onAdminPanel();
  };

  return (
    <AppBar position="static" elevation={1}>
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        
        <PsychologyIcon sx={{ mr: 1 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Aieditor
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <LLMProviderSelector
            selectedProvider={selectedProvider}
            onProviderChange={onProviderChange}
          />

          {currentUser && (
            <Chip
              icon={<CreditsIcon />}
              label={`$${currentUser.credits?.toFixed(2) || '0.00'}`}
              color="secondary"
              variant="outlined"
              size="small"
            />
          )}
          
          <Tooltip title="Settings">
            <IconButton color="inherit">
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Help">
            <IconButton color="inherit">
              <HelpIcon />
            </IconButton>
          </Tooltip>

          {currentUser && (
            <>
              <Tooltip title="User Menu">
                <IconButton
                  color="inherit"
                  onClick={handleUserMenuOpen}
                  sx={{ p: 0.5 }}
                >
                  <Avatar
                    src={currentUser.avatar_url}
                    sx={{ width: 32, height: 32 }}
                  >
                    <PersonIcon />
                  </Avatar>
                </IconButton>
              </Tooltip>

              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleUserMenuClose}
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
                  <ListItemText
                    primary={currentUser.username}
                    secondary={currentUser.email}
                  />
                </MenuItem>
                
                {currentUser.role === 'admin' && (
                  <MenuItem onClick={handleAdminPanel}>
                    <ListItemIcon>
                      <AdminIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Admin Panel" />
                  </MenuItem>
                )}
                
                <MenuItem onClick={handleLogout}>
                  <ListItemIcon>
                    <LogoutIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText primary="Logout" />
                </MenuItem>
              </Menu>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default AuthHeader;