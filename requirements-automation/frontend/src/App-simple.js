import React from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Button, 
  Container, 
  CssBaseline, 
  ThemeProvider,
  createTheme,
  AppBar,
  Toolbar,
  Paper,
  TextField,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Card,
  CardContent,
  CardActions,
  CircularProgress,
  Alert,
  LinearProgress,
  Snackbar,
  Divider
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AssignmentIcon from '@mui/icons-material/Assignment';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#0077C8', // Blue
    },
    secondary: {
      main: '#6B3FA0', // Purple
    },
  },
});

// Home page component
const Home = () => (
  <Box sx={{ my: 4 }}>
    <Box sx={{ textAlign: 'center', mb: 6 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Requirements Automation
      </Typography>
      <Typography variant="h6" color="text.secondary" paragraph sx={{ maxWidth: '700px', mx: 'auto' }}>
        Streamline your product requirements process with AI-powered automation
      </Typography>
    </Box>
    
    <Grid container spacing={4}>
      <Grid item xs={12} md={4}>
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ flexGrow: 1 }}>
            <AssignmentIcon color="primary" sx={{ fontSize: 40, mb: 2 }} />
            <Typography variant="h5" component="h2" gutterBottom>
              Create Requirements
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Create structured product requirements that capture business needs, technical requirements, and timelines.
            </Typography>
          </CardContent>
          <CardActions>
            <Button size="small" component={Link} to="/new">Create New</Button>
          </CardActions>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ flexGrow: 1 }}>
            <AutoAwesomeIcon color="primary" sx={{ fontSize: 40, mb: 2 }} />
            <Typography variant="h5" component="h2" gutterBottom>
              AI-Powered Generation
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Use AI to automatically generate, validate, and enhance product requirement documents.
            </Typography>
          </CardContent>
          <CardActions>
            <Button size="small" component={Link} to="/about">Learn More</Button>
          </CardActions>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ flexGrow: 1 }}>
            <DashboardIcon color="primary" sx={{ fontSize: 40, mb: 2 }} />
            <Typography variant="h5" component="h2" gutterBottom>
              Track Progress
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Monitor the status of your requirements and view insights on your product documentation.
            </Typography>
          </CardContent>
          <CardActions>
            <Button size="small" component={Link} to="/dashboard">View Dashboard</Button>
          </CardActions>
        </Card>
      </Grid>
    </Grid>
    
    <Box sx={{ mt: 6, textAlign: 'center' }}>
      <Button 
        variant="contained" 
        color="primary" 
        size="large"
        component={Link}
        to="/new"
        startIcon={<AddIcon />}
      >
        Create New Requirement
      </Button>
    </Box>
  </Box>
);

