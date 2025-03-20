import React, { useState } from 'react';
import { 
  TextField, 
  Box, 
  Typography, 
  Chip,
  Stack,
  Button,
  Grid
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

interface RequirementsDetailFormProps {
  requirements: string;
  businessImpact: string;
  contributors: string[];
  onRequirementsChange: (value: string) => void;
  onBusinessImpactChange: (value: string) => void;
  onContributorsChange: (value: string[]) => void;
}

const RequirementsDetailForm: React.FC<RequirementsDetailFormProps> = ({
  requirements,
  businessImpact,
  contributors,
  onRequirementsChange,
  onBusinessImpactChange,
  onContributorsChange,
}) => {
  const [newContributor, setNewContributor] = useState('');

  const handleAddContributor = () => {
    if (newContributor.trim() === '') return;
    
    onContributorsChange([...contributors, newContributor.trim()]);
    setNewContributor('');
  };

  const handleDeleteContributor = (contributorToDelete: string) => {
    onContributorsChange(
      contributors.filter((contributor) => contributor !== contributorToDelete)
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddContributor();
    }
  };

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Detailed Requirements
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Provide detailed requirements with who/what/where/when/why. Be as specific as possible.
          </Typography>
          
          <TextField
            fullWidth
            label="Requirements"
            multiline
            rows={6}
            value={requirements}
            onChange={(e) => onRequirementsChange(e.target.value)}
            placeholder="Describe the detailed requirements for this feature/product"
            helperText="Include who, what, where, when, why details"
            required
            sx={{ mb: 4 }}
          />
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Business Impact
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Explain the impact if delivered or not delivered. Why is this important?
          </Typography>
          
          <TextField
            fullWidth
            label="Business Impact"
            multiline
            rows={4}
            value={businessImpact}
            onChange={(e) => onBusinessImpactChange(e.target.value)}
            placeholder="Describe the business impact of this requirement"
            helperText="What happens if we deliver this? What happens if we don't?"
            required
            sx={{ mb: 4 }}
          />
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Contributors
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Add people who should be involved in this requirement.
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
            <TextField
              label="Add Contributor"
              value={newContributor}
              onChange={(e) => setNewContributor(e.target.value)}
              onKeyPress={handleKeyPress}
              sx={{ mr: 1, flexGrow: 1 }}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleAddContributor}
              startIcon={<AddIcon />}
              sx={{ ml: 1 }}
            >
              Add
            </Button>
          </Box>
          
          {contributors.length > 0 ? (
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {contributors.map((contributor, index) => (
                <Chip
                  key={index}
                  label={contributor}
                  onDelete={() => handleDeleteContributor(contributor)}
                  sx={{ m: 0.5 }}
                />
              ))}
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No contributors added yet
            </Typography>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default RequirementsDetailForm;