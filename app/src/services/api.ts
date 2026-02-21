const API_BASE_URL = 'http://localhost:8000';

export interface TaskStatus {
  task_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  result_url?: string;
  mesh_url?: string;
  error?: string;
}

export interface GenerationResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface HealthStatus {
  status: string;
  triposr_initialized: boolean;
  blender_available: boolean;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async healthCheck(): Promise<HealthStatus> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error('Failed to check API health');
    }
    return response.json();
  }

  async uploadImage(file: File): Promise<GenerationResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/generate/image-to-ugc`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || 'Failed to upload image');
    }

    return response.json();
  }

  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await fetch(`${this.baseUrl}/task/${taskId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get task status');
    }

    return response.json();
  }

  getDownloadUrl(taskId: string, format: string = 'fbx'): string {
    return `${this.baseUrl}/download/${taskId}?format=${format}`;
  }

  async downloadResult(taskId: string, format: string = 'fbx'): Promise<Blob> {
    const response = await fetch(this.getDownloadUrl(taskId, format));
    
    if (!response.ok) {
      throw new Error('Failed to download result');
    }

    return response.blob();
  }
}

export const api = new ApiService();
export default api;
