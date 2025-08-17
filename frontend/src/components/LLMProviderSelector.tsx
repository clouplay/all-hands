import React, { useState, useEffect } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Chip,
  Typography,
  Tooltip,
  IconButton
} from '@mui/material';
import { Info as InfoIcon, CheckCircle as CheckIcon } from '@mui/icons-material';
import { apiClient } from '../services/api';

interface LLMProvider {
  model: string;
  type: string;
  is_default: boolean;
}

interface LLMProviderSelectorProps {
  selectedProvider: string;
  onProviderChange: (provider: string) => void;
}

const LLMProviderSelector: React.FC<LLMProviderSelectorProps> = ({
  selectedProvider,
  onProviderChange
}) => {
  const [providers, setProviders] = useState<Record<string, LLMProvider>>({});
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await apiClient.get('/llm/providers');
      setProviders(response.data.providers);
      setAvailableProviders(response.data.available);
      
      // Eğer seçili provider yoksa, default olanı seç
      if (!selectedProvider && response.data.available.length > 0) {
        const defaultProvider = Object.keys(response.data.providers).find(
          key => response.data.providers[key].is_default
        ) || response.data.available[0];
        onProviderChange(defaultProvider);
      }
    } catch (error) {
      console.error('Error fetching LLM providers:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProviderDisplayName = (providerKey: string) => {
    const provider = providers[providerKey];
    if (!provider) return providerKey;
    
    const names: Record<string, string> = {
      'openai': 'OpenAI',
      'anthropic': 'Anthropic',
      'deepseek': 'DeepSeek'
    };
    
    return names[providerKey] || providerKey;
  };

  const getProviderIcon = (providerKey: string) => {
    const icons: Record<string, string> = {
      'openai': '🤖',
      'anthropic': '🧠',
      'deepseek': '🔍'
    };
    
    return icons[providerKey] || '🤖';
  };

  if (loading) {
    return (
      <Box sx={{ minWidth: 200 }}>
        <Typography variant="body2" color="text.secondary">
          Loading providers...
        </Typography>
      </Box>
    );
  }

  if (availableProviders.length === 0) {
    return (
      <Box sx={{ minWidth: 200 }}>
        <Typography variant="body2" color="error">
          No LLM providers configured
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ minWidth: 200, display: 'flex', alignItems: 'center', gap: 1 }}>
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel>LLM Provider</InputLabel>
        <Select
          value={selectedProvider}
          label="LLM Provider"
          onChange={(e) => onProviderChange(e.target.value)}
        >
          {availableProviders.map((providerKey) => {
            const provider = providers[providerKey];
            return (
              <MenuItem key={providerKey} value={providerKey}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <span>{getProviderIcon(providerKey)}</span>
                  <span>{getProviderDisplayName(providerKey)}</span>
                  {provider?.is_default && (
                    <CheckIcon sx={{ fontSize: 16, color: 'success.main' }} />
                  )}
                </Box>
              </MenuItem>
            );
          })}
        </Select>
      </FormControl>

      {selectedProvider && providers[selectedProvider] && (
        <Tooltip
          title={
            <Box>
              <Typography variant="body2">
                <strong>Model:</strong> {providers[selectedProvider].model}
              </Typography>
              <Typography variant="body2">
                <strong>Type:</strong> {providers[selectedProvider].type}
              </Typography>
              {providers[selectedProvider].is_default && (
                <Typography variant="body2" color="success.light">
                  <strong>Default Provider</strong>
                </Typography>
              )}
            </Box>
          }
        >
          <IconButton size="small">
            <InfoIcon sx={{ fontSize: 16 }} />
          </IconButton>
        </Tooltip>
      )}

      <Box sx={{ display: 'flex', gap: 0.5 }}>
        {availableProviders.map((providerKey) => (
          <Chip
            key={providerKey}
            label={getProviderIcon(providerKey)}
            size="small"
            variant={selectedProvider === providerKey ? "filled" : "outlined"}
            onClick={() => onProviderChange(providerKey)}
            sx={{ 
              minWidth: 'auto',
              '& .MuiChip-label': { px: 1 }
            }}
          />
        ))}
      </Box>
    </Box>
  );
};

export default LLMProviderSelector;