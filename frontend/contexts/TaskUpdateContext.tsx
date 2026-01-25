"use client";

import React, { createContext, useContext, useState, useCallback } from 'react';

interface TaskUpdateContextType {
  triggerTaskRefresh: () => void;
  onTaskRefresh: (callback: () => void) => () => void;
}

const TaskUpdateContext = createContext<TaskUpdateContextType | undefined>(undefined);

export function TaskUpdateProvider({ children }: { children: React.ReactNode }) {
  const [refreshCallbacks, setRefreshCallbacks] = useState<Set<() => void>>(new Set());

  const triggerTaskRefresh = useCallback(() => {
    console.log('[TaskUpdateContext] triggerTaskRefresh called, callbacks:', refreshCallbacks.size);
    refreshCallbacks.forEach(callback => {
      try {
        callback();
      } catch (error) {
        console.error('Error in task refresh callback:', error);
      }
    });
  }, [refreshCallbacks]);

  const onTaskRefresh = useCallback((callback: () => void) => {
    setRefreshCallbacks(prev => {
      const newSet = new Set(prev);
      newSet.add(callback);
      return newSet;
    });

    // Return cleanup function
    return () => {
      setRefreshCallbacks(prev => {
        const newSet = new Set(prev);
        newSet.delete(callback);
        return newSet;
      });
    };
  }, []);

  return (
    <TaskUpdateContext.Provider value={{ triggerTaskRefresh, onTaskRefresh }}>
      {children}
    </TaskUpdateContext.Provider>
  );
}

export function useTaskUpdate() {
  const context = useContext(TaskUpdateContext);
  if (context === undefined) {
    throw new Error('useTaskUpdate must be used within a TaskUpdateProvider');
  }
  return context;
}
