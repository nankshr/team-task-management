"use client";

import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, ClipboardList, CheckCircle, AlertCircle } from "lucide-react";
import Link from "next/link";
import { TaskStatus, TaskPriority } from "@/types";

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: dashboardApi.getStats,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const attendance = stats?.attendance || {
    today_present: 0,
    today_absent: 0,
    total_employees: 0,
    not_marked: 0,
  };

  const tasks = stats?.tasks || {
    pending: 0,
    in_progress: 0,
    completed: 0,
    overdue: 0,
  };

  const recentTasks = stats?.recent_tasks || [];

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return "text-green-600 bg-green-50";
      case TaskStatus.IN_PROGRESS:
        return "text-blue-600 bg-blue-50";
      case TaskStatus.OVERDUE:
        return "text-red-600 bg-red-50";
      case TaskStatus.BLOCKED:
        return "text-orange-600 bg-orange-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.URGENT:
        return "text-red-600";
      case TaskPriority.HIGH:
        return "text-orange-600";
      case TaskPriority.MEDIUM:
        return "text-yellow-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">
          Overview of your team's attendance and tasks
        </p>
      </div>

      {/* Attendance Overview */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-3">
          Today's Attendance
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Employees
              </CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {attendance.total_employees}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Active employees
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Present</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {attendance.today_present}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Marked as present
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Absent</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {attendance.today_absent}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Marked as absent
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Not Marked</CardTitle>
              <AlertCircle className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {attendance.not_marked}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Pending attendance
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Task Overview */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-3">
          Task Overview
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <ClipboardList className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{tasks.pending}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Not yet started
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">In Progress</CardTitle>
              <ClipboardList className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {tasks.in_progress}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Currently being worked on
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {tasks.completed}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Successfully finished
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overdue</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {tasks.overdue}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Past due date
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Recent Tasks */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-800">Recent Tasks</h2>
          <Link
            href="/dashboard/tasks"
            className="text-sm text-primary hover:underline"
          >
            View all tasks →
          </Link>
        </div>

        <Card>
          <CardContent className="p-0">
            {recentTasks.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No tasks found. Create your first task!
              </div>
            ) : (
              <div className="divide-y">
                {recentTasks.map((task: any) => (
                  <div
                    key={task.id}
                    className="p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium text-gray-900">
                            {task.title}
                          </h3>
                          <span
                            className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                              task.status
                            )}`}
                          >
                            {task.status.replace("_", " ").toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          {task.description || "No description"}
                        </p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span>Task #{task.task_number}</span>
                          <span
                            className={`font-medium ${getPriorityColor(
                              task.priority
                            )}`}
                          >
                            {task.priority.toUpperCase()} Priority
                          </span>
                          <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
