import React, { useEffect, useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Typography,
  Divider,
  Grid,
  Chip,
  Link,
  Paper,
  Stack,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import LaunchIcon from '@mui/icons-material/Launch';
import { Requirement } from '../services/requirements.service';
import requirementsService from '../services/requirements.service';

const RequirementDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [requirement, setRequirement] = useState<Requirement | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchRequirement(id);
    }
  }, [id]);

  const fetchRequirement = async (requirementId: string) => {
    try {
      setError(null);
      setLoading(true);
      const data = await requirementsService.getById(requirementId);
      setRequirement(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch requirement details');
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="300px">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !requirement) {
    return (
      <Card>
        <CardContent>
          <Typography color="error">{error || 'Requirement not found'}</Typography>
          <Button 
            component={RouterLink} 
            to="/requirements" 
            startIcon={<ArrowBackIcon />}
            sx={{ mt: 2 }}
          >
            Back to Requirements
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        <Button 
          component={RouterLink} 
          to="/requirements" 
          startIcon={<ArrowBackIcon />}
          sx={{ mr: 2 }}
        >
          Back
        </Button>
        <Typography variant="h5">Requirement Details</Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="flex-start">
              <Typography variant="h5" gutterBottom>
                {requirement.businessNeed || requirement.business_need}
              </Typography>
              <Chip 
                label={requirement.status} 
                color={getStatusColor(requirement.status) as any}
              />
            </Box>
            
            <Typography variant="subtitle2" color="text.secondary">
              Created: {formatDate(requirement.created_at)}
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Typography variant="h6" gutterBottom>
                  Requirements
                </Typography>
                <Typography variant="body1" paragraph style={{ whiteSpace: 'pre-line' }}>
                  {requirement.requirements}
                </Typography>
                
                <Typography variant="h6" gutterBottom>
                  Business Impact
                </Typography>
                <Typography variant="body1" paragraph>
                  {requirement.businessImpact || requirement.business_impact}
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Timeline
                    </Typography>
                    <Box mb={2}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Delivery Date
                      </Typography>
                      <Typography variant="body1">
                        {requirement.deliveryDate || requirement.delivery_date}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="subtitle2" color="text.secondary">
                        Campaign Date
                      </Typography>
                      <Typography variant="body1">
                        {requirement.campaignDate || requirement.campaign_date}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
                
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Contributors
                    </Typography>
                    {requirement.contributors && requirement.contributors.length > 0 ? (
                      <Stack spacing={1}>
                        {requirement.contributors.map((contributor: string, index: number) => (
                          <Chip key={index} label={contributor} size="small" />
                        ))}
                      </Stack>
                    ) : (
                      <Typography variant="body2">
                        No contributors specified
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            {requirement.definitions && requirement.definitions.length > 0 && (
              <Box mt={3}>
                <Typography variant="h6" gutterBottom>
                  Definitions
                </Typography>
                <Grid container spacing={2}>
                  {requirement.definitions.map((def, index) => (
                    <Grid item xs={12} md={6} key={index}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {def.attribute}
                        </Typography>
                        <Typography variant="body2">
                          {def.definition}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
            
            {requirement.status === 'complete' && requirement.document_links && (
              <Box mt={4}>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Generated Documents
                </Typography>
                <Stack spacing={1}>
                  {requirement.document_links.google_doc && (
                    <Link 
                      href={requirement.document_links.google_doc} 
                      target="_blank"
                      rel="noopener"
                      sx={{ display: 'flex', alignItems: 'center' }}
                    >
                      <LaunchIcon fontSize="small" sx={{ mr: 1 }} />
                      PRD Document
                    </Link>
                  )}
                  {requirement.document_links.jira_ticket && (
                    <Link 
                      href={requirement.document_links.jira_ticket} 
                      target="_blank"
                      rel="noopener"
                      sx={{ display: 'flex', alignItems: 'center' }}
                    >
                      <LaunchIcon fontSize="small" sx={{ mr: 1 }} />
                      JIRA Ticket
                    </Link>
                  )}
                  {requirement.document_links.wiki_page && (
                    <Link 
                      href={requirement.document_links.wiki_page} 
                      target="_blank"
                      rel="noopener"
                      sx={{ display: 'flex', alignItems: 'center' }}
                    >
                      <LaunchIcon fontSize="small" sx={{ mr: 1 }} />
                      Technical Design Document
                    </Link>
                  )}
                </Stack>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RequirementDetail;