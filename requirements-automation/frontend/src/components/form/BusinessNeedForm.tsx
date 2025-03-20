import React from 'react';
import { TextField, Box, Typography } from '@mui/material';

interface BusinessNeedFormProps {
  businessNeed: string;
  onBusinessNeedChange: (value: string) => void;
}

const BusinessNeedForm: React.FC<BusinessNeedFormProps> = ({
  businessNeed,
  onBusinessNeedChange,
}) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Business Need
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Describe what the business is asking for. This should be a high-level summary
        of the requirement.
      </Typography>
      
      <TextField
        fullWidth
        label="Business Need"
        multiline
        rows={4}
        value={businessNeed}
        onChange={(e) => onBusinessNeedChange(e.target.value)}
        placeholder="Describe the business need or problem to be solved"
        helperText="Be specific about what problem you're trying to solve"
        required
      />
    </Box>
  );
};

export default BusinessNeedForm;