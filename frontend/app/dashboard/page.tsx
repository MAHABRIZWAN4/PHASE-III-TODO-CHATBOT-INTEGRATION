"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAuthUser, logout, type AuthUser } from "@/lib/auth";
import TaskList from "@/components/TaskList";
import TaskForm from "@/components/TaskForm";
import { useTaskUpdate } from "@/contexts/TaskUpdateContext";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const { triggerTaskRefresh } = useTaskUpdate();

  useEffect(() => {
    // Get user from localStorage on client side only
    const authUser = getAuthUser();
    setUser(authUser);

    if (!authUser) {
      router.replace("/login");
    }
  }, [router]);

  const handleLogout = () => {
    logout();
  };

  const handleTaskAdded = () => {
    setShowAddForm(false);
    // Trigger task refresh instead of full page reload
    triggerTaskRefresh();
  };

  const handleTaskUpdated = () => {
    // Trigger task refresh instead of full page reload
    triggerTaskRefresh();
  };

  // Show loading while checking auth
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-semibold text-gray-900">Todo App</h1>
              <div className="hidden sm:flex space-x-4">
                <a
                  href="/dashboard"
                  className="px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md"
                >
                  Tasks
                </a>
                <a
                  href="/chat"
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
                >
                  Chat
                </a>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                {user.name || user.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">My Tasks</h2>
            <p className="text-sm text-gray-600">Manage your todo items</p>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {showAddForm ? "Cancel" : "+ Add Task"}
          </button>
        </div>

        {/* Add Task Form */}
        {showAddForm && (
          <div className="mb-6 bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Create New Task
            </h3>
            <TaskForm onSuccess={handleTaskAdded} onCancel={() => setShowAddForm(false)} />
          </div>
        )}

        {/* Task List */}
        <div className="bg-white border border-gray-200 rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">All Tasks</h3>
          </div>
          <div className="p-6">
            <TaskList onTaskUpdated={handleTaskUpdated} />
          </div>
        </div>
      </div>
    </div>
  );
}
