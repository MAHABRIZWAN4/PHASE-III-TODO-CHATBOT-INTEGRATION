"use client";

import { useState, useEffect, useRef } from "react";
import type { Message } from "@/lib/types";
import { sendChatMessage } from "@/lib/chat-api";
import MessageBubble from "./MessageBubble";
import { useTaskUpdate } from "@/contexts/TaskUpdateContext";

interface ChatInterfaceProps {
  conversationId?: string;
  onConversationCreated?: (conversationId: string) => void;
}

/**
 * ChatInterface component provides the main chat UI
 * Integrates with OpenAI ChatKit for AI-powered conversations
 */
export default function ChatInterface({
  conversationId,
  onConversationCreated,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentConversationId, setCurrentConversationId] = useState<
    string | undefined
  >(conversationId);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { triggerTaskRefresh } = useTaskUpdate();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Update conversation ID when prop changes
  useEffect(() => {
    setCurrentConversationId(conversationId);
  }, [conversationId]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim() || loading) {
      return;
    }

    const userMessageContent = inputMessage.trim();
    setInputMessage("");
    setError("");
    setLoading(true);

    // Optimistically add user message to UI
    const tempId = `temp-${Date.now()}`;
    const tempUserMessage: Message = {
      id: tempId,
      conversation_id: currentConversationId || "",
      role: "user",
      content: userMessageContent,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMessage]);

    try {
      const response = await sendChatMessage(
        userMessageContent,
        currentConversationId
      );

      // Update conversation ID if this is a new conversation
      if (!currentConversationId && response.conversation_id) {
        setCurrentConversationId(response.conversation_id);
        onConversationCreated?.(response.conversation_id);
      }

      // Check if a task was added successfully and trigger refresh
      if (response.metadata?.tool_calls) {
        console.log('[ChatInterface] Tool calls received:', response.metadata.tool_calls);
        const taskAdded = response.metadata.tool_calls.some(
          (call) => call.tool === "add_task" && call.success
        );
        console.log('[ChatInterface] Task added:', taskAdded);
        if (taskAdded) {
          // Trigger task refresh to update dashboard
          console.log('[ChatInterface] Triggering task refresh...');
          triggerTaskRefresh();
        }
      } else {
        console.log('[ChatInterface] No metadata or tool_calls in response');
      }

      // Replace temp user message and add assistant message
      setMessages((prev) => {
        const withoutTemp = prev.filter((msg) => msg.id !== tempId);
        return [
          ...withoutTemp,
          {
            ...tempUserMessage,
            id: `user-${Date.now()}`, // Temporary user message ID
            conversation_id: response.conversation_id,
          },
          {
            id: response.message_id, // Use the actual message ID from backend
            conversation_id: response.conversation_id,
            role: "assistant" as const,
            content: response.response,
            created_at: new Date().toISOString(),
          },
        ];
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove optimistic user message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== tempId));
      // Restore input message
      setInputMessage(userMessageContent);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as any);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Error Banner */}
      {error && (
        <div
          className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4"
          role="alert"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm">{error}</span>
            <button
              onClick={() => setError("")}
              className="text-red-600 hover:text-red-800"
              aria-label="Dismiss error"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <svg
              className="h-16 w-16 text-gray-400 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start a conversation
            </h3>
            <p className="text-sm text-gray-600 max-w-md">
              Ask me to create tasks, list your todos, mark items as complete,
              or anything else you need help with!
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 border border-gray-200 rounded-lg px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="border-t border-gray-200 bg-white px-4 py-4">
        <form onSubmit={handleSendMessage} className="flex space-x-4">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Shift+Enter for new line)"
            className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={1}
            disabled={loading}
            aria-label="Message input"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Send message"
          >
            {loading ? (
              <svg
                className="animate-spin h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            ) : (
              <svg
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
