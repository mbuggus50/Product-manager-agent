import api from './api';

// Types
export interface RequirementStep {
  name: string;
  status: string;
  start_time?: string;
  end_time?: string;
  details?: any;
  error?: string;
}

export interface RequirementStatus {
  id: string;
  status: string;
  steps: RequirementStep[];
  links: Record<string, string>;
  created_at: string;
  updated_at: string;
  current_node?: string;
}

// Status service for a specific requirement
export const statusService = {
  // Get status for a specific requirement
  getRequirementStatus: async (requirementId: string): Promise<RequirementStatus> => {
    return await api.get<RequirementStatus>(`/api/requirements/${requirementId}/status`);
  },
  
  // Poll status for a specific requirement
  pollStatus: (requirementId: string, callback: (status: RequirementStatus) => void, interval = 5000) => {
    const intervalId = setInterval(async () => {
      try {
        const status = await statusService.getRequirementStatus(requirementId);
        callback(status);
        
        // If the status is 'completed' or 'failed', stop polling
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(intervalId);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        clearInterval(intervalId);
      }
    }, interval);
    
    // Return function to stop polling
    return () => clearInterval(intervalId);
  }
};

export default statusService;