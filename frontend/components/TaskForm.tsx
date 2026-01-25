"use client";

import { useState } from "react";
import type { CreateTaskRequest } from "@/lib/types";
import { createTask } from "@/lib/api";

interface TaskFormProps {
  onSuccess?: (data: CreateTaskRequest) => void;
  initialData?: CreateTaskRequest;
  onCancel?: () => void;
  mode?: "create" | "edit";
  taskId?: number;
}

export default function TaskForm({
  onSuccess,
  initialData,
  onCancel,
  mode = "create",
  taskId,
}: TaskFormProps) {
  const [formData, setFormData] = useState<CreateTaskRequest>(
    initialData || { title: "", description: "" }
  );
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "create") {
        await createTask(formData);
      } else if (taskId) {
        // Update task (to be implemented with updateTask API)
        console.log("Update task:", taskId, formData);
      }

      setFormData({ title: "", description: "" });
      onSuccess?.(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          id="title"
          name="title"
          type="text"
          required
          maxLength={200}
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter task title"
        />
        <p className="mt-1 text-xs text-gray-500">
          Maximum 200 characters
        </p>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          rows={3}
          maxLength={1000}
          value={formData.description || ""}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter task description (optional)"
        />
        <p className="mt-1 text-xs text-gray-500">
          Maximum 1000 characters
        </p>
      </div>

      <div>
        <label htmlFor="due_date" className="block text-sm font-medium text-gray-700">
          Due Date
        </label>
        <input
          id="due_date"
          name="due_date"
          type="date"
          value={formData.due_date || ""}
          onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
        <p className="mt-1 text-xs text-gray-500">
          Optional - Select a due date for this task
        </p>
      </div>

      <div>
        <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
          Priority
        </label>
        <select
          id="priority"
          name="priority"
          value={formData.priority || "medium"}
          onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <p className="mt-1 text-xs text-gray-500">
          Select task priority level
        </p>
      </div>

      <div>
        <label htmlFor="category" className="block text-sm font-medium text-gray-700">
          Category
        </label>
        <select
          id="category"
          name="category"
          value={formData.category || ""}
          onChange={(e) => setFormData({ ...formData, category: e.target.value })}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">None</option>
          <option value="personal">Personal</option>
          <option value="work">Work</option>
          <option value="shopping">Shopping</option>
        </select>
        <p className="mt-1 text-xs text-gray-500">
          Optional - Categorize your task
        </p>
      </div>

      <div className="flex space-x-3">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Saving..." : mode === "create" ? "Add Task" : "Update Task"}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