// About page component
const About = () => (
  <Box sx={{ my: 4 }}>
    <Typography variant="h4" component="h1" gutterBottom>
      About This Project
    </Typography>
    
    <Paper sx={{ p: 3, mb: 4 }}>
      <Typography variant="h5" gutterBottom>
        AI-Powered Requirements Automation
      </Typography>
      <Typography variant="body1" paragraph>
        This tool helps product managers streamline the creation and management of product requirements using advanced AI technology. 
        Our platform leverages state-of-the-art language models to assist with generating, refining, and validating product requirements.
      </Typography>
      <Typography variant="body1" paragraph>
        By automating the repetitive and time-consuming aspects of requirements engineering, 
        product managers can focus on strategic decision-making and stakeholder alignment.
      </Typography>
    </Paper>
    
    <Typography variant="h5" gutterBottom>
      Key Features
    </Typography>
    
    <Grid container spacing={3} sx={{ mb: 4 }}>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom color="primary">
            AI-Powered Generation
          </Typography>
          <Typography variant="body2">
            Generate detailed requirements automatically from high-level business needs. The AI suggests specific, 
            actionable requirements and outlines business impact.
          </Typography>
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom color="primary">
            Validation & Quality
          </Typography>
          <Typography variant="body2">
            Automatically validate requirements for clarity, completeness, and consistency. 
            Receive AI feedback on how to improve your requirements for better implementation.
          </Typography>
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom color="primary">
            Integration & Export
          </Typography>
          <Typography variant="body2">
            Seamlessly export requirements to popular tools like JIRA, Google Docs, and more. 
            Convert requirements into various formats suitable for different stakeholders.
          </Typography>
        </Paper>
      </Grid>
    </Grid>
    
    <Typography variant="h5" gutterBottom>
      How It Works
    </Typography>
    
    <Paper sx={{ p: 3, mb: 4 }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Box>
          <Typography variant="h6">1. Input Your Business Need</Typography>
          <Typography variant="body2">
            Provide a high-level description of what the business is asking for.
          </Typography>
        </Box>
        
        <Box>
          <Typography variant="h6">2. AI-Enhanced Processing</Typography>
          <Typography variant="body2">
            Our AI analyzes your input and generates detailed requirements, business impact assessments, and validation feedback.
          </Typography>
        </Box>
        
        <Box>
          <Typography variant="h6">3. Review and Refine</Typography>
          <Typography variant="body2">
            Review the AI-generated content, make adjustments as needed, and finalize your requirements.
          </Typography>
        </Box>
        
        <Box>
          <Typography variant="h6">4. Export and Share</Typography>
          <Typography variant="body2">
            Generate finalized documents in various formats and export to tools like JIRA, Google Docs, etc.
          </Typography>
        </Box>
      </Box>
    </Paper>
    
    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
      <Button 
        variant="contained" 
        color="primary" 
        component={Link}
        to="/"
      >
        Back to Home
      </Button>
      
      <Button 
        variant="contained" 
        color="secondary"
        component={Link}
        to="/new"
        startIcon={<AddIcon />}
      >
        Try It Now
      </Button>
    </Box>
  </Box>
);

// Header component
const Header = () => (
  <AppBar position="static">
    <Toolbar>
      <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
        Product Requirements Automation
      </Typography>
      <Button color="inherit" component={Link} to="/">Home</Button>
      <Button color="inherit" component={Link} to="/dashboard">
        <DashboardIcon sx={{ mr: 1 }} fontSize="small" />
        Dashboard
      </Button>
      <Button color="inherit" component={Link} to="/requirements">
        <AssignmentIcon sx={{ mr: 1 }} fontSize="small" />
        Requirements
      </Button>
      <Button color="inherit" component={Link} to="/new">New Requirement</Button>
      <Button color="inherit" component={Link} to="/about">About</Button>
    </Toolbar>
  </AppBar>
);

// New Requirement Form
const NewRequirement = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = React.useState({
    businessNeed: '',
    requirements: '',
    businessImpact: '',
    deliveryDate: '',
    campaignDate: '',
  });
  
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [aiSuggestion, setAiSuggestion] = React.useState(null);
  const [snackbarOpen, setSnackbarOpen] = React.useState(false);
  const [snackbarMessage, setSnackbarMessage] = React.useState('');
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    // This would send the data to the backend in a real app
    setSnackbarMessage("Requirement successfully created!");
    setSnackbarOpen(true);
    
    // Navigate to the requirements list after submission
    setTimeout(() => {
      navigate('/requirements');
    }, 1500);
  };
  
  const handleGenerateWithAI = () => {
    if (!formData.businessNeed.trim()) {
      setSnackbarMessage("Please provide a business need first");
      setSnackbarOpen(true);
      return;
    }
    
    setIsGenerating(true);
    
    // Simulate AI generation with a timeout
    setTimeout(() => {
      // In a real app, this would call an API to generate requirements
      const mockAiSuggestion = {
        requirements: `Based on the business need, the following requirements are identified:

1. Create a user-friendly interface for ${formData.businessNeed.split(' ').slice(0, 3).join(' ')}
2. Implement secure authentication mechanisms
3. Ensure data validation and error handling
4. Provide comprehensive analytics and reporting functionality
5. Support integration with existing systems via APIs
6. Implement responsive design for mobile and desktop compatibility`,
        
        businessImpact: `The successful implementation of this project will:
- Increase operational efficiency by approximately 30%
- Reduce manual workload for the team
- Improve data accuracy and decision-making capabilities
- Enhance customer satisfaction through improved services

If not delivered, the organization risks falling behind competitors and losing market share.`
      };
      
      setAiSuggestion(mockAiSuggestion);
      setIsGenerating(false);
      setSnackbarMessage("AI suggestions generated successfully!");
      setSnackbarOpen(true);
    }, 2000);
  };
  
  const handleAcceptSuggestion = (field) => {
    if (!aiSuggestion || !aiSuggestion[field]) return;
    
    setFormData(prev => ({
      ...prev,
      [field]: aiSuggestion[field]
    }));
    
    setSnackbarMessage(`${field.charAt(0).toUpperCase() + field.slice(1)} updated with AI suggestion`);
    setSnackbarOpen(true);
  };
  
  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Create New Requirement
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box component="form" onSubmit={handleSubmit}>
          <Typography variant="h6" gutterBottom>
            Business Need
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Describe what the business is asking for.
          </Typography>
          <TextField
            fullWidth
            label="Business Need"
            multiline
            rows={4}
            name="businessNeed"
            value={formData.businessNeed}
            onChange={handleChange}
            margin="normal"
            required
          />
          
          <Box sx={{ mt: 2, mb: 4, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="secondary"
              onClick={handleGenerateWithAI}
              disabled={isGenerating}
              startIcon={isGenerating ? <CircularProgress size={20} color="inherit" /> : <AutoAwesomeIcon />}
            >
              {isGenerating ? 'Generating...' : 'Generate with AI'}
            </Button>
          </Box>
          
          {isGenerating && (
            <Box sx={{ width: '100%', mt: 2, mb: 2 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Analyzing business need and generating suggestions...
              </Typography>
              <LinearProgress color="secondary" />
            </Box>
          )}
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Requirements
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Provide detailed requirements with who/what/where/when/why.
          </Typography>
          
          {aiSuggestion && aiSuggestion.requirements && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                AI Suggestion:
              </Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {aiSuggestion.requirements.substring(0, 100)}...
              </Typography>
              <Button 
                size="small" 
                sx={{ mt: 1 }} 
                onClick={() => handleAcceptSuggestion('requirements')}
              >
                Accept Suggestion
              </Button>
            </Alert>
          )}
          
          <TextField
            fullWidth
            label="Requirements"
            multiline
            rows={6}
            name="requirements"
            value={formData.requirements}
            onChange={handleChange}
            margin="normal"
            required
          />
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Business Impact
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Explain the impact if delivered or not delivered.
          </Typography>
          
          {aiSuggestion && aiSuggestion.businessImpact && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                AI Suggestion:
              </Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {aiSuggestion.businessImpact.substring(0, 100)}...
              </Typography>
              <Button 
                size="small" 
                sx={{ mt: 1 }} 
                onClick={() => handleAcceptSuggestion('businessImpact')}
              >
                Accept Suggestion
              </Button>
            </Alert>
          )}
          
          <TextField
            fullWidth
            label="Business Impact"
            multiline
            rows={4}
            name="businessImpact"
            value={formData.businessImpact}
            onChange={handleChange}
            margin="normal"
            required
          />
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Timeline
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Delivery Date"
                type="date"
                name="deliveryDate"
                value={formData.deliveryDate}
                onChange={handleChange}
                margin="normal"
                InputLabelProps={{
                  shrink: true,
                }}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Campaign Date"
                type="date"
                name="campaignDate"
                value={formData.campaignDate}
                onChange={handleChange}
                margin="normal"
                InputLabelProps={{
                  shrink: true,
                }}
                required
              />
            </Grid>
          </Grid>
          
          <Box sx={{ mt: 4, textAlign: 'right' }}>
            <Button 
              type="submit"
              variant="contained" 
              color="primary" 
              size="large"
            >
              Submit Requirement
            </Button>
          </Box>
        </Box>
      </Paper>
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
      />
    </Box>
  );
};

