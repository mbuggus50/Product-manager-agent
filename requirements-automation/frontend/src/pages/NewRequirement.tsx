import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  CircularProgress,
  Stepper, 
  Step, 
  StepLabel, 
  Typography,
  Alert
} from '@mui/material';
import BusinessNeedForm from '../components/form/BusinessNeedForm';
import RequirementsDetailForm from '../components/form/RequirementsDetailForm';
import TimelineForm from '../components/form/TimelineForm';
import DefinitionsForm from '../components/form/DefinitionsForm';
import requirementsService from '../services/requirements.service';
import type { RequirementFormData } from '../services/requirements.service';

const steps = ['Business Need', 'Requirements Details', 'Timeline', 'Definitions (Optional)'];

const NewRequirement: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<RequirementFormData>({
    businessNeed: '',
    requirements: '',
    businessImpact: '',
    deliveryDate: '',
    campaignDate: '',
    definitions: [],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const updateFormField = (field: keyof RequirementFormData, value: any) => {
    setFormData((prev: RequirementFormData) => ({
      ...prev,
      [field]: value,
    }));
  };

  const addDefinition = (attribute: string, definition: string) => {
    setFormData((prev: RequirementFormData) => ({
      ...prev,
      definitions: [...(prev.definitions || []), { attribute, definition }],
    }));
  };

  const removeDefinition = (index: number) => {
    setFormData((prev: RequirementFormData) => ({
      ...prev,
      definitions: prev.definitions?.filter((_: any, i: number) => i !== index) || [],
    }));
  };

  const handleSubmit = async () => {
    try {
      setIsSubmitting(true);
      setError(null);
      
      const response = await requirementsService.create(formData);
      
      if (response.success) {
        // Navigate to status page with the ID and any links
        navigate('/status', { 
          state: { 
            requirementId: response.requirement.id,
            links: response.requirement.document_links || {}
          } 
        });
      } else {
        // Handle validation errors or other issues
        setError('Failed to submit requirement');
        setIsSubmitting(false);
      }
    } catch (err) {
      setError('An unexpected error occurred');
      setIsSubmitting(false);
      console.error('Error submitting requirement:', err);
    }
  };

  const isStepValid = () => {
    switch (activeStep) {
      case 0:
        return formData.businessNeed.trim() !== '';
      case 1:
        return (
          formData.requirements.trim() !== '' && 
          (formData.businessImpact?.trim() || '') !== ''
        );
      case 2:
        return (
          (formData.deliveryDate?.trim() || '') !== '' && 
          (formData.campaignDate?.trim() || '') !== ''
        );
      default:
        return true;
    }
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <BusinessNeedForm 
            businessNeed={formData.businessNeed} 
            onBusinessNeedChange={(value) => updateFormField('businessNeed', value)} 
          />
        );
      case 1:
        return (
          <RequirementsDetailForm 
            requirements={formData.requirements}
            businessImpact={formData.businessImpact || ''}
            contributors={[]}
            onRequirementsChange={(value) => updateFormField('requirements', value)}
            onBusinessImpactChange={(value) => updateFormField('businessImpact', value)}
            onContributorsChange={(value) => {/* Contributors not stored in this version */}}
          />
        );
      case 2:
        return (
          <TimelineForm 
            deliveryDate={formData.deliveryDate || ''}
            campaignDate={formData.campaignDate || ''}
            onDeliveryDateChange={(value) => updateFormField('deliveryDate', value)}
            onCampaignDateChange={(value) => updateFormField('campaignDate', value)}
          />
        );
      case 3:
        return (
          <DefinitionsForm 
            definitions={formData.definitions || []}
            onAddDefinition={addDefinition}
            onRemoveDefinition={removeDefinition}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Card sx={{ 
      borderRadius: 2, 
      boxShadow: '0 8px 40px rgba(0,0,0,0.07)',
      overflow: 'visible'
    }}>
      <CardContent sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography 
            variant="h4" 
            component="h1" 
            sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(90deg, #0077C8 0%, #6B3FA0 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              textFillColor: 'transparent'
            }}
          >
            Create New Requirement
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          <Typography variant="body2" color="text.secondary">
            AI-Powered Requirements Generator
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        )}
        
        <Stepper 
          activeStep={activeStep} 
          sx={{ 
            my: 4,
            '& .MuiStepIcon-root.Mui-active': {
              color: 'secondary.main'
            },
            '& .MuiStepIcon-root.Mui-completed': {
              color: 'success.main'
            }
          }}
        >
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <Box sx={{ 
          mt: 2, 
          mb: 4,
          p: 3,
          borderRadius: 2,
          backgroundColor: '#f8f9fa'
        }}>
          {renderStepContent()}
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            variant="outlined"
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>
          
          <Box>
            {activeStep === steps.length - 1 ? (
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Requirement'}
                </Button>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
                  sx={{
                    background: 'linear-gradient(90deg, #6B3FA0 0%, #9B59B6 100%)',
                    boxShadow: '0 4px 10px rgba(107, 63, 160, 0.3)',
                    '&:hover': {
                      background: 'linear-gradient(90deg, #5A2E8A 0%, #8E44AD 100%)',
                      boxShadow: '0 6px 15px rgba(107, 63, 160, 0.4)',
                    }
                  }}
                >
                  {isSubmitting ? 'Processing...' : 'Generate with AI ✨'}
                </Button>
              </Box>
            ) : (
              <Button
                variant="contained"
                color="primary"
                onClick={handleNext}
                disabled={!isStepValid()}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default NewRequirement;