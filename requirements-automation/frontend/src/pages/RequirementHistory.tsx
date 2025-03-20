import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
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
  Button,
  TextField,
  InputAdornment
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { Requirement } from '../services/requirements.service';
import requirementsService from '../services/requirements.service';

const RequirementHistory: React.FC = () => {
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [filteredRequirements, setFilteredRequirements] = useState<Requirement[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const navigate = useNavigate();
  
  // Fetch requirements on component mount
  useEffect(() => {
    fetchRequirements();
  }, []);
  
  // Filter requirements when search term changes
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredRequirements(requirements);
    } else {
      const filtered = requirements.filter(
        req => 
          (req.businessNeed || req.business_need || '').toLowerCase().includes(searchTerm.toLowerCase()) || 
          req.requirements.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredRequirements(filtered);
    }
  }, [searchTerm, requirements]);
  
  const fetchRequirements = async () => {
    try {
      setError(null);
      setLoading(true);
      const data = await requirementsService.getAll();
      setRequirements(data);
      setFilteredRequirements(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch requirements');
      setLoading(false);
    }
  };
  
  const handleRowClick = (id: string) => {
    navigate(`/requirements/${id}`);
  };
  
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
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="300px">
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Card>
        <CardContent>
          <Typography color="error">{error}</Typography>
          <Button variant="outlined" onClick={fetchRequirements} sx={{ mt: 2 }}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">Requirement History</Typography>
          
          <Box>
            <TextField
              placeholder="Search requirements"
              size="small"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
            
            <Button 
              variant="contained" 
              color="primary" 
              sx={{ ml: 2 }}
              onClick={() => navigate('/new-requirement')}
            >
              New Requirement
            </Button>
          </Box>
        </Box>
        
        {filteredRequirements.length === 0 ? (
          <Typography>No requirements found.</Typography>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Business Need</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Campaign Date</TableCell>
                  <TableCell>Created</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredRequirements.map((req) => (
                  <TableRow 
                    key={req.id} 
                    hover 
                    onClick={() => handleRowClick(req.id)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      <Typography noWrap sx={{ maxWidth: 400 }}>
                        {req.businessNeed || req.business_need}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={req.status} 
                        color={getStatusColor(req.status) as any} 
                        size="small" 
                      />
                    </TableCell>
                    <TableCell>{req.campaignDate || req.campaign_date}</TableCell>
                    <TableCell>{formatDate(req.created_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );
};

export default RequirementHistory;