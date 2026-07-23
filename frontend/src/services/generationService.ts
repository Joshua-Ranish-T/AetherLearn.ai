import { apiClient } from './api';
import type { GenerationRequest, Job, Video } from '@/types';

export const generationService = {
  async startGeneration(payload: GenerationRequest): Promise<Job> {
    const response = await apiClient.post<Job>('/generate', payload);
    return response.data;
  },

  async getJobStatus(jobId: string): Promise<Job> {
    const response = await apiClient.get<Job>(`/jobs/${jobId}`);
    return response.data;
  },

  getStreamUrl(jobId: string): string {
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/jobs/${jobId}/stream`;
  },
};

export const videoService = {
  async getById(videoId: string): Promise<Video> {
    const response = await apiClient.get<Video>(`/video/${videoId}`);
    return response.data;
  },

  async listAll(limit = 20): Promise<Video[]> {
    const response = await apiClient.get<Video[]>('/videos', { params: { limit } });
    return response.data;
  },

  async getByProject(projectId: string): Promise<Video[]> {
    const response = await apiClient.get<Video[]>(`/project/${projectId}/videos`);
    return response.data;
  },
};
