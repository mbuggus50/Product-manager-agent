import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';
import { AuthProvider, useAuth } from './hooks/useAuth';
import AppRoutes from './routes';
import Layout from './components/layout/Layout';

const theme = createTheme({
  palette: {
    primary: {
      main: '#0077C8',
    },
    secondary: {
      main: '#6B3FA0',
    }
  }
});

const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
};

const AppContent = () => {
  const { isAuthenticated } = useAuth();
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {isAuthenticated ? (
        <Layout>
          <AppRoutes />
        </Layout>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Box sx={{ flexGrow: 1 }}>
            <AppRoutes />
          </Box>
        </Box>
      )}
    </ThemeProvider>
  );
};

export default App;
