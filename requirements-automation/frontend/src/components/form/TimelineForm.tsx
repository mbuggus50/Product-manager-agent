import React from 'react';
import { Box, Typography, Grid } from '@mui/material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { format, parse } from 'date-fns';

interface TimelineFormProps {
  deliveryDate: string;
  campaignDate: string;
  onDeliveryDateChange: (value: string) => void;
  onCampaignDateChange: (value: string) => void;
}

const TimelineForm: React.FC<TimelineFormProps> = ({
  deliveryDate,
  campaignDate,
  onDeliveryDateChange,
  onCampaignDateChange,
}) => {
  // Convert string to Date object
  const parseDate = (dateStr: string) => {
    if (!dateStr) return null;
    try {
      return parse(dateStr, 'yyyy-MM-dd', new Date());
    } catch (e) {
      return null;
    }
  };

  // Handle date changes from date picker
  const handleDeliveryDateChange = (date: Date | null) => {
    if (date) {
      onDeliveryDateChange(format(date, 'yyyy-MM-dd'));
    }
  };

  const handleCampaignDateChange = (date: Date | null) => {
    if (date) {
      onCampaignDateChange(format(date, 'yyyy-MM-dd'));
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Typography variant="h6" gutterBottom>
          Timeline
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Set the expected delivery and campaign dates for this requirement.
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <DatePicker
              label="Delivery Date"
              value={parseDate(deliveryDate)}
              onChange={handleDeliveryDateChange}
              slotProps={{
                textField: {
                  fullWidth: true,
                  required: true,
                  helperText: "When does engineering need to deliver this feature?"
                }
              }}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <DatePicker
              label="Campaign Date"
              value={parseDate(campaignDate)}
              onChange={handleCampaignDateChange}
              slotProps={{
                textField: {
                  fullWidth: true,
                  required: true,
                  helperText: "When will this feature be used in a campaign?"
                }
              }}
            />
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Note: Please allow sufficient time between delivery and campaign dates to account for testing and validation.
            </Typography>
          </Grid>
        </Grid>
      </Box>
    </LocalizationProvider>
  );
};

export default TimelineForm;