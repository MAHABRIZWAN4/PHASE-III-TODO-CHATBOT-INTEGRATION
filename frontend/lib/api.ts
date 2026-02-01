/** Centralized API client with JWT injection */

import { getAuthToken } from "./auth";
import type {
  SignupRequest,
  LoginRequest,
  CreateTaskRequest,
  UpdateTaskRequest,
  AuthResponse,
  Task,
  ApiError,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
}

function getHeaders(): HeadersInit {
  const token = getAuthToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
}

// Authentication endpoints
export async function signup(data: SignupRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  return handleResponse<AuthResponse>(response);
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  return handleResponse<AuthResponse>(response);
}

// Task endpoints
export async function getTasks(): Promise<Task[]> {
  const response = await fetch(`${API_URL}/api/tasks`, {
    headers: getHeaders(),
  });

  return handleResponse<Task[]>(response);
}

export async function createTask(data: CreateTaskRequest): Promise<Task> {
  const response = await fetch(`${API_URL}/api/tasks`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });

  return handleResponse<Task>(response);
}

export async function getTask(id: number): Promise<Task> {
  const response = await fetch(`${API_URL}/api/tasks/${id}`, {
    headers: getHeaders(),
  });

  return handleResponse<Task>(response);
}

export async function updateTask(
  id: number,
  data: UpdateTaskRequest
): Promise<Task> {
  const response = await fetch(`${API_URL}/api/tasks/${id}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });

  return handleResponse<Task>(response);
}

export async function deleteTask(id: number): Promise<void> {
  const response = await fetch(`${API_URL}/api/tasks/${id}`, {
    method: "DELETE",
    headers: getHeaders(),
  });

  // If task is already deleted (404), treat it as success
  // since the desired state (task doesn't exist) is achieved
  if (response.status === 404) {
    console.log('[API] Task already deleted (404), treating as success');
    return;
  }

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || "Request failed");
  }
}

export async function toggleTaskComplete(id: number): Promise<Task> {
  const response = await fetch(`${API_URL}/api/tasks/${id}/complete`, {
    method: "PATCH",
    headers: getHeaders(),
  });

  return handleResponse<Task>(response);
}

// User profile endpoints
export async function updateProfile(data: { name?: string; email?: string }): Promise<{ id: string; email: string; name?: string; created_at: string }> {
  const response = await fetch(`${API_URL}/api/auth/profile`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });

  return handleResponse(response);
}

export async function changePassword(data: { current_password: string; new_password: string }): Promise<{ message: string }> {
  const response = await fetch(`${API_URL}/api/auth/change-password`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });

  return handleResponse(response);
}
