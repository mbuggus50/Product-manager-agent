import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Collapse,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

interface ValidationFeedbackProps {
  validationResults: {
    is_valid: boolean;
    missing_fields?: string[];
    feedback?: string;
    examples?: Record<string, string>;
  };
  onDismiss: () => void;
}

const ValidationFeedback: React.FC<ValidationFeedbackProps> = ({
  validationResults,
  onDismiss,
}) => {
  return (
    <Box sx={{ mb: 4 }}>
      <Alert 
        severity={validationResults.is_valid ? "success" : "warning"} 
        action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="small"
            onClick={onDismiss}
          >
            <CloseIcon fontSize="inherit" />
          </IconButton>
        }
      >
        <AlertTitle>
          {validationResults.is_valid 
            ? "Validation Successful" 
            : "Validation Issues Detected"
          }
        </AlertTitle>
        
        {validationResults.feedback && (
          <Typography variant="body2" sx={{ mt: 1, mb: 2 }}>
            {validationResults.feedback}
          </Typography>
        )}
        
        {validationResults.missing_fields && validationResults.missing_fields.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="subtitle2">Missing Information:</Typography>
            <List dense disablePadding>
              {validationResults.missing_fields.map((field, index) => (
                <ListItem key={index} disablePadding sx={{ py: 0.5 }}>
                  <ListItemText primary={field} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
        
        {validationResults.examples && Object.keys(validationResults.examples).length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2">Examples to improve your requirement:</Typography>
            <List dense disablePadding>
              {Object.entries(validationResults.examples).map(([field, example], index) => (
                <React.Fragment key={field}>
                  {index > 0 && <Divider />}
                  <ListItem disablePadding sx={{ py: 1 }}>
                    <ListItemText 
                      primary={field} 
                      secondary={example}
                      primaryTypographyProps={{ fontWeight: 'bold' }}
                    />
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          </Box>
        )}
      </Alert>
    </Box>
  );
};

export default ValidationFeedback;