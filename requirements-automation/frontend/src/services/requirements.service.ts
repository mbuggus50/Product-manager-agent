import api from './api';

// Types
export interface Requirement {
  id: string;
  title: string;
  description: string;
  status: string;
  businessNeed: string;
  requirements: string;
  businessImpact?: string;
  deliveryDate?: string;
  campaignDate?: string;
  business_need?: string; // For backward compatibility
  business_impact?: string; // For backward compatibility
  delivery_date?: string; // For backward compatibility
  campaign_date?: string; // For backward compatibility
  priority?: string;
  owner?: string;
  created_at: string;
  updated_at: string;
  steps?: Array<{
    name: string;
    status: string;
    start_time?: string;
    end_time?: string;
    details?: any;
    error?: string;
  }>;
  document_links?: Record<string, string>;
  feedback?: Array<{
    id: string;
    type: string;
    message: string;
    timestamp: string;
  }>;
  current_node?: string;
  contributors?: string[]; // For backward compatibility
  definitions?: Array<{attribute: string, definition: string}>; // For backward compatibility
}

// Form data structure
export interface RequirementFormData {
  businessNeed: string;
  requirements: string;
  businessImpact?: string;
  deliveryDate?: string;
  campaignDate?: string;
  definitions?: Array<{attribute: string, definition: string}>;
  [key: string]: any; // Allow additional properties for flexibility
}

export interface CreateRequirementRequest {
  businessNeed: string;
  requirements: string;
  businessImpact?: string;
  deliveryDate?: string;
  campaignDate?: string;
}

export interface CreateRequirementResponse {
  success: boolean;
  message: string;
  requirement: Requirement;
}

// Alias for backward compatibility
export type RequirementResponse = CreateRequirementResponse;

export interface RequirementsListResponse {
  requirements: Requirement[];
}

export interface RequirementStatusResponse {
  id: string;
  status: string;
  steps: Array<{
    name: string;
    status: string;
    start_time?: string;
    end_time?: string;
    details?: any;
    error?: string;
  }>;
  links: Record<string, string>;
  created_at: string;
  updated_at: string;
  current_node?: string;
}

export interface GenerateResponse {
  success: boolean;
  message: string;
  requirement: Requirement;
}

// Requirements service
const requirementsService = {
  // Get all requirements - both new and legacy methods
  getAll: async (): Promise<Requirement[]> => {
    const response = await api.get<RequirementsListResponse>('/api/requirements');
    return response.requirements;
  },
  
  getRequirements: async (): Promise<Requirement[]> => {
    const response = await api.get<RequirementsListResponse>('/api/requirements');
    return response.requirements;
  },
  
  // Get a requirement by ID - both new and legacy methods
  getById: async (id: string): Promise<Requirement> => {
    return await api.get<Requirement>(`/api/requirements/${id}`);
  },
  
  getRequirement: async (id: string): Promise<Requirement> => {
    return await api.get<Requirement>(`/api/requirements/${id}`);
  },
  
  // Create a new requirement - both new and legacy methods
  create: async (data: RequirementFormData): Promise<CreateRequirementResponse> => {
    return await api.post<CreateRequirementResponse>('/api/requirements', data);
  },
  
  createRequirement: async (data: RequirementFormData): Promise<RequirementResponse> => {
    return await api.post<RequirementResponse>('/api/requirements', data);
  },
  
  // Get requirement status - both new and legacy methods
  getStatus: async (id: string): Promise<RequirementStatusResponse> => {
    return await api.get<RequirementStatusResponse>(`/api/requirements/${id}/status`);
  },
  
  getRequirementStatus: async (id: string): Promise<RequirementStatusResponse> => {
    return await api.get<RequirementStatusResponse>(`/api/requirements/${id}/status`);
  },
  
  // Generate requirement using AI
  generate: async (id: string): Promise<GenerateResponse> => {
    return await api.post<GenerateResponse>(`/api/requirements/${id}/generate`);
  }
};

export default requirementsService;