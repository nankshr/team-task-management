// User types
export enum UserRole {
  OWNER = "owner",
  ADMIN = "admin",
  EMPLOYEE = "employee",
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Employee types
export interface EmployeeLabel {
  id: string;
  name: string;
  color?: string;
  created_at: string;
}

export interface Employee {
  id: string;
  user_id?: string;
  name: string;
  phone?: string;
  telegram_user_id?: number;
  telegram_username?: string;
  is_active: boolean;
  labels: EmployeeLabel[];
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreate {
  name: string;
  phone?: string;
  telegram_user_id?: number;
  telegram_username?: string;
  is_active?: boolean;
  label_ids?: string[];
}

export interface EmployeeUpdate {
  name?: string;
  phone?: string;
  telegram_user_id?: number;
  telegram_username?: string;
  is_active?: boolean;
  label_ids?: string[];
}

// Attendance types
export enum AttendanceStatus {
  PRESENT = "present",
  ABSENT = "absent",
  HALF_DAY = "half_day",
  ON_LEAVE = "on_leave",
}

export interface Attendance {
  id: string;
  employee_id: string;
  date: string;
  status: AttendanceStatus;
  marked_at?: string;
  auto_marked: boolean;
  employee: Employee;
}

export interface AttendanceSummary {
  date: string;
  total_employees: number;
  present: number;
  absent: number;
  half_day: number;
  on_leave: number;
  not_marked: number;
}

// Task types
export enum TaskType {
  ROUTINE = "routine",
  ONE_TIME = "one_time",
}

export enum TaskPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  URGENT = "urgent",
}

export enum TaskStatus {
  PENDING = "pending",
  ASSIGNED = "assigned",
  IN_PROGRESS = "in_progress",
  BLOCKED = "blocked",
  COMPLETED = "completed",
  OVERDUE = "overdue",
}

export enum CommentType {
  GENERAL = "general",
  ISSUE_REPORT = "issue_report",
  CLARIFICATION = "clarification",
}

export interface TaskComment {
  id: string;
  task_id: string;
  comment_by_employee_id?: string;
  comment_by_user_id?: string;
  comment_text: string;
  comment_type: CommentType;
  created_at: string;
  employee?: Employee;
  user?: User;
}

export interface Task {
  id: string;
  task_number: string;
  title: string;
  description?: string;
  task_type: TaskType;
  priority: TaskPriority;
  status: TaskStatus;
  due_date: string;
  due_time?: string;
  assigned_to?: string;
  assigned_by?: string;
  created_by?: string;
  parent_task_id?: string;
  is_subtask: boolean;
  telegram_message_id?: number;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  assigned_employee?: Employee;
  assigner?: User;
  creator?: User;
  parent_task?: Task;
  subtasks?: Task[];
  comments?: TaskComment[];
  labels?: EmployeeLabel[];
}

export interface TaskCreate {
  title: string;
  description?: string;
  task_type?: TaskType;
  priority?: TaskPriority;
  due_date: string;
  due_time?: string;
  assigned_to?: string;
  label_ids?: string[];
  parent_task_id?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  status?: TaskStatus;
  due_date?: string;
  due_time?: string;
  assigned_to?: string;
  label_ids?: string[];
}

// Routine types
export enum RecurrenceType {
  DAILY = "daily",
  WEEKLY = "weekly",
  MONTHLY = "monthly",
}

export interface Routine {
  id: string;
  title: string;
  description?: string;
  recurrence_type: RecurrenceType;
  recurrence_time: string;
  recurrence_day?: number;
  is_active: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
  creator?: User;
  labels?: EmployeeLabel[];
}

export interface RoutineCreate {
  title: string;
  description?: string;
  recurrence_type: RecurrenceType;
  recurrence_time: string;
  recurrence_day?: number;
  is_active?: boolean;
  label_ids?: string[];
}

export interface RoutineUpdate {
  title?: string;
  description?: string;
  recurrence_type?: RecurrenceType;
  recurrence_time?: string;
  recurrence_day?: number;
  is_active?: boolean;
  label_ids?: string[];
}

// Dashboard types
export interface DashboardStats {
  attendance: {
    today_present: number;
    today_absent: number;
    total_employees: number;
    not_marked: number;
  };
  tasks: {
    pending: number;
    in_progress: number;
    completed: number;
    overdue: number;
  };
  recent_tasks: Task[];
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
}
