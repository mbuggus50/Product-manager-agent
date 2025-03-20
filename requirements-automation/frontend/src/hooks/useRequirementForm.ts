import { useState } from 'react';
import requirementsService, { 
  RequirementFormData, 
  RequirementResponse 
} from '../services/requirements.service';

interface UseRequirementFormReturn {
  formData: RequirementFormData;
  setField: (field: keyof RequirementFormData, value: any) => void;
  addDefinition: (attribute: string, definition: string) => void;
  removeDefinition: (index: number) => void;
  submitForm: () => Promise<RequirementResponse>;
  isSubmitting: boolean;
  error: string | null;
}

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
    } catch (err: any) { // Type assertion to any for error handling
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