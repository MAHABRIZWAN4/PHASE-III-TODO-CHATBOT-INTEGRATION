"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getAuthUser, logout, type AuthUser } from "@/lib/auth";
import ChatInterface from "@/components/chat/ChatInterface";
import {
  Brain,
  MessageSquare,
  Plus,
  Search,
  MoreVertical,
  Trash2,
  Menu,
  X,
  Moon,
  Sun,
  LogOut,
  Bell
} from "lucide-react";
import { Avatar } from "@/components/ui/Avatar";
import { Button } from "@/components/ui/Button";
import { SpinnerFullPage } from "@/components/ui/Spinner";

/**
 * Chat page for AI-powered todo assistant
 * Protected route - requires authentication
 */
export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // Get user from localStorage on client side only
    const authUser = getAuthUser();
    setUser(authUser);

    if (!authUser) {
      router.replace("/login");
    }

    // Check for dark mode preference
    const isDark = localStorage.getItem("darkMode") === "true";
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add("dark");
    }
  }, [router]);

  const handleLogout = () => {
    logout();
  };

  const handleConversationCreated = (newConversationId: string) => {
    setConversationId(newConversationId);
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
      {/* Conversation Sidebar - Desktop */}
      <aside className="hidden lg:flex lg:flex-col lg:w-80 bg-white dark:bg-neutral-800 border-r border-neutral-200 dark:border-neutral-700">
        {/* Sidebar Header */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-neutral-200 dark:border-neutral-700">
          <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
            Conversations
          </h2>
          <button
            className="p-2 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
            aria-label="New conversation"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-700">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              className="w-full pl-10 pr-4 py-2 bg-neutral-100 dark:bg-neutral-700 border-0 rounded-lg text-sm text-neutral-900 dark:text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2 space-y-1">
            {/* Active Conversation */}
            <div className="group px-4 py-3 bg-primary-50 dark:bg-primary-900/20 border-l-4 border-primary-600 rounded-r-lg cursor-pointer">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-neutral-900 dark:text-white truncate">
                    Current Chat
                  </h3>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400 truncate mt-1">
                    Add task to buy groceries...
                  </p>
                  <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
                    Just now
                  </p>
                </div>
                <button className="opacity-0 group-hover:opacity-100 p-1 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-opacity">
                  <MoreVertical className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Empty State */}
            <div className="px-4 py-8 text-center">
              <MessageSquare className="w-12 h-12 text-neutral-300 dark:text-neutral-600 mx-auto mb-3" />
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                No previous conversations
              </p>
              <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
                Start a new chat to see it here
              </p>
            </div>
          </div>
        </div>

        {/* User Profile */}
        <div className="p-4 border-t border-neutral-200 dark:border-neutral-700">
          <Link href="/dashboard" className="flex items-center gap-3 px-3 py-2 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors">
            <Avatar name={user.name || user.email} size="md" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-neutral-900 dark:text-white truncate">
                {user.name || "User"}
              </p>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate">
                Back to Dashboard
              </p>
            </div>
          </Link>
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
        className={`fixed inset-y-0 left-0 z-50 w-80 bg-white dark:bg-neutral-800 border-r border-neutral-200 dark:border-neutral-700 transform transition-transform duration-300 lg:hidden ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Sidebar Header */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-neutral-200 dark:border-neutral-700">
          <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
            Conversations
          </h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Search */}
        <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-700">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              className="w-full pl-10 pr-4 py-2 bg-neutral-100 dark:bg-neutral-700 border-0 rounded-lg text-sm text-neutral-900 dark:text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2 space-y-1">
            <div className="px-4 py-8 text-center">
              <MessageSquare className="w-12 h-12 text-neutral-300 dark:text-neutral-600 mx-auto mb-3" />
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                No previous conversations
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
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
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-neutral-900 dark:text-white">
                  AI Assistant
                </h1>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Always ready to help
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleDarkMode}
              className="p-2 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button
              className="p-2 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors relative"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5" />
            </button>
            <Link href="/dashboard">
              <Button variant="ghost" size="sm" className="hidden sm:flex">
                Dashboard
              </Button>
            </Link>
            <button
              onClick={handleLogout}
              className="hidden sm:flex items-center gap-2 px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </header>

        {/* Chat Container with Gradient Background */}
        <div className="flex-1 bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-neutral-900 dark:via-neutral-900 dark:to-neutral-800 overflow-hidden">
          <div className="h-full max-w-5xl mx-auto">
            <ChatInterface
              conversationId={conversationId}
              onConversationCreated={handleConversationCreated}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

