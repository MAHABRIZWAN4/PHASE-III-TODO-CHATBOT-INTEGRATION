"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { isAuthenticated } from "@/lib/auth";
import {
  Brain,
  CheckCircle,
  Zap,
  MessageSquare,
  Globe,
  ArrowRight,
  Sparkles,
  Users,
  TrendingUp
} from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function Home() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Redirect authenticated users to dashboard
    if (isAuthenticated()) {
      router.replace("/dashboard");
    } else {
      setIsChecking(false);
    }
  }, [router]);

  // Show loading while checking auth
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-neutral-900">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-lg border-b border-neutral-200 dark:border-neutral-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gradient">TaskAI</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/login">
                <Button variant="ghost" size="md">
                  Sign in
                </Button>
              </Link>
              <Link href="/signup">
                <Button variant="primary" size="md">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-neutral-900 dark:via-neutral-900 dark:to-neutral-800">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-8 animate-fade-in">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-neutral-800 rounded-full shadow-sm border border-neutral-200 dark:border-neutral-700">
              <Sparkles className="w-4 h-4 text-primary-600" />
              <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                AI-Powered Task Management
              </span>
            </div>

            {/* Headline */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-neutral-900 dark:text-white leading-tight">
              Manage tasks with{" "}
              <span className="text-gradient">AI intelligence</span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl sm:text-2xl text-neutral-600 dark:text-neutral-400 max-w-3xl mx-auto">
              Transform your productivity with natural language task management.
              Just tell us what you need to do, and let AI organize it for you.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link href="/signup">
                <Button variant="primary" size="lg" className="w-full sm:w-auto">
                  Start for free
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                  View demo
                </Button>
              </Link>
            </div>

            {/* Social Proof */}
            <div className="pt-8 flex items-center justify-center gap-8 text-sm text-neutral-600 dark:text-neutral-400">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                <span>10,000+ users</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                <span>50,000+ tasks completed</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white dark:bg-neutral-900">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold text-neutral-900 dark:text-white">
              Everything you need to stay productive
            </h2>
            <p className="text-xl text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto">
              Powerful features designed to help you manage tasks effortlessly
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="group p-8 bg-gradient-to-br from-primary-50 to-white dark:from-neutral-800 dark:to-neutral-900 rounded-2xl border border-neutral-200 dark:border-neutral-700 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-neutral-900 dark:text-white mb-2">
                Natural Language Input
              </h3>
              <p className="text-neutral-600 dark:text-neutral-400">
                Simply describe what you need to do in plain English or Urdu. No complex forms or fields.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="group p-8 bg-gradient-to-br from-secondary-50 to-white dark:from-neutral-800 dark:to-neutral-900 rounded-2xl border border-neutral-200 dark:border-neutral-700 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-to-br from-secondary-500 to-secondary-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-neutral-900 dark:text-white mb-2">
                Smart Prioritization
              </h3>
              <p className="text-neutral-600 dark:text-neutral-400">
                AI automatically organizes and prioritizes your tasks based on urgency and importance.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="group p-8 bg-gradient-to-br from-green-50 to-white dark:from-neutral-800 dark:to-neutral-900 rounded-2xl border border-neutral-200 dark:border-neutral-700 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-neutral-900 dark:text-white mb-2">
                Multi-Language Support
              </h3>
              <p className="text-neutral-600 dark:text-neutral-400">
                Work in your preferred language. Full support for English and Urdu with more coming soon.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-neutral-50 to-white dark:from-neutral-800 dark:to-neutral-900">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-4xl sm:text-5xl font-bold text-neutral-900 dark:text-white">
                Why choose TaskAI?
              </h2>
              <p className="text-xl text-neutral-600 dark:text-neutral-400">
                Join thousands of professionals who have transformed their productivity with AI-powered task management.
              </p>

              <div className="space-y-4 pt-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg text-neutral-900 dark:text-white">
                      Save time with AI automation
                    </h3>
                    <p className="text-neutral-600 dark:text-neutral-400">
                      Let AI handle the organization while you focus on getting things done.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg text-neutral-900 dark:text-white">
                      Never miss a deadline
                    </h3>
                    <p className="text-neutral-600 dark:text-neutral-400">
                      Smart reminders and intelligent prioritization keep you on track.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg text-neutral-900 dark:text-white">
                      Work your way
                    </h3>
                    <p className="text-neutral-600 dark:text-neutral-400">
                      Type, speak, or chat - manage tasks however you prefer.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="aspect-square rounded-3xl overflow-hidden">
                <Image
                  src="/ai-workflow.png"
                  alt="AI Workflow Illustration"
                  width={600}
                  height={600}
                  className="w-full h-full object-cover"
                  priority
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary-600 to-secondary-600">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="text-4xl sm:text-5xl font-bold text-white">
            Ready to transform your productivity?
          </h2>
          <p className="text-xl text-primary-100">
            Join thousands of users who are already managing their tasks smarter with AI.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/signup">
              <Button
                variant="secondary"
                size="lg"
                className="w-full sm:w-auto bg-white text-primary-600 hover:bg-neutral-100"
              >
                Get started for free
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
          <p className="text-sm text-primary-100">
            No credit card required • Free forever • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 bg-neutral-900 dark:bg-black">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-white">TaskAI</span>
            </div>
            <p className="text-sm text-neutral-400">
              © 2026 TaskAI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

