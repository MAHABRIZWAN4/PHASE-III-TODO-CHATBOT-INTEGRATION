"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getAuthUser, logout, type AuthUser } from "@/lib/auth";
import {
  Brain,
  ArrowLeft,
  User,
  Bell,
  Moon,
  Sun,
  Globe,
  Shield,
  Trash2,
  Save,
  LogOut
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Avatar } from "@/components/ui/Avatar";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { SpinnerFullPage } from "@/components/ui/Spinner";

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(true);
  const [language, setLanguage] = useState("en");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const authUser = getAuthUser();
    setUser(authUser);

    if (!authUser) {
      router.replace("/login");
    }

    // Load preferences
    const isDark = localStorage.getItem("darkMode") === "true";
    setDarkMode(isDark);

    const savedLanguage = localStorage.getItem("language") || "en";
    setLanguage(savedLanguage);
  }, [router]);

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

  const handleSaveSettings = async () => {
    setSaving(true);

    // Save to localStorage
    localStorage.setItem("darkMode", String(darkMode));
    localStorage.setItem("language", language);
    localStorage.setItem("emailNotifications", String(emailNotifications));
    localStorage.setItem("pushNotifications", String(pushNotifications));

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    setSaving(false);
    alert("Settings saved successfully!");
  };

  const handleLogout = () => {
    logout();
  };

  if (!user) {
    return <SpinnerFullPage />;
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900">
      {/* Header */}
      <header className="bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="p-2 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <h1 className="text-xl font-semibold text-neutral-900 dark:text-white">
                Settings
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={toggleDarkMode}
                className="p-2 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
                aria-label="Toggle dark mode"
              >
                {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Profile Section */}
          <Card variant="elevated">
            <CardHeader>
              <div className="flex items-center gap-3">
                <User className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                  Profile
                </h2>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4">
                <Avatar name={user.name || user.email} size="xl" />
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-neutral-900 dark:text-white">
                    {user.name || "User"}
                  </h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">
                    {user.email}
                  </p>
                </div>
              </div>
              <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700">
                <Button variant="secondary" size="sm">
                  Edit Profile
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Appearance Section */}
          <Card variant="elevated">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Moon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                  Appearance
                </h2>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-neutral-900 dark:text-white">
                    Dark Mode
                  </h3>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400">
                    Switch between light and dark theme
                  </p>
                </div>
                <button
                  onClick={toggleDarkMode}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    darkMode ? "bg-primary-600" : "bg-neutral-300"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      darkMode ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>
            </CardContent>
          </Card>

          {/* Notifications Section */}
          <Card variant="elevated">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Bell className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                  Notifications
                </h2>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-neutral-900 dark:text-white">
                    Email Notifications
                  </h3>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400">
                    Receive email updates about your tasks
                  </p>
                </div>
                <button
                  onClick={() => setEmailNotifications(!emailNotifications)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    emailNotifications ? "bg-primary-600" : "bg-neutral-300"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      emailNotifications ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-neutral-200 dark:border-neutral-700">
                <div>
                  <h3 className="text-sm font-medium text-neutral-900 dark:text-white">
                    Push Notifications
                  </h3>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400">
                    Get notified about overdue tasks
                  </p>
                </div>
                <button
                  onClick={() => setPushNotifications(!pushNotifications)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    pushNotifications ? "bg-primary-600" : "bg-neutral-300"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      pushNotifications ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>
            </CardContent>
          </Card>

          {/* Language Section */}
          <Card variant="elevated">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Globe className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                  Language
                </h2>
              </div>
            </CardHeader>
            <CardContent>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-4 py-2 bg-white dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="en">English</option>
                <option value="ur">اردو (Urdu)</option>
              </select>
            </CardContent>
          </Card>

          {/* Security Section */}
          <Card variant="elevated">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Shield className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                  Security
                </h2>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button variant="secondary" size="sm">
                Change Password
              </Button>
              <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700">
                <Button variant="danger" size="sm">
                  <Trash2 className="w-4 h-4" />
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Save Button */}
          <div className="flex items-center justify-between pt-4">
            <Button
              variant="ghost"
              size="md"
              onClick={handleLogout}
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={handleSaveSettings}
              loading={saving}
              disabled={saving}
            >
              <Save className="w-4 h-4" />
              {saving ? "Saving..." : "Save Settings"}
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
