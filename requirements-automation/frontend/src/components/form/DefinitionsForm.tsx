import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  IconButton,
  Paper,
  Grid,
  Divider
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';

interface Definition {
  attribute: string;
  definition: string;
}

interface DefinitionsFormProps {
  definitions: Definition[];
  onAddDefinition: (attribute: string, definition: string) => void;
  onRemoveDefinition: (index: number) => void;
}

const DefinitionsForm: React.FC<DefinitionsFormProps> = ({
  definitions,
  onAddDefinition,
  onRemoveDefinition,
}) => {
  const [attribute, setAttribute] = useState('');
  const [definition, setDefinition] = useState('');

  const handleAdd = () => {
    if (attribute.trim() === '' || definition.trim() === '') return;
    
    onAddDefinition(attribute.trim(), definition.trim());
    setAttribute('');
    setDefinition('');
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Definitions (Optional)
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Add any specific attribute definitions or terminology that may need clarification.
        This helps ensure everyone has the same understanding of key concepts.
      </Typography>
      
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Attribute/Term"
            value={attribute}
            onChange={(e) => setAttribute(e.target.value)}
            placeholder="Enter attribute or term"
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Definition"
            value={definition}
            onChange={(e) => setDefinition(e.target.value)}
            placeholder="Enter definition"
          />
        </Grid>
        
        <Grid item xs={12} md={2} sx={{ display: 'flex', alignItems: 'center' }}>
          <Button
            fullWidth
            variant="contained"
            color="primary"
            onClick={handleAdd}
            startIcon={<AddIcon />}
            disabled={attribute.trim() === '' || definition.trim() === ''}
          >
            Add
          </Button>
        </Grid>
      </Grid>
      
      {definitions.length > 0 ? (
        <Paper variant="outlined" sx={{ p: 0 }}>
          <List>
            {definitions.map((def, index) => (
              <React.Fragment key={index}>
                {index > 0 && <Divider />}
                <ListItem
                  sx={{ py: 2 }}
                  secondaryAction={
                    <IconButton 
                      edge="end" 
                      aria-label="delete"
                      onClick={() => onRemoveDefinition(index)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <Box sx={{ width: '100%' }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {def.attribute}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={8}>
                        <Typography variant="body1">
                          {def.definition}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        </Paper>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          No definitions added yet. This step is optional.
        </Typography>
      )}
    </Box>
  );
};

export default DefinitionsForm;