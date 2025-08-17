import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Avatar,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  AdminPanelSettings,
  AccountBalance,
  Person,
  Refresh,
  Add,
  Remove
} from '@mui/icons-material';
import { apiClient } from '../services/apiClient';

interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  role: string;
  status: string;
  credits: number;
  total_credits_used: number;
  created_at: string;
  last_login?: string;
}

interface AdminPanelProps {
  currentUser: any;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ currentUser }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creditDialog, setCreditDialog] = useState<{
    open: boolean;
    user?: User;
    amount: string;
    operation: 'add' | 'deduct';
  }>({
    open: false,
    amount: '',
    operation: 'add'
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/auth/admin/users');
      setUsers(response.data.users);
      setError(null);
    } catch (err: any) {
      console.error('Failed to load users:', err);
      setError(err.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreditUpdate = async () => {
    if (!creditDialog.user || !creditDialog.amount) return;

    try {
      await apiClient.post(
        `/auth/admin/users/${creditDialog.user.id}/credits?amount=${creditDialog.amount}&operation=${creditDialog.operation}`
      );
      
      setCreditDialog({ open: false, amount: '', operation: 'add' });
      loadUsers(); // Refresh users list
    } catch (err: any) {
      console.error('Failed to update credits:', err);
      setError(err.response?.data?.detail || 'Failed to update credits');
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  const getRoleColor = (role: string) => {
    return role === 'admin' ? 'error' : 'default';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'error';
      default: return 'default';
    }
  };

  if (!currentUser?.role || currentUser.role !== 'admin') {
    return (
      <Box p={3}>
        <Alert severity="error">
          Access denied. Admin privileges required.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" alignItems="center" mb={3}>
        <AdminPanelSettings sx={{ mr: 2, fontSize: 32 }} />
        <Typography variant="h4" component="h1">
          Admin Panel
        </Typography>
        <Box flexGrow={1} />
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadUsers}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            User Management
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>User</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Credits</TableCell>
                  <TableCell align="right">Used</TableCell>
                  <TableCell>Joined</TableCell>
                  <TableCell>Last Login</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Avatar
                          src={user.avatar_url}
                          sx={{ width: 32, height: 32, mr: 2 }}
                        >
                          <Person />
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {user.username}
                          </Typography>
                          {user.full_name && (
                            <Typography variant="caption" color="text.secondary">
                              {user.full_name}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Chip
                        label={user.role}
                        color={getRoleColor(user.role)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.status}
                        color={getStatusColor(user.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="bold">
                        ${user.credits.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" color="text.secondary">
                        ${user.total_credits_used.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell>{formatDate(user.last_login)}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="Add Credits">
                        <IconButton
                          size="small"
                          onClick={() => setCreditDialog({
                            open: true,
                            user,
                            amount: '',
                            operation: 'add'
                          })}
                        >
                          <Add />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Deduct Credits">
                        <IconButton
                          size="small"
                          onClick={() => setCreditDialog({
                            open: true,
                            user,
                            amount: '',
                            operation: 'deduct'
                          })}
                        >
                          <Remove />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Credit Update Dialog */}
      <Dialog
        open={creditDialog.open}
        onClose={() => setCreditDialog({ open: false, amount: '', operation: 'add' })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <AccountBalance sx={{ mr: 1 }} />
            {creditDialog.operation === 'add' ? 'Add Credits' : 'Deduct Credits'}
          </Box>
        </DialogTitle>
        <DialogContent>
          {creditDialog.user && (
            <Box>
              <Typography variant="body1" gutterBottom>
                User: <strong>{creditDialog.user.username}</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Current Balance: ${creditDialog.user.credits.toFixed(2)}
              </Typography>
              <TextField
                fullWidth
                label="Amount ($)"
                type="number"
                value={creditDialog.amount}
                onChange={(e) => setCreditDialog(prev => ({ ...prev, amount: e.target.value }))}
                inputProps={{ min: 0, step: 0.01 }}
                sx={{ mt: 2 }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setCreditDialog({ open: false, amount: '', operation: 'add' })}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreditUpdate}
            variant="contained"
            disabled={!creditDialog.amount}
          >
            {creditDialog.operation === 'add' ? 'Add Credits' : 'Deduct Credits'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminPanel;