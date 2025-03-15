import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useRequirement } from '../hooks/useRequirement';
import { Requirement } from '../services/requirements.service';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

const Dashboard: React.FC = () => {
  const { getRequirements, loading: hookLoading, error: hookError } = useRequirement();
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRequirements = async () => {
      try {
        const data = await getRequirements();
        setRequirements(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load requirements');
        setLoading(false);
        console.error('Error fetching requirements:', err);
      }
    };

    fetchRequirements();
  }, []); // Remove dependency on getRequirements to avoid infinite loop

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'success';
      case 'error':
        return 'error';
      case 'validation':
      case 'formatting':
      case 'document_creation':
      case 'design_document':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading || hookLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="300px">
        <CircularProgress />
      </Box>
    );
  }

  if (error || hookError) {
    return (
      <Card>
        <CardContent>
          <Typography color="error">{error || hookError}</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Dashboard</Typography>
        <Button
          variant="contained"
          color="primary"
          component={Link}
          to="/new-requirement"
          startIcon={<AddIcon />}
        >
          Create New Requirement
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Your Requirements
          </Typography>

          {requirements.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" sx={{ mb: 2 }}>
                You haven't created any requirements yet.
              </Typography>
              <Button
                variant="outlined"
                color="primary"
                component={Link}
                to="/new-requirement"
              >
                Create Your First Requirement
              </Button>
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Business Need</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Updated</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {requirements.map((req) => (
                    <TableRow key={req.id} hover>
                      <TableCell>
                        <Typography noWrap sx={{ maxWidth: 300 }}>
                          {req.title || req.businessNeed || req.business_need}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={req.status}
                          color={getStatusColor(req.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(req.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {new Date(req.updated_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell align="right">
                        <Button
                          component={Link}
                          to={`/requirements/${req.id}`}
                          size="small"
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;