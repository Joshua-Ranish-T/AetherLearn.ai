import { apiClient } from './api';
import type { Project, ProjectCreate, ProjectListResponse } from '@/types';

export const projectsService = {
  async create(data: ProjectCreate): Promise<Project> {
    const response = await apiClient.post<Project>('/projects', data);
    return response.data;
  },

  async createWithFile(formData: FormData): Promise<Project> {
    const response = await apiClient.post<Project>('/projects/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async list(limit = 20, offset = 0): Promise<ProjectListResponse> {
    const response = await apiClient.get<ProjectListResponse>('/projects', {
      params: { limit, offset },
    });
    return response.data;
  },

  async getById(id: string): Promise<Project> {
    const response = await apiClient.get<Project>(`/projects/${id}`);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/projects/${id}`);
  },
};
