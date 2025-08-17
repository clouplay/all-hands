import React, { useState } from 'react';
import {
  Drawer,
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Chip,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  Code as CodeIcon,
  Terminal as TerminalIcon,
  Folder as FolderIcon,
  SmartToy as BotIcon,
  ExpandLess,
  ExpandMore,
  Psychology as PsychologyIcon,
  Storage as StorageIcon,
  Settings as SettingsIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';

import { ApiService } from '../services/api';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  sessionId: string;
}

const SIDEBAR_WIDTH = 280;

const Sidebar: React.FC<SidebarProps> = ({ open, onClose, sessionId }) => {
  const [agentsExpanded, setAgentsExpanded] = useState(true);
  const [providersExpanded, setProvidersExpanded] = useState(false);

  // Agents query
  const { data: agentsData } = useQuery(
    'agents',
    () => ApiService.getAgents(),
    {
      select: (response) => response.data,
    }
  );

  // LLM providers query
  const { data: providersData } = useQuery(
    'llm-providers',
    () => ApiService.getLLMProviders(),
    {
      select: (response) => response.data,
    }
  );

  // Session info query
  const { data: sessionData } = useQuery(
    ['session', sessionId],
    () => ApiService.getSession(sessionId),
    {
      enabled: !!sessionId,
      select: (response) => response.data,
    }
  );

  const getAgentIcon = (agentName: string) => {
    switch (agentName.toLowerCase()) {
      case 'codeagent':
        return <CodeIcon />;
      case 'terminalagent':
        return <TerminalIcon />;
      case 'fileagent':
        return <FolderIcon />;
      default:
        return <BotIcon />;
    }
  };

  const getAgentStatus = (agent: any) => {
    return agent.active ? 'Aktif' : 'Pasif';
  };

  const getAgentStatusColor = (agent: any) => {
    return agent.active ? 'success' : 'default';
  };

  const formatProviderName = (name: string) => {
    switch (name.toLowerCase()) {
      case 'openai':
        return 'OpenAI';
      case 'anthropic':
        return 'Anthropic';
      default:
        return name;
    }
  };

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: SIDEBAR_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: SIDEBAR_WIDTH,
          boxSizing: 'border-box',
          bgcolor: 'background.paper',
          borderRight: 1,
          borderColor: 'divider',
        },
      }}
    >
      <Box sx={{ overflow: 'auto', height: '100%' }}>
        {/* Header */}
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          p={2}
          bgcolor="primary.dark"
        >
          <Box display="flex" alignItems="center" gap={1}>
            <PsychologyIcon color="inherit" />
            <Typography variant="h6" color="inherit">
              Aieditor
            </Typography>
          </Box>
          <IconButton onClick={onClose} color="inherit" size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Session Info */}
        {sessionData && (
          <Box p={2} bgcolor="background.default">
            <Typography variant="subtitle2" gutterBottom>
              Oturum Bilgileri
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              ID: {sessionData.session_id.substring(0, 8)}...
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              Mesaj: {sessionData.message_count}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              Oluşturulma: {new Date(sessionData.created_at).toLocaleString('tr-TR')}
            </Typography>
          </Box>
        )}

        <Divider />

        {/* Agents Section */}
        <List>
          <ListItemButton onClick={() => setAgentsExpanded(!agentsExpanded)}>
            <ListItemIcon>
              <BotIcon />
            </ListItemIcon>
            <ListItemText primary="AI Agents" />
            {agentsExpanded ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>
          
          <Collapse in={agentsExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {agentsData?.agents && Object.entries(agentsData.agents).map(([name, agent]) => (
                <ListItem key={name} sx={{ pl: 4 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {getAgentIcon(name)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body2">
                          {agent.name}
                        </Typography>
                        <Chip
                          size="small"
                          label={getAgentStatus(agent)}
                          color={getAgentStatusColor(agent)}
                          variant="outlined"
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        {agent.description}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Collapse>
        </List>

        <Divider />

        {/* LLM Providers Section */}
        <List>
          <ListItemButton onClick={() => setProvidersExpanded(!providersExpanded)}>
            <ListItemIcon>
              <StorageIcon />
            </ListItemIcon>
            <ListItemText primary="LLM Providers" />
            {providersExpanded ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>
          
          <Collapse in={providersExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {providersData?.providers && Object.entries(providersData.providers).map(([name, provider]) => (
                <ListItem key={name} sx={{ pl: 4 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <PsychologyIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body2">
                          {formatProviderName(name)}
                        </Typography>
                        {provider.is_default && (
                          <Chip
                            size="small"
                            label="Varsayılan"
                            color="primary"
                            variant="outlined"
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        Model: {provider.model}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
              
              {(!providersData?.providers || Object.keys(providersData.providers).length === 0) && (
                <ListItem sx={{ pl: 4 }}>
                  <ListItemText
                    primary={
                      <Typography variant="body2" color="text.secondary">
                        LLM provider yapılandırılmamış
                      </Typography>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        API key'lerini ayarlayın
                      </Typography>
                    }
                  />
                </ListItem>
              )}
            </List>
          </Collapse>
        </List>

        <Divider />

        {/* Quick Actions */}
        <List>
          <Typography variant="subtitle2" sx={{ px: 2, py: 1, color: 'text.secondary' }}>
            Hızlı Eylemler
          </Typography>
          
          <ListItemButton>
            <ListItemIcon>
              <CodeIcon />
            </ListItemIcon>
            <ListItemText primary="Kod Örnekleri" />
          </ListItemButton>
          
          <ListItemButton>
            <ListItemIcon>
              <TerminalIcon />
            </ListItemIcon>
            <ListItemText primary="Terminal Komutları" />
          </ListItemButton>
          
          <ListItemButton>
            <ListItemIcon>
              <FolderIcon />
            </ListItemIcon>
            <ListItemText primary="Dosya Yönetimi" />
          </ListItemButton>
        </List>

        <Divider />

        {/* Settings */}
        <List>
          <ListItemButton>
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText primary="Ayarlar" />
          </ListItemButton>
        </List>
      </Box>
    </Drawer>
  );
};

export default Sidebar;