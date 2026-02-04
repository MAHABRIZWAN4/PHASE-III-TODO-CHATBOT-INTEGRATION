"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getAuthUser, logout, type AuthUser, setAuthUser } from "@/lib/auth";
import { updateProfile, changePassword } from "@/lib/api";
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
  LogOut,
  X,
  Check
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

  // Profile edit state
  const [showProfileEdit, setShowProfileEdit] = useState(false);
  const [profileName, setProfileName] = useState("");
  const [profileEmail, setProfileEmail] = useState("");
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [profileSuccess, setProfileSuccess] = useState(false);

  // Password change state
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  useEffect(() => {
    const authUser = getAuthUser();
    setUser(authUser);

    if (!authUser) {
      window.location.href = '/login';
      return;
    } else {
      // Initialize profile form with current user data
      setProfileName(authUser.name || "");
      setProfileEmail(authUser.email);
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
    setUser(null); // Clear user state to trigger redirect
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileError("");
    setProfileSuccess(false);
    setProfileSaving(true);

    try {
      const updateData: { name?: string; email?: string } = {};

      if (profileName !== user?.name) {
        updateData.name = profileName;
      }

      if (profileEmail !== user?.email) {
        updateData.email = profileEmail;
      }

      if (Object.keys(updateData).length === 0) {
        setProfileError("No changes to save");
        setProfileSaving(false);
        return;
      }

      const updatedUser = await updateProfile(updateData);

      // Update local auth user
      if (user) {
        const newUser = { ...user, name: updatedUser.name, email: updatedUser.email };
        setAuthUser(newUser);
        setUser(newUser);
      }

      setProfileSuccess(true);
      setTimeout(() => {
        setShowProfileEdit(false);
        setProfileSuccess(false);
      }, 2000);
    } catch (error) {
      setProfileError(error instanceof Error ? error.message : "Failed to update profile");
    } finally {
      setProfileSaving(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError("");
    setPasswordSuccess(false);

    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordError("All fields are required");
      return;
    }

    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters");
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match");
      return;
    }

    setPasswordSaving(true);

    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      setPasswordSuccess(true);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      setTimeout(() => {
        setShowPasswordChange(false);
        setPasswordSuccess(false);
      }, 2000);
    } catch (error) {
      setPasswordError(error instanceof Error ? error.message : "Failed to change password");
    } finally {
      setPasswordSaving(false);
    }
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

              {!showProfileEdit ? (
                <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setShowProfileEdit(true)}
                  >
                    Edit Profile
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleProfileUpdate} className="pt-4 border-t border-neutral-200 dark:border-neutral-700 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      Name
                    </label>
                    <input
                      type="text"
                      value={profileName}
                      onChange={(e) => setProfileName(e.target.value)}
                      className="w-full px-4 py-2 bg-white dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Your name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      value={profileEmail}
                      onChange={(e) => setProfileEmail(e.target.value)}
                      className="w-full px-4 py-2 bg-white dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="your@email.com"
                      required
                    />
                  </div>

                  {profileError && (
                    <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400">
                      {profileError}
                    </div>
                  )}

                  {profileSuccess && (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-sm text-green-600 dark:text-green-400 flex items-center gap-2">
                      <Check className="w-4 h-4" />
                      Profile updated successfully!
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      variant="primary"
                      size="sm"
                      loading={profileSaving}
                      disabled={profileSaving}
                    >
                      <Save className="w-4 h-4" />
                      {profileSaving ? "Saving..." : "Save Changes"}
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setShowProfileEdit(false);
                        setProfileError("");
                        setProfileName(user?.name || "");
                        setProfileEmail(user?.email || "");
                      }}
                      disabled={profileSaving}
                    >
                      <X className="w-4 h-4" />
                      Cancel
                    </Button>
                  </div>
                </form>
              )}
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
              {!showPasswordChange ? (
                <>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setShowPasswordChange(true)}
                  >
                    Change Password
                  </Button>
                  <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700">
                    <Button variant="danger" size="sm">
                      <Trash2 className="w-4 h-4" />
                      Delete Account
                    </Button>
                  </div>
                </>
              ) : (
                <form onSubmit={handlePasswordChange} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      Current Password
                    </label>
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className="w-full px-4 py-2 bg-white dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Enter current password"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      New Password
                    </label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full px-4 py-2 bg-white dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Enter new password (min 8 characters)"
                      required
                      minLength={8}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full px-4 py-2 bg-white dark:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Confirm new password"
                      required
                    />
                  </div>

                  {passwordError && (
                    <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400">
                      {passwordError}
                    </div>
                  )}

                  {passwordSuccess && (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-sm text-green-600 dark:text-green-400 flex items-center gap-2">
                      <Check className="w-4 h-4" />
                      Password changed successfully!
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      variant="primary"
                      size="sm"
                      loading={passwordSaving}
                      disabled={passwordSaving}
                    >
                      <Save className="w-4 h-4" />
                      {passwordSaving ? "Changing..." : "Change Password"}
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setShowPasswordChange(false);
                        setPasswordError("");
                        setCurrentPassword("");
                        setNewPassword("");
                        setConfirmPassword("");
                      }}
                      disabled={passwordSaving}
                    >
                      <X className="w-4 h-4" />
                      Cancel
                    </Button>
                  </div>
                </form>
              )}
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
