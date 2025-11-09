import { apiClient } from "./client";
import { Employee, EmployeeCreate, EmployeeUpdate, EmployeeLabel } from "@/types";

export const employeesApi = {
  getAll: async (): Promise<Employee[]> => {
    const response = await apiClient.get<Employee[]>("/api/employees");
    return response.data;
  },

  getById: async (id: string): Promise<Employee> => {
    const response = await apiClient.get<Employee>(`/api/employees/${id}`);
    return response.data;
  },

  create: async (data: EmployeeCreate): Promise<Employee> => {
    const response = await apiClient.post<Employee>("/api/employees", data);
    return response.data;
  },

  update: async (id: string, data: EmployeeUpdate): Promise<Employee> => {
    const response = await apiClient.put<Employee>(`/api/employees/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/employees/${id}`);
  },

  getEmployeeTasks: async (id: string) => {
    const response = await apiClient.get(`/api/employees/${id}/tasks`);
    return response.data;
  },
};

export const labelsApi = {
  getAll: async (): Promise<EmployeeLabel[]> => {
    const response = await apiClient.get<EmployeeLabel[]>("/api/labels");
    return response.data;
  },

  create: async (data: Omit<EmployeeLabel, "id" | "created_at">): Promise<EmployeeLabel> => {
    const response = await apiClient.post<EmployeeLabel>("/api/labels", data);
    return response.data;
  },

  update: async (id: string, data: Partial<Omit<EmployeeLabel, "id" | "created_at">>): Promise<EmployeeLabel> => {
    const response = await apiClient.put<EmployeeLabel>(`/api/labels/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/labels/${id}`);
  },
};
