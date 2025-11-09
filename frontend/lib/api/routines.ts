import { apiClient } from "./client";
import { Routine, RoutineCreate, RoutineUpdate } from "@/types";

export const routinesApi = {
  getAll: async (): Promise<Routine[]> => {
    const response = await apiClient.get<Routine[]>("/api/routines");
    return response.data;
  },

  getById: async (id: string): Promise<Routine> => {
    const response = await apiClient.get<Routine>(`/api/routines/${id}`);
    return response.data;
  },

  create: async (data: RoutineCreate): Promise<Routine> => {
    const response = await apiClient.post<Routine>("/api/routines", data);
    return response.data;
  },

  update: async (id: string, data: RoutineUpdate): Promise<Routine> => {
    const response = await apiClient.put<Routine>(`/api/routines/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/routines/${id}`);
  },

  generateTasks: async (id: string): Promise<void> => {
    await apiClient.post(`/api/routines/${id}/generate`);
  },
};
