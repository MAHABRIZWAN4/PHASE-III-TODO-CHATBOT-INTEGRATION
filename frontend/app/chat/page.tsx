"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getAuthUser, logout, type AuthUser } from "@/lib/auth";
import ChatInterface from "@/components/chat/ChatInterface";

/**
 * Chat page for AI-powered todo assistant
 * Protected route - requires authentication
 */
export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>();

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

  const handleConversationCreated = (newConversationId: string) => {
    setConversationId(newConversationId);
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
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-semibold text-gray-900">Todo App</h1>
              <div className="hidden sm:flex space-x-4">
                <Link
                  href="/dashboard"
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
                >
                  Tasks
                </Link>
                <Link
                  href="/chat"
                  className="px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md"
                >
                  Chat
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                {user.name || user.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex flex-col max-w-7xl w-full mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-gray-900">AI Assistant</h2>
          <p className="text-sm text-gray-600">
            Chat with your AI-powered todo assistant
          </p>
        </div>

        {/* Chat Container */}
        <div className="flex-1 bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden flex flex-col">
          <ChatInterface
            conversationId={conversationId}
            onConversationCreated={handleConversationCreated}
          />
        </div>
      </div>
    </div>
  );
}
