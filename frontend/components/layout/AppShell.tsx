"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquare,
  CheckSquare,
  Settings,
  Menu,
  X,
  Sun,
  Moon,
  LogOut,
  User,
  Brain,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { logout } from "@/lib/auth";

/**
 * User information for the AppShell
 */
interface AppShellUser {
  id: string;
  name?: string;
  email: string;
  avatar?: string;
}

/**
 * Props for the AppShell component
 */
interface AppShellProps {
  children: React.ReactNode;
  user: AppShellUser;
}

/**
 * Navigation item configuration
 */
interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navigation: NavItem[] = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Tasks", href: "/tasks", icon: CheckSquare },
  { name: "Settings", href: "/settings", icon: Settings },
];

/**
 * AppShell Component
 *
 * Responsive navigation system that wraps authenticated pages.
 * Features:
 * - Desktop: Fixed sidebar with collapsible functionality
 * - Mobile: Bottom navigation + slide-in drawer
 * - Theme toggle (light/dark mode)
 * - User profile dropdown
 * - Active route highlighting
 * - Full accessibility support
 */
export default function AppShell({ children, user }: AppShellProps) {
  const pathname = usePathname();
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const profileDropdownRef = useRef<HTMLDivElement>(null);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.classList.toggle("dark", savedTheme === "dark");
    }
  }, []);

  // Close mobile drawer when route changes
  useEffect(() => {
    setIsMobileDrawerOpen(false);
  }, [pathname]);

  // Close profile dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        profileDropdownRef.current &&
        !profileDropdownRef.current.contains(event.target as Node)
      ) {
        setIsProfileDropdownOpen(false);
      }
    }

    if (isProfileDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isProfileDropdownOpen]);

  // Handle Escape key to close drawer and dropdown
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsMobileDrawerOpen(false);
        setIsProfileDropdownOpen(false);
      }
    }

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, []);

  // Toggle theme
  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
  };

  // Handle logout
  const handleLogout = () => {
    logout();
  };

  // Check if route is active
  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  // Get user initials for avatar
  const getUserInitials = () => {
    if (user.name) {
      return user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    return user.email[0].toUpperCase();
  };

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900">
      {/* Skip to content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded-lg"
      >
        Skip to content
      </a>

      {/* Mobile Header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 h-16">
        <div className="flex items-center justify-between h-full px-4">
          <button
            onClick={() => setIsMobileDrawerOpen(true)}
            className="p-2 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu className="w-6 h-6" />
          </button>

          <div className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            <span className="text-lg font-semibold text-neutral-900 dark:text-white">
              TaskAI
            </span>
          </div>

          <button
            onClick={toggleTheme}
            className="p-2 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
          >
            {theme === "light" ? (
              <Moon className="w-5 h-5" />
            ) : (
              <Sun className="w-5 h-5" />
            )}
          </button>
        </div>
      </header>

      {/* Mobile Drawer Backdrop */}
      {isMobileDrawerOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40 transition-opacity"
          onClick={() => setIsMobileDrawerOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile Drawer */}
      <aside
        className={`lg:hidden fixed top-0 left-0 bottom-0 z-50 w-64 bg-white dark:bg-neutral-800 transform transition-transform duration-300 ${
          isMobileDrawerOpen ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Mobile navigation"
      >
        <div className="flex flex-col h-full">
          {/* Drawer Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              <span className="text-lg font-semibold text-neutral-900 dark:text-white">
                TaskAI
              </span>
            </div>
            <button
              onClick={() => setIsMobileDrawerOpen(false)}
              className="p-2 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
              aria-label="Close navigation menu"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    active
                      ? "bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400"
                      : "text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 hover:text-neutral-900 dark:hover:text-white"
                  }`}
                  aria-current={active ? "page" : undefined}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Drawer User Profile */}
          <div className="border-t border-neutral-200 dark:border-neutral-700 p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-primary-600 dark:bg-primary-500 flex items-center justify-center text-white font-semibold">
                {getUserInitials()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-900 dark:text-white truncate">
                  {user.name || "User"}
                </p>
                <p className="text-xs text-neutral-600 dark:text-neutral-400 truncate">
                  {user.email}
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-700 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Desktop Sidebar */}
      <aside
        className={`hidden lg:flex lg:flex-col lg:fixed lg:top-0 lg:left-0 lg:bottom-0 lg:z-30 bg-white dark:bg-neutral-800 border-r border-neutral-200 dark:border-neutral-700 transition-all duration-300 ${
          isSidebarCollapsed ? "lg:w-20" : "lg:w-64"
        }`}
        aria-label="Desktop navigation"
      >
        {/* Sidebar Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-neutral-200 dark:border-neutral-700">
          {!isSidebarCollapsed && (
            <div className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              <span className="text-lg font-semibold text-neutral-900 dark:text-white">
                TaskAI
              </span>
            </div>
          )}
          {isSidebarCollapsed && (
            <Brain className="w-6 h-6 text-primary-600 dark:text-primary-400 mx-auto" />
          )}
        </div>

        {/* Sidebar Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  active
                    ? "bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400"
                    : "text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 hover:text-neutral-900 dark:hover:text-white"
                } ${isSidebarCollapsed ? "justify-center" : ""}`}
                aria-current={active ? "page" : undefined}
                title={isSidebarCollapsed ? item.name : undefined}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {!isSidebarCollapsed && (
                  <span className="font-medium">{item.name}</span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="border-t border-neutral-200 dark:border-neutral-700 p-4">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className={`w-full flex items-center gap-3 px-3 py-2 mb-2 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 rounded-lg transition-colors ${
              isSidebarCollapsed ? "justify-center" : ""
            }`}
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            title={isSidebarCollapsed ? `${theme === "light" ? "Dark" : "Light"} mode` : undefined}
          >
            {theme === "light" ? (
              <Moon className="w-5 h-5 flex-shrink-0" />
            ) : (
              <Sun className="w-5 h-5 flex-shrink-0" />
            )}
            {!isSidebarCollapsed && (
              <span className="font-medium">
                {theme === "light" ? "Dark" : "Light"} mode
              </span>
            )}
          </button>

          {/* Collapse Toggle */}
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className={`w-full flex items-center gap-3 px-3 py-2 mb-3 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 rounded-lg transition-colors ${
              isSidebarCollapsed ? "justify-center" : ""
            }`}
            aria-label={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            title={isSidebarCollapsed ? "Expand sidebar" : undefined}
          >
            {isSidebarCollapsed ? (
              <ChevronRight className="w-5 h-5 flex-shrink-0" />
            ) : (
              <>
                <ChevronLeft className="w-5 h-5 flex-shrink-0" />
                <span className="font-medium">Collapse</span>
              </>
            )}
          </button>

          {/* User Profile */}
          <div className="relative" ref={profileDropdownRef}>
            <button
              onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
              className={`w-full flex items-center gap-3 px-3 py-2 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 rounded-lg transition-colors ${
                isSidebarCollapsed ? "justify-center" : ""
              }`}
              aria-expanded={isProfileDropdownOpen}
              aria-haspopup="true"
              title={isSidebarCollapsed ? user.name || user.email : undefined}
            >
              <div className="w-8 h-8 rounded-full bg-primary-600 dark:bg-primary-500 flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
                {getUserInitials()}
              </div>
              {!isSidebarCollapsed && (
                <div className="flex-1 min-w-0 text-left">
                  <p className="text-sm font-medium text-neutral-900 dark:text-white truncate">
                    {user.name || "User"}
                  </p>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400 truncate">
                    {user.email}
                  </p>
                </div>
              )}
            </button>

            {/* Profile Dropdown */}
            {isProfileDropdownOpen && !isSidebarCollapsed && (
              <div className="absolute bottom-full left-0 right-0 mb-2 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg overflow-hidden">
                <Link
                  href="/settings"
                  className="flex items-center gap-2 px-4 py-2 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors"
                  onClick={() => setIsProfileDropdownOpen(false)}
                >
                  <User className="w-4 h-4" />
                  <span>Profile</span>
                </Link>
                <Link
                  href="/settings"
                  className="flex items-center gap-2 px-4 py-2 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors"
                  onClick={() => setIsProfileDropdownOpen(false)}
                >
                  <Settings className="w-4 h-4" />
                  <span>Settings</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-700 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Mobile Bottom Navigation */}
      <nav
        className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white dark:bg-neutral-800 border-t border-neutral-200 dark:border-neutral-700 shadow-lg h-16"
        aria-label="Mobile bottom navigation"
      >
        <div className="flex items-center justify-around h-full px-2">
          {navigation.slice(0, 3).map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex flex-col items-center justify-center gap-1 px-3 py-2 min-w-[44px] min-h-[44px] transition-colors ${
                  active
                    ? "text-primary-600 dark:text-primary-400"
                    : "text-neutral-500 dark:text-neutral-400"
                }`}
                aria-current={active ? "page" : undefined}
                aria-label={item.name}
              >
                <Icon className="w-6 h-6" />
                <span className="text-xs font-medium">{item.name}</span>
              </Link>
            );
          })}
          <button
            onClick={() => setIsMobileDrawerOpen(true)}
            className="flex flex-col items-center justify-center gap-1 px-3 py-2 min-w-[44px] min-h-[44px] text-neutral-500 dark:text-neutral-400 transition-colors"
            aria-label="Open profile menu"
          >
            <User className="w-6 h-6" />
            <span className="text-xs font-medium">Profile</span>
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main
        id="main-content"
        className={`transition-all duration-300 ${
          isSidebarCollapsed ? "lg:ml-20" : "lg:ml-64"
        } pt-16 lg:pt-0 pb-16 lg:pb-0`}
      >
        {children}
      </main>
    </div>
  );
}
