"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getAuthUser, logout, type AuthUser } from "@/lib/auth";
import { getTasks } from "@/lib/api";
import type { Task } from "@/lib/types";
import TaskList from "@/components/TaskList";
import TaskForm from "@/components/TaskForm";
import { useTaskUpdate } from "@/contexts/TaskUpdateContext";
import {
  Brain,
  LayoutDashboard,
  CheckSquare,
  MessageSquare,
  Settings,
  User,
  LogOut,
  Plus,
  Search,
  Bell,
  Moon,
  Sun,
  Menu,
  X
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Avatar } from "@/components/ui/Avatar";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { SpinnerFullPage } from "@/components/ui/Spinner";

interface TaskStats {
  total: number;
  completed: number;
  pending: number;
  overdue: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [stats, setStats] = useState<TaskStats>({ total: 0, completed: 0, pending: 0, overdue: 0 });
  const [loadingStats, setLoadingStats] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [overdueTasks, setOverdueTasks] = useState<Task[]>([]);
  const { triggerTaskRefresh, refreshTrigger } = useTaskUpdate();

  useEffect(() => {
    // Get user from localStorage on client side only
    console.log('[Dashboard] Checking auth...');
    const authUser = getAuthUser();
    console.log('[Dashboard] Auth user:', authUser ? 'Found' : 'Not found');
    setUser(authUser);

    if (!authUser) {
      console.log('[Dashboard] No user, redirecting to login...');
      router.replace("/login");
      return;
    }

    // Check for dark mode preference
    const isDark = localStorage.getItem("darkMode") === "true";
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add("dark");
    }
  }, [router]);

  // Fetch and calculate task stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoadingStats(true);
        console.log('[Dashboard] Fetching tasks...');
        const tasks = await getTasks();
        console.log('[Dashboard] Tasks fetched:', tasks.length);

        const now = new Date();
        const total = tasks.length;
        const completed = tasks.filter(t => t.completed).length;
        const pending = tasks.filter(t => !t.completed).length;

        // Find overdue tasks
        const overdueTasksList = tasks.filter(t => {
          if (t.completed || !t.due_date) return false;
          const dueDate = new Date(t.due_date);
          return dueDate < now;
        });

        setOverdueTasks(overdueTasksList);
        setStats({ total, completed, pending, overdue: overdueTasksList.length });
        console.log('[Dashboard] Stats updated:', { total, completed, pending, overdue: overdueTasksList.length });
      } catch (error) {
        console.error("[Dashboard] Failed to fetch task stats:", error);
        // Set default stats on error so page doesn't hang
        setStats({ total: 0, completed: 0, pending: 0, overdue: 0 });
        setOverdueTasks([]);
      } finally {
        setLoadingStats(false);
      }
    };

    if (user) {
      fetchStats();
    }
  }, [user, refreshTrigger]);

  const handleLogout = () => {
    logout();
  };

  const handleTaskAdded = () => {
    setShowAddForm(false);
    triggerTaskRefresh();
  };

  const handleTaskUpdated = () => {
    triggerTaskRefresh();
  };

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem("darkMode", String(newDarkMode));
    if (newDarkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  // Show loading while checking auth
  if (!user) {
    return <SpinnerFullPage />;
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900 flex">
      {/* Sidebar - Desktop */}
      <aside className="hidden lg:flex lg:flex-col lg:w-64 bg-white dark:bg-neutral-800 border-r border-neutral-200 dark:border-neutral-700">
        {/* Logo */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-neutral-200 dark:border-neutral-700">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-xl flex items-center justify-center">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold text-gradient">TaskAI</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          <Link
            href="/dashboard"
            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg transition-all"
          >
            <LayoutDashboard className="w-5 h-5" />
            Dashboard
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-all"
          >
            <CheckSquare className="w-5 h-5" />
            All Tasks
          </Link>
          <Link
            href="/chat"
            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-all"
          >
            <MessageSquare className="w-5 h-5" />
            AI Assistant
          </Link>
          <Link
            href="/settings"
            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-all"
          >
            <Settings className="w-5 h-5" />
            Settings
          </Link>
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-neutral-200 dark:border-neutral-700">
          <div className="flex items-center gap-3 px-3 py-2">
            <Avatar name={user.name || user.email} size="md" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-neutral-900 dark:text-white truncate">
                {user.name || "User"}
              </p>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate">
                {user.email}
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-neutral-800 border-r border-neutral-200 dark:border-neutral-700 transform transition-transform duration-300 lg:hidden ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-neutral-200 dark:border-neutral-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gradient">TaskAI</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          <Link
            href="/dashboard"
            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg"
            onClick={() => setSidebarOpen(false)}
          >
            <LayoutDashboard className="w-5 h-5" />
            Dashboard
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg"
            onClick={() => setSidebarOpen(false)}
          >
            <CheckSquare className="w-5 h-5" />
            All Tasks
          </Link>
          <Link
            href="/chat"
            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg"
            onClick={() => setSidebarOpen(false)}
          >
            <MessageSquare className="w-5 h-5" />
            AI Assistant
          </Link>
          <Link
            href="/settings"
            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg"
            onClick={() => setSidebarOpen(false)}
          >
            <Settings className="w-5 h-5" />
            Settings
          </Link>
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-neutral-200 dark:border-neutral-700">
          <div className="flex items-center gap-3 px-3 py-2">
            <Avatar name={user.name || user.email} size="md" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-neutral-900 dark:text-white truncate">
                {user.name || "User"}
              </p>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate">
                {user.email}
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 flex items-center justify-between px-4 lg:px-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
            >
              <Menu className="w-6 h-6" />
            </button>
            <h1 className="text-xl font-semibold text-neutral-900 dark:text-white">
              Dashboard
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleDarkMode}
              className="p-2 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors relative"
                aria-label="Notifications"
              >
                <Bell className="w-5 h-5" />
                {stats.overdue > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                )}
              </button>

              {/* Notification Dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-neutral-800 rounded-xl shadow-xl border border-neutral-200 dark:border-neutral-700 z-50 animate-scale-in">
                  <div className="p-4 border-b border-neutral-200 dark:border-neutral-700">
                    <h3 className="text-sm font-semibold text-neutral-900 dark:text-white">
                      Notifications
                    </h3>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {overdueTasks.length > 0 ? (
                      <div className="p-2">
                        {overdueTasks.map((task) => (
                          <div
                            key={task.id}
                            className="p-3 mb-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
                          >
                            <div className="flex items-start gap-2">
                              <div className="flex-shrink-0 mt-0.5">
                                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-neutral-900 dark:text-white truncate">
                                  {task.title}
                                </p>
                                <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                                  Overdue: {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-8 text-center">
                        <Bell className="w-12 h-12 text-neutral-300 dark:text-neutral-600 mx-auto mb-3" />
                        <p className="text-sm text-neutral-600 dark:text-neutral-400">
                          No notifications
                        </p>
                        <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
                          You're all caught up!
                        </p>
                      </div>
                    )}
                  </div>
                  {overdueTasks.length > 0 && (
                    <div className="p-3 border-t border-neutral-200 dark:border-neutral-700">
                      <button
                        onClick={() => setShowNotifications(false)}
                        className="w-full text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
                      >
                        Close
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
            <button
              onClick={handleLogout}
              className="hidden sm:flex items-center gap-2 px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto p-4 lg:p-8">
          {/* Quick Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <Card variant="elevated" className="hover:shadow-xl transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                      Total Tasks
                    </p>
                    <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">
                      {loadingStats ? "..." : stats.total}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-xl flex items-center justify-center">
                    <CheckSquare className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card variant="elevated" className="hover:shadow-xl transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                      Completed
                    </p>
                    <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">
                      {loadingStats ? "..." : stats.completed}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-xl flex items-center justify-center">
                    <CheckSquare className="w-6 h-6 text-green-600 dark:text-green-400" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card variant="elevated" className="hover:shadow-xl transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                      Pending
                    </p>
                    <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">
                      {loadingStats ? "..." : stats.pending}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-amber-100 dark:bg-amber-900 rounded-xl flex items-center justify-center">
                    <CheckSquare className="w-6 h-6 text-amber-600 dark:text-amber-400" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card variant="elevated" className="hover:shadow-xl transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                      Overdue
                    </p>
                    <p className="text-3xl font-bold text-neutral-900 dark:text-white mt-2">
                      {loadingStats ? "..." : stats.overdue}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-red-100 dark:bg-red-900 rounded-xl flex items-center justify-center">
                    <CheckSquare className="w-6 h-6 text-red-600 dark:text-red-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Task Management Section */}
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h2 className="text-2xl font-bold text-neutral-900 dark:text-white">
                  My Tasks
                </h2>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                  Manage and organize your tasks
                </p>
              </div>
              <Button
                variant="primary"
                size="md"
                onClick={() => setShowAddForm(!showAddForm)}
                className="w-full sm:w-auto"
              >
                <Plus className="w-5 h-5" />
                {showAddForm ? "Cancel" : "Add Task"}
              </Button>
            </div>

            {/* Add Task Form */}
            {showAddForm && (
              <Card variant="elevated" className="animate-slide-down">
                <CardHeader>
                  <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
                    Create New Task
                  </h3>
                </CardHeader>
                <CardContent>
                  <TaskForm
                    onSuccess={handleTaskAdded}
                    onCancel={() => setShowAddForm(false)}
                  />
                </CardContent>
              </Card>
            )}

            {/* Task List */}
            <Card variant="elevated">
              <CardHeader className="flex flex-row items-center justify-between">
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
                  All Tasks
                </h3>
                <Badge variant="primary">{stats.total} tasks</Badge>
              </CardHeader>
              <CardContent>
                <TaskList onTaskUpdated={handleTaskUpdated} />
              </CardContent>
            </Card>
          </div>
        </main>
      </div>

      {/* Floating Action Button (Mobile) */}
      <button
        onClick={() => setShowAddForm(!showAddForm)}
        className="lg:hidden fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-primary-600 to-secondary-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-110 active:scale-95 flex items-center justify-center z-30"
        aria-label="Add task"
      >
        {showAddForm ? <X className="w-6 h-6" /> : <Plus className="w-6 h-6" />}
      </button>
    </div>
  );
}
