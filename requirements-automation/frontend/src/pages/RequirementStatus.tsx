import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  Box, 
  Card, 
  CardContent, 
  CircularProgress, 
  Typography, 
  Stepper, 
  Step, 
  StepLabel, 
  Link,
  Alert
} from '@mui/material';
import requirementsService from '../services/requirements.service';

interface StatusLocationState {
  requirementId: string;
  links?: Record<string, string>;
}

const RequirementStatus: React.FC = () => {
  const location = useLocation();
  const [requirementId, setRequirementId] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [currentNode, setCurrentNode] = useState<string>('');
  const [links, setLinks] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<number | null>(null);
  
  // Workflow steps mapping
  const workflowSteps = [
    { id: 'validation', label: 'Validation' },
    { id: 'formatting', label: 'Formatting' },
    { id: 'document_creation', label: 'Document Creation' },
    { id: 'design_document', label: 'Design Document' },
    { id: 'complete', label: 'Complete' }
  ];
  
  // Initialize from location state or query param
  useEffect(() => {
    const state = location.state as StatusLocationState | null;
    if (state && state.requirementId) {
      setRequirementId(state.requirementId);
      if (state.links) {
        setLinks(state.links);
      }
    } else {
      // For demo, we'll use a mock ID
      setRequirementId('req-1');
    }
  }, [location]);
  
  // Get current step index based on node
  const getCurrentStepIndex = () => {
    const index = workflowSteps.findIndex(step => step.id === currentNode);
    return index >= 0 ? index : 0;
  };
  
  // Check status when requirementId changes
  useEffect(() => {
    if (requirementId) {
      fetchStatus();
      
      // Set up polling if not already polling
      if (!pollingInterval && currentNode !== 'complete' && currentNode !== 'error') {
        const interval = window.setInterval(() => {
          fetchStatus();
        }, 5000); // Check every 5 seconds
        
        setPollingInterval(interval);
      }
      
      // Clean up interval on unmount
      return () => {
        if (pollingInterval) {
          clearInterval(pollingInterval as number);
        }
      };
    }
  }, [requirementId]);
  
  // Stop polling when complete
  useEffect(() => {
    if ((currentNode === 'complete' || currentNode === 'error') && pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  }, [currentNode, pollingInterval]);
  
  const fetchStatus = async () => {
    if (!requirementId) return;
    
    try {
      setError(null);
      const response = await requirementsService.getStatus(requirementId);
      
      setStatus(response.status);
      setCurrentNode(response.current_node || '');
      
      // Update links if available
      if (response.links && Object.keys(response.links).length > 0) {
        setLinks(response.links);
      }
      
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch status');
      setLoading(false);
    }
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
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Requirement Status
        </Typography>
        
        <Box my={4}>
          <Stepper activeStep={getCurrentStepIndex()}>
            {workflowSteps.map((step) => (
              <Step key={step.id}>
                <StepLabel>{step.label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Box>
        
        <Typography variant="h6" gutterBottom>
          Current Status: {status}
        </Typography>
        
        {currentNode === 'error' && (
          <Alert severity="error" sx={{ my: 2 }}>
            An error occurred during processing. Please check the details and try again.
          </Alert>
        )}
        
        {currentNode === 'complete' && (
          <>
            <Typography variant="h6" gutterBottom>
              Documents Generated
            </Typography>
            
            <Box component="ul">
              {links.google_doc && (
                <Box component="li" my={1}>
                  <Link href={links.google_doc} target="_blank" rel="noopener">
                    PRD Document
                  </Link>
                </Box>
              )}
              
              {links.jira_ticket && (
                <Box component="li" my={1}>
                  <Link href={links.jira_ticket} target="_blank" rel="noopener">
                    JIRA Ticket
                  </Link>
                </Box>
              )}
              
              {links.wiki_page && (
                <Box component="li" my={1}>
                  <Link href={links.wiki_page} target="_blank" rel="noopener">
                    Technical Design Document
                  </Link>
                </Box>
              )}
            </Box>
          </>
        )}
        
        {(currentNode !== 'complete' && currentNode !== 'error') && (
          <Typography variant="body1">
            Your requirement is being processed. This page will automatically update when complete.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default RequirementStatus;