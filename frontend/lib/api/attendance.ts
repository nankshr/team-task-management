import { apiClient } from "./client";
import { Attendance, AttendanceSummary, AttendanceStatus } from "@/types";

export const attendanceApi = {
  getToday: async (): Promise<AttendanceSummary> => {
    const response = await apiClient.get<AttendanceSummary>("/api/attendance/today");
    return response.data;
  },

  getHistory: async (params?: {
    start_date?: string;
    end_date?: string;
    employee_id?: string;
  }): Promise<Attendance[]> => {
    const response = await apiClient.get<Attendance[]>("/api/attendance", { params });
    return response.data;
  },

  mark: async (employee_id: string, status: AttendanceStatus, date?: string): Promise<Attendance> => {
    const response = await apiClient.post<Attendance>("/api/attendance/mark", {
      employee_id,
      status,
      date,
    });
    return response.data;
  },

  getReport: async (params?: {
    start_date?: string;
    end_date?: string;
    employee_id?: string;
  }) => {
    const response = await apiClient.get("/api/attendance/report", { params });
    return response.data;
  },
};