// Requirements List
const RequirementsList = () => {
  // State for filters
  const [statusFilter, setStatusFilter] = React.useState('all');
  const [searchQuery, setSearchQuery] = React.useState('');
  
  // Mock data - in a real app this would come from an API
  const allRequirements = [
    { id: 'req-1', businessNeed: 'Customer Analytics Dashboard', status: 'complete', created: '2023-03-01', owner: 'John Smith', priority: 'high' },
    { id: 'req-2', businessNeed: 'User Onboarding Flow Optimization', status: 'in-progress', created: '2023-03-05', owner: 'Sarah Johnson', priority: 'medium' },
    { id: 'req-3', businessNeed: 'Payment Processing Integration', status: 'pending', created: '2023-03-10', owner: 'Alex Wong', priority: 'high' },
    { id: 'req-4', businessNeed: 'Marketing Campaign Analytics', status: 'complete', created: '2023-02-20', owner: 'Emily Davis', priority: 'medium' },
    { id: 'req-5', businessNeed: 'Customer Support Chatbot', status: 'in-progress', created: '2023-03-08', owner: 'John Smith', priority: 'low' },
  ];
  
  // Filter requirements based on status and search query
  const filteredRequirements = allRequirements.filter(req => {
    const matchesStatus = statusFilter === 'all' || req.status === statusFilter;
    const matchesSearch = req.businessNeed.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          req.owner.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'complete': return 'success';
      case 'in-progress': return 'warning';
      case 'pending': return 'info';
      default: return 'default';
    }
  };
  
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };
  
  const handleStatusFilterChange = (event) => {
    setStatusFilter(event.target.value);
  };
  
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };
  
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Requirements
        </Typography>
        <Button 
          variant="contained" 
          color="primary"
          component={Link}
          to="/new"
          startIcon={<AddIcon />}
        >
          New Requirement
        </Button>
      </Box>
      
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search"
              variant="outlined"
              size="small"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search by title or owner"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              select
              fullWidth
              label="Status"
              variant="outlined"
              size="small"
              value={statusFilter}
              onChange={handleStatusFilterChange}
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="in-progress">In Progress</option>
              <option value="complete">Complete</option>
            </TextField>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip label={`Total: ${allRequirements.length}`} variant="outlined" />
              <Chip 
                label={`Filtered: ${filteredRequirements.length}`} 
                color="primary" 
                variant={filteredRequirements.length < allRequirements.length ? "filled" : "outlined"} 
              />
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Requirements Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Business Need</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredRequirements.length > 0 ? (
              filteredRequirements.map((req) => (
                <TableRow key={req.id} hover>
                  <TableCell>{req.businessNeed}</TableCell>
                  <TableCell>
                    <Chip
                      label={req.status}
                      color={getStatusColor(req.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={req.priority}
                      color={getPriorityColor(req.priority)}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{req.owner}</TableCell>
                  <TableCell>{req.created}</TableCell>
                  <TableCell align="right">
                    <Button
                      variant="outlined"
                      size="small"
                      component={Link}
                      to={`/requirements/${req.id}`}
                    >
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Box sx={{ py: 3 }}>
                    <Typography variant="body1" color="text.secondary">
                      No requirements found matching your filters.
                    </Typography>
                    <Button
                      variant="text"
                      onClick={() => {
                        setStatusFilter('all');
                        setSearchQuery('');
                      }}
                      sx={{ mt: 1 }}
                    >
                      Clear Filters
                    </Button>
                  </Box>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

// Requirement Detail View
const RequirementDetail = () => {
  // In a real app, you would use useParams to get the ID from the URL
  // and fetch the requirement data from the API
  const requirementId = "req-1"; // This would be dynamic in a real app
  
  // Mock data
  const requirement = {
    id: 'req-1',
    businessNeed: 'Customer Analytics Dashboard',
    requirements: 'Create a dashboard that shows customer behavior analytics across our platforms. The dashboard should include visualizations for user engagement, conversion rates, and retention metrics.',
    businessImpact: 'This dashboard will help the marketing team optimize campaigns and increase conversion rates. Without it, we will continue to make decisions with incomplete data.',
    deliveryDate: '2023-04-15',
    campaignDate: '2023-05-01',
    status: 'complete',
    created: '2023-03-01',
    documents: {
      prd: 'https://docs.google.com/document/d/1234',
      jira: 'https://jira.example.com/browse/PRD-123',
      design: 'https://figma.com/file/123456'
    },
    processingSteps: [
      { id: 'step-1', name: 'Validation', status: 'complete', completedAt: '2023-03-02', message: 'Requirements validated successfully' },
      { id: 'step-2', name: 'AI Processing', status: 'complete', completedAt: '2023-03-03', message: 'AI processing completed with high confidence score' },
      { id: 'step-3', name: 'Document Generation', status: 'complete', completedAt: '2023-03-04', message: 'All documents generated successfully' },
      { id: 'step-4', name: 'Integration', status: 'complete', completedAt: '2023-03-05', message: 'Successfully integrated with JIRA and other systems' }
    ],
    feedback: [
      { id: 'feedback-1', type: 'improvement', message: 'Consider adding more specific KPIs for measuring success', timestamp: '2023-03-03' },
      { id: 'feedback-2', type: 'positive', message: 'Clear business impact and requirements', timestamp: '2023-03-04' }
    ]
  };
  
  // Define step status colors
  const getStepStatusColor = (status) => {
    switch(status) {
      case 'complete': return 'success';
      case 'in-progress': return 'warning';
      case 'pending': return 'info';
      case 'failed': return 'error';
      default: return 'default';
    }
  };
  
  // Get feedback chip color
  const getFeedbackColor = (type) => {
    switch(type) {
      case 'positive': return 'success';
      case 'improvement': return 'warning';
      case 'issue': return 'error';
      default: return 'default';
    }
  };
  
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            {requirement.businessNeed}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Created: {requirement.created} | Status: 
            <Chip 
              label={requirement.status}
              color={requirement.status === 'complete' ? 'success' : 'warning'}
              size="small"
              sx={{ ml: 1 }}
            />
          </Typography>
        </Box>
        <Button 
          variant="outlined"
          component={Link}
          to="/requirements"
        >
          Back to List
        </Button>
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Requirements
            </Typography>
            <Typography variant="body1">
              {requirement.requirements}
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Business Impact
            </Typography>
            <Typography variant="body1">
              {requirement.businessImpact}
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Timeline
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Delivery Date
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              {requirement.deliveryDate}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Campaign Date
            </Typography>
            <Typography variant="body1">
              {requirement.campaignDate}
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Processing Status
            </Typography>
            
            <Box sx={{ width: '100%', mb: 3 }}>
              {requirement.processingSteps.map((step, index) => (
                <Box key={step.id} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body1">
                      {index + 1}. {step.name}
                    </Typography>
                    <Chip 
                      label={step.status}
                      color={getStepStatusColor(step.status)}
                      size="small"
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Box sx={{ width: '100%', mr: 1 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={step.status === 'complete' ? 100 : step.status === 'in-progress' ? 60 : 0}
                        color={getStepStatusColor(step.status)}
                      />
                    </Box>
                    {step.status === 'complete' && step.completedAt && (
                      <Typography variant="caption" color="text.secondary">
                        {step.completedAt}
                      </Typography>
                    )}
                  </Box>
                  
                  {step.message && (
                    <Typography variant="body2" color="text.secondary">
                      {step.message}
                    </Typography>
                  )}
                  
                  {index < requirement.processingSteps.length - 1 && (
                    <Divider sx={{ my: 2 }} />
                  )}
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
        
        {requirement.feedback && requirement.feedback.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                AI Feedback
              </Typography>
              
              {requirement.feedback.map((item) => (
                <Box key={item.id} sx={{ mb: 2, display: 'flex', alignItems: 'flex-start' }}>
                  <Chip 
                    label={item.type}
                    color={getFeedbackColor(item.type)}
                    size="small"
                    sx={{ mr: 2, mt: 0.5 }}
                  />
                  <Box>
                    <Typography variant="body1">
                      {item.message}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {item.timestamp}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Paper>
          </Grid>
        )}
        
        {requirement.status === 'complete' && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Generated Documents
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button 
                  variant="contained" 
                  color="primary"
                  href={requirement.documents.prd}
                  target="_blank"
                  startIcon={<AssignmentIcon />}
                >
                  View PRD
                </Button>
                <Button 
                  variant="outlined"
                  href={requirement.documents.jira}
                  target="_blank"
                >
                  JIRA Ticket
                </Button>
                <Button 
                  variant="outlined"
                  href={requirement.documents.design}
                  target="_blank"
                >
                  Design Document
                </Button>
              </Box>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

// Dashboard Component
const Dashboard = () => {
  // This would normally come from an API
  const stats = {
    total: 12,
    inProgress: 3,
    completed: 8,
    pending: 1
  };
  
  const recentActivity = [
    { id: 'act-1', action: 'Requirement created', item: 'Mobile App Authentication', date: '2023-03-12' },
    { id: 'act-2', action: 'AI generation completed', item: 'Customer Analytics Dashboard', date: '2023-03-10' },
    { id: 'act-3', action: 'Requirement updated', item: 'Payment Processing Integration', date: '2023-03-08' }
  ];
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h4" color="primary">
              {stats.total}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Requirements
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h4" color="success.main">
              {stats.completed}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Completed
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h4" color="warning.main">
              {stats.inProgress}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              In Progress
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h4" color="info.main">
              {stats.pending}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Pending
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Action</TableCell>
                  <TableCell>Item</TableCell>
                  <TableCell>Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentActivity.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.action}</TableCell>
                    <TableCell>{item.item}</TableCell>
                    <TableCell>{item.date}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Button 
                variant="contained" 
                color="primary" 
                component={Link} 
                to="/new"
                startIcon={<AddIcon />}
              >
                New Requirement
              </Button>
              <Button 
                variant="outlined" 
                component={Link} 
                to="/requirements"
                startIcon={<AssignmentIcon />}
              >
                View Requirements
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Header />
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/about" element={<About />} />
              <Route path="/new" element={<NewRequirement />} />
              <Route path="/requirements" element={<RequirementsList />} />
              <Route path="/requirements/:id" element={<RequirementDetail />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </Container>
          <Box component="footer" sx={{ bgcolor: '#f5f5f5', py: 3, mt: 'auto' }}>
            <Container maxWidth="lg">
              <Typography variant="body2" align="center">
                © {new Date().getFullYear()} Product Requirements Automation
              </Typography>
            </Container>
          </Box>
        </Box>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;