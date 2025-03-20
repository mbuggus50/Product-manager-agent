import React from 'react';
import { Box, Typography, Button } from '@mui/material';

const Test: React.FC = () => {
  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Test Page
      </Typography>
      <Typography variant="body1" paragraph>
        This is a simple test page to check if the UI is rendering correctly.
      </Typography>
      <Button variant="contained" color="primary">
        Test Button
      </Button>
    </Box>
  );
};

export default Test;