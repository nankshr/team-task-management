import { apiClient } from "./client";
import { Task, TaskCreate, TaskUpdate, TaskComment, CommentType } from "@/types";

export const tasksApi = {
  getAll: async (params?: {
    status?: string;
    employee_id?: string;
    priority?: string;
    date?: string;
  }): Promise<Task[]> => {
    const response = await apiClient.get<Task[]>("/api/tasks", { params });
    return response.data;
  },

  getById: async (id: string): Promise<Task> => {
    const response = await apiClient.get<Task>(`/api/tasks/${id}`);
    return response.data;
  },

  create: async (data: TaskCreate): Promise<Task> => {
    const response = await apiClient.post<Task>("/api/tasks", data);
    return response.data;
  },

  update: async (id: string, data: TaskUpdate): Promise<Task> => {
    const response = await apiClient.put<Task>(`/api/tasks/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/tasks/${id}`);
  },

  assign: async (id: string, employee_id: string): Promise<Task> => {
    const response = await apiClient.post<Task>(`/api/tasks/${id}/assign`, {
      employee_id,
    });
    return response.data;
  },

  complete: async (id: string): Promise<Task> => {
    const response = await apiClient.post<Task>(`/api/tasks/${id}/complete`);
    return response.data;
  },

  createSubtask: async (id: string, data: TaskCreate): Promise<Task> => {
    const response = await apiClient.post<Task>(`/api/tasks/${id}/subtask`, data);
    return response.data;
  },

  getComments: async (id: string): Promise<TaskComment[]> => {
    const response = await apiClient.get<TaskComment[]>(`/api/tasks/${id}/comments`);
    return response.data;
  },

  addComment: async (
    id: string,
    comment_text: string,
    comment_type: CommentType = CommentType.GENERAL
  ): Promise<TaskComment> => {
    const response = await apiClient.post<TaskComment>(`/api/tasks/${id}/comments`, {
      comment_text,
      comment_type,
    });
    return response.data;
  },

  getOverdue: async (): Promise<Task[]> => {
    const response = await apiClient.get<Task[]>("/api/tasks/overdue");
    return response.data;
  },
};
