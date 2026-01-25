"use client";

import { useState, useEffect, useCallback } from "react";
import type { Task } from "@/lib/types";
import { getTasks, toggleTaskComplete } from "@/lib/api";
import TaskItem from "./TaskItem";
import { useTaskUpdate } from "@/contexts/TaskUpdateContext";

interface TaskListProps {
  onTaskUpdated?: () => void;
}

export default function TaskList({ onTaskUpdated }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { onTaskRefresh } = useTaskUpdate();

  console.log('[TaskList] Component rendered with', tasks.length, 'tasks');

  useEffect(() => {
    console.log('[TaskList] Initial mount - fetching tasks');
    fetchTasks();
  }, []);

  // Listen for task updates from chat
  useEffect(() => {
    console.log('[TaskList] Setting up task refresh listener');
    const cleanup = onTaskRefresh(() => {
      console.log('[TaskList] Task refresh triggered! Fetching tasks...');
      fetchTasks();
    });

    return cleanup;
  }, [onTaskRefresh]);

  // Log whenever tasks state changes
  useEffect(() => {
    console.log('[TaskList] Tasks state changed! New count:', tasks.length);
    console.log('[TaskList] Task IDs in state:', tasks.map(t => t.id));
  }, [tasks]);

  const fetchTasks = useCallback(async () => {
    try {
      const timestamp = new Date().toISOString();
      console.log(`[TaskList ${timestamp}] fetchTasks called - Starting fetch...`);
      console.log(`[TaskList ${timestamp}] Current tasks count:`, tasks.length);

      setLoading(true);
      const data = await getTasks();

      console.log(`[TaskList ${timestamp}] Fetched tasks:`, data.length, 'tasks');
      console.log(`[TaskList ${timestamp}] Task IDs:`, data.map(t => t.id));

      setTasks(data);
      console.log(`[TaskList ${timestamp}] State updated with new tasks`);

      setError("");
    } catch (err) {
      console.error('[TaskList] Error fetching tasks:', err);
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
      console.log(`[TaskList] fetchTasks completed`);
    }
  }, [tasks.length]); // Only recreate if tasks count changes

  const handleToggleComplete = async (taskId: number) => {
    try {
      // Optimistic update
      setTasks(tasks.map(task =>
        task.id === taskId ? { ...task, completed: !task.completed } : task
      ));

      await toggleTaskComplete(taskId);

      onTaskUpdated?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update task");
      // Revert on error
      fetchTasks();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 012 2v2a2 2 0 012 2h10a2 2 0 012-2V7a2 2 0 00-2-2H9z"
          />
        </svg>
        <h3 className="mt-4 text-lg font-medium text-gray-900">No tasks yet</h3>
        <p className="mt-2 text-sm text-gray-600">
          Create your first task to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggleComplete={handleToggleComplete}
          onTaskUpdated={fetchTasks}
        />
      ))}
    </div>
  );
}
