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

      // Check if any task operation was successful and trigger refresh
      if (response.metadata?.tool_calls) {
        console.log('[ChatInterface] Tool calls received:', response.metadata.tool_calls);
        console.log('[ChatInterface] Full response metadata:', response.metadata);

        const taskModified = response.metadata.tool_calls.some(
          (call: any) =>
            (call.tool === "add_task" ||
             call.tool === "complete_task" ||
             call.tool === "delete_task" ||
             call.tool === "update_task") &&
            call.success === true
        );
        console.log('[ChatInterface] Task modified:', taskModified);

        if (taskModified) {
          // Trigger task refresh to update dashboard
          console.log('[ChatInterface] Triggering task refresh...');
          triggerTaskRefresh();
          console.log('[ChatInterface] Task refresh triggered!');
        }
      } else {
        console.log('[ChatInterface] No metadata or tool_calls in response');
        console.log('[ChatInterface] Full response:', response);
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
          className="mx-4 mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-xl animate-slide-down"
          role="alert"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">{error}</span>
            <button
              onClick={() => setError("")}
              className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors"
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
          <div className="flex flex-col items-center justify-center h-full text-center px-4 animate-fade-in">
            <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-secondary-100 dark:from-primary-900 dark:to-secondary-900 rounded-2xl flex items-center justify-center mb-6">
              <svg
                className="h-10 w-10 text-primary-600 dark:text-primary-400"
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
            </div>
            <h3 className="text-2xl font-bold text-neutral-900 dark:text-white mb-3">
              Welcome to your AI Assistant
            </h3>
            <p className="text-base text-neutral-600 dark:text-neutral-400 max-w-md mb-8">
              I can help you manage your tasks through natural conversation. Just tell me what you need!
            </p>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
              <button
                onClick={() => setInputMessage("Show me all my tasks")}
                className="p-4 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-xl hover:shadow-md hover:-translate-y-0.5 transition-all text-left group"
              >
                <div className="text-sm font-medium text-neutral-900 dark:text-white mb-1">
                  📋 View Tasks
                </div>
                <div className="text-xs text-neutral-600 dark:text-neutral-400">
                  Show me all my tasks
                </div>
              </button>
              <button
                onClick={() => setInputMessage("Add a new task")}
                className="p-4 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-xl hover:shadow-md hover:-translate-y-0.5 transition-all text-left group"
              >
                <div className="text-sm font-medium text-neutral-900 dark:text-white mb-1">
                  ➕ Add Task
                </div>
                <div className="text-xs text-neutral-600 dark:text-neutral-400">
                  Create a new task
                </div>
              </button>
            </div>
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
          <div className="flex justify-start animate-fade-in">
            <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-2xl px-5 py-3 shadow-sm">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                ></div>
                <div
                  className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="border-t border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-4 py-4">
        <form onSubmit={handleSendMessage} className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Shift+Enter for new line)"
              className="w-full resize-none rounded-xl border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 px-4 py-3 pr-12 text-sm text-neutral-900 dark:text-white placeholder-neutral-500 dark:placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all max-h-32"
              rows={1}
              disabled={loading}
              aria-label="Message input"
              style={{
                minHeight: '44px',
                height: 'auto',
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = Math.min(target.scrollHeight, 128) + 'px';
              }}
            />
          </div>
          <button
            type="submit"
            disabled={!inputMessage.trim() || loading}
            className="flex-shrink-0 w-11 h-11 bg-gradient-to-br from-primary-600 to-secondary-600 text-white rounded-xl font-medium hover:shadow-lg hover:scale-105 active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all flex items-center justify-center"
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
        <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-2 text-center">
          AI can make mistakes. Please verify important information.
        </p>
      </div>
    </div>
  );
}
