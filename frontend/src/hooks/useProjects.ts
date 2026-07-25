import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsService } from '@/services/projectsService';
import { generationService } from '@/services/generationService';
import type { ProjectCreate, GenerationRequest } from '@/types';
import toast from 'react-hot-toast';

// Query keys
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  detail: (id: string) => [...projectKeys.all, 'detail', id] as const,
};

export const jobKeys = {
  all: ['jobs'] as const,
  detail: (id: string) => [...jobKeys.all, id] as const,
};

// Hooks
export function useProjects(limit = 20, offset = 0) {
  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: () => projectsService.list(limit, offset),
    staleTime: 30_000,
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: projectKeys.detail(id),
    queryFn: () => projectsService.getById(id),
    enabled: !!id,
    staleTime: 10_000,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProjectCreate) => projectsService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      toast.success('Project created!');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });
}

export function useCreateProjectWithFile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) => projectsService.createWithFile(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      toast.success('Project created with file!');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => projectsService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      toast.success('Project deleted');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });
}

export function useStartGeneration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: GenerationRequest) => generationService.startGeneration(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });
}

export function useJobStatus(jobId: string | null) {
  return useQuery({
    queryKey: jobKeys.detail(jobId!),
    queryFn: () => generationService.getJobStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'running' || status === 'pending' ? 1000 : false;
    },
  });
}

