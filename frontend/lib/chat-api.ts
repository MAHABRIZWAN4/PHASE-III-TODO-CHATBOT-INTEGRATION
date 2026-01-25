/** Chat API client for AI-powered todo chatbot */

import { getAuthToken, getAuthUser } from "./auth";
import type { ChatRequest, ChatResponse, Message, ApiError } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      detail: "Request failed",
      status: response.status,
    }));
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

/**
 * Send a chat message to the AI assistant
 * @param message - The user's message text
 * @param conversationId - Optional conversation ID (UUID) to continue an existing conversation
 * @returns ChatResponse with the assistant's reply and conversation ID
 * @throws Error if user is not authenticated or request fails
 */
export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const user = getAuthUser();
  if (!user) {
    throw new Error("User not authenticated");
  }

  const requestBody: ChatRequest = {
    message,
    ...(conversationId && { conversation_id: conversationId }),
  };

  const response = await fetch(`${API_URL}/api/${user.id}/chat`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(requestBody),
  });

  return handleResponse<ChatResponse>(response);
}

/**
 * Get all conversations for the current user
 * @returns Array of conversations
 * @throws Error if user is not authenticated or request fails
 */
export async function getConversations(): Promise<any[]> {
  const user = getAuthUser();
  if (!user) {
    throw new Error("User not authenticated");
  }

  const response = await fetch(`${API_URL}/api/${user.id}/conversations`, {
    headers: getHeaders(),
  });

  return handleResponse<any[]>(response);
}

/**
 * Get all messages for a specific conversation
 * @param conversationId - The conversation ID (UUID)
 * @returns Array of messages
 * @throws Error if user is not authenticated or request fails
 */
export async function getConversationMessages(
  conversationId: string
): Promise<Message[]> {
  const user = getAuthUser();
  if (!user) {
    throw new Error("User not authenticated");
  }

  const response = await fetch(
    `${API_URL}/api/${user.id}/conversations/${conversationId}/messages`,
    {
      headers: getHeaders(),
    }
  );

  return handleResponse<Message[]>(response);
}
