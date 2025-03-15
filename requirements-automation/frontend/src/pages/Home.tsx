import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Grid,
  Paper,
  Typography,
  Link,
} from '@mui/material';

const Home: React.FC = () => {
  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #0077C8 0%, #6B3FA0 100%)',
          color: 'white',
          py: 10,
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'url("https://images.unsplash.com/photo-1557804506-669a67965ba0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8dGVjaHx8fHx8fDE2NTE3ODA2MTA&ixlib=rb-1.2.1&q=80&utm_campaign=api-credit&utm_medium=referral&utm_source=unsplash_source&w=1080") center/cover no-repeat',
            opacity: 0.1,
            zIndex: 0,
          }
        }}
      >
        <Container maxWidth="md" sx={{ position: 'relative', zIndex: 1 }}>
          <Typography 
            variant="h2" 
            component="h1" 
            gutterBottom
            sx={{ 
              fontWeight: 800,
              textShadow: '0 2px 10px rgba(0,0,0,0.2)',
              mb: 3 
            }}
          >
            Product Requirements Automation
          </Typography>
          <Typography 
            variant="h5" 
            component="p" 
            paragraph
            sx={{ 
              mb: 4,
              maxWidth: '800px',
              mx: 'auto',
              lineHeight: 1.6
            }}
          >
            Transform your product ideas into comprehensive requirements documents using our powerful AI assistant. Save time, improve clarity, and ensure nothing gets missed.
          </Typography>
          <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              color="secondary"
              size="large"
              component={RouterLink}
              to="/login"
              sx={{ 
                px: 4, 
                py: 1.5,
                fontSize: '1.1rem',
                borderRadius: '30px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 6px 25px rgba(0,0,0,0.15)',
                }
              }}
            >
              Get Started Now
            </Button>
            <Button
              variant="outlined"
              color="inherit"
              size="large"
              component={Link}
              href="#features"
              sx={{ 
                px: 4, 
                py: 1.5,
                fontSize: '1.1rem',
                borderRadius: '30px',
                borderWidth: 2,
                '&:hover': {
                  borderWidth: 2,
                  backgroundColor: 'rgba(255,255,255,0.1)'
                }
              }}
            >
              Learn More
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Box id="features" sx={{ py: 12, backgroundColor: '#f8f9fa' }}>
        <Container maxWidth="lg">
          <Typography
            variant="h3"
            component="h2"
            gutterBottom
            align="center"
            sx={{ 
              mb: 2,
              fontWeight: 700,
              color: '#333' 
            }}
          >
            Powerful Features
          </Typography>
          
          <Typography
            variant="h6"
            component="p"
            align="center"
            color="text.secondary"
            sx={{ 
              mb: 8,
              maxWidth: 700,
              mx: 'auto' 
            }}
          >
            Our AI-powered platform streamlines the entire requirements process, saving you time and ensuring quality.
          </Typography>

          <Grid container spacing={4}>
            <Grid item xs={12} md={6} lg={3}>
              <Paper
                elevation={4}
                sx={{
                  p: 4,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 2,
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
                  }
                }}
              >
                <Box sx={{ mb: 2, color: 'primary.main', fontSize: 40 }}>
                  🧠
                </Box>
                <Typography variant="h5" component="h3" gutterBottom fontWeight="bold">
                  AI-Powered Analysis
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ flexGrow: 1 }}>
                  Automatically analyze and structure your product requirements using advanced AI models tailored for product management.
                </Typography>
                <Button 
                  sx={{ mt: 2, alignSelf: 'flex-start' }} 
                  color="primary"
                >
                  Learn more
                </Button>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6} lg={3}>
              <Paper
                elevation={4}
                sx={{
                  p: 4,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 2,
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
                  }
                }}
              >
                <Box sx={{ mb: 2, color: 'primary.main', fontSize: 40 }}>
                  📄
                </Box>
                <Typography variant="h5" component="h3" gutterBottom fontWeight="bold">
                  Document Generation
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ flexGrow: 1 }}>
                  Create professional PRDs with consistent formatting, complete with executive summaries, technical details, and timelines.
                </Typography>
                <Button 
                  sx={{ mt: 2, alignSelf: 'flex-start' }} 
                  color="primary"
                >
                  Learn more
                </Button>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6} lg={3}>
              <Paper
                elevation={4}
                sx={{
                  p: 4,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 2,
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
                  }
                }}
              >
                <Box sx={{ mb: 2, color: 'primary.main', fontSize: 40 }}>
                  ✅
                </Box>
                <Typography variant="h5" component="h3" gutterBottom fontWeight="bold">
                  Validation
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ flexGrow: 1 }}>
                  Ensure your requirements are complete, clear, and well-defined with automated validation that catches issues early.
                </Typography>
                <Button 
                  sx={{ mt: 2, alignSelf: 'flex-start' }} 
                  color="primary"
                >
                  Learn more
                </Button>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6} lg={3}>
              <Paper
                elevation={4}
                sx={{
                  p: 4,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 2,
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
                  }
                }}
              >
                <Box sx={{ mb: 2, color: 'primary.main', fontSize: 40 }}>
                  🔄
                </Box>
                <Typography variant="h5" component="h3" gutterBottom fontWeight="bold">
                  Easy Integration
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ flexGrow: 1 }}>
                  Export your requirements to popular tools like JIRA, Google Docs, Confluence, and more with one-click integrations.
                </Typography>
                <Button 
                  sx={{ mt: 2, alignSelf: 'flex-start' }} 
                  color="primary"
                >
                  Learn more
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* Call to Action */}
      <Box sx={{ py: 10, bgcolor: 'secondary.main', color: 'white', textAlign: 'center' }}>
        <Container maxWidth="md">
          <Typography variant="h4" component="h2" gutterBottom fontWeight="bold">
            Ready to Streamline Your Requirements Process?
          </Typography>
          <Typography variant="h6" sx={{ mb: 4, maxWidth: 800, mx: 'auto' }}>
            Join thousands of product managers who are saving time and improving their requirements documents with AI.
          </Typography>
          <Button 
            variant="contained" 
            size="large" 
            component={RouterLink}
            to="/signup"
            sx={{ 
              px: 6, 
              py: 1.5,
              backgroundColor: 'white',
              color: 'secondary.main',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.9)',
              }
            }}
          >
            Sign Up Free
          </Button>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;