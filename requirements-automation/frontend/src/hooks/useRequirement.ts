import { useState } from 'react';
import requirementsService, { 
  RequirementFormData, 
  RequirementResponse, 
  Requirement 
} from '../services/requirements.service';
import statusService from '../services/status.service';

interface UseRequirementFormReturn {
  formData: RequirementFormData;
  setField: (field: keyof RequirementFormData, value: any) => void;
  addDefinition: (attribute: string, definition: string) => void;
  removeDefinition: (index: number) => void;
  submitForm: () => Promise<RequirementResponse>;
  isSubmitting: boolean;
  error: string | null;
}

// Hook for requirement form operations
export function useRequirementForm(): UseRequirementFormReturn {
  const initialForm: RequirementFormData = {
    businessNeed: '',
    requirements: '',
    businessImpact: '',
    deliveryDate: '',
    campaignDate: '',
    definitions: [],
  };

  const [formData, setFormData] = useState<RequirementFormData>(initialForm);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const setField = (field: keyof RequirementFormData, value: any): void => {
    setFormData((prev: RequirementFormData) => ({ ...prev, [field]: value }));
  };

  const addDefinition = (attribute: string, definition: string): void => {
    setFormData((prev: RequirementFormData) => ({
      ...prev,
      definitions: [...(prev.definitions || []), { attribute, definition }],
    }));
  };

  const removeDefinition = (index: number): void => {
    setFormData((prev: RequirementFormData) => ({
      ...prev,
      definitions: (prev.definitions || []).filter((_: any, i: number) => i !== index),
    }));
  };

  const submitForm = async (): Promise<RequirementResponse> => {
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await requirementsService.create(formData);
      setIsSubmitting(false);
      return response;
    } catch (err: any) { // Type assertion for error handling
      setIsSubmitting(false);
      setError(err.response?.data?.error || 'Failed to submit requirement');
      throw err;
    }
  };

  return {
    formData,
    setField,
    addDefinition,
    removeDefinition,
    submitForm,
    isSubmitting,
    error,
  };
}

// Hook for requirement data operations
export function useRequirement() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Get all requirements
  const getRequirements = async (): Promise<Requirement[]> => {
    setLoading(true);
    setError(null);
    
    try {
      const requirements = await requirementsService.getAll();
      setLoading(false);
      return requirements;
    } catch (err: any) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch requirements';
      setError(errorMessage);
      setLoading(false);
      throw err;
    }
  };

  // Get a specific requirement
  const getRequirement = async (id: string): Promise<Requirement> => {
    setLoading(true);
    setError(null);
    
    try {
      const requirement = await requirementsService.getById(id);
      setLoading(false);
      return requirement;
    } catch (err: any) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch requirement';
      setError(errorMessage);
      setLoading(false);
      throw err;
    }
  };

  // Track requirement status
  const trackRequirementStatus = (
    id: string, 
    onUpdate: (status: any) => void
  ) => {
    return statusService.pollStatus(id, onUpdate);
  };

  return {
    loading,
    error,
    getRequirements,
    getRequirement,
    trackRequirementStatus,
  };
}