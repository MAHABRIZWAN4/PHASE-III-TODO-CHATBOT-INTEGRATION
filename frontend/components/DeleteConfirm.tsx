"use client";

interface DeleteConfirmProps {
  taskTitle: string;
  onConfirm: () => void;
  onCancel: () => void;
  isDeleting?: boolean;
}

export default function DeleteConfirm({ taskTitle, onConfirm, onCancel, isDeleting = false }: DeleteConfirmProps) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="mb-4">
          <svg
            className="mx-auto h-12 w-12 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 9l9 9m-9-2v2M9 5a2 2 0 012 2v10a2 2 0 002-2h-10a2 2 0 00-2-2V9a2 2 0 00-2-2h-2m0 9l9-9m-9-2v2"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Delete Task
        </h3>
        <p className="text-sm text-gray-600 mb-6">
          Are you sure you want to delete &quot;{taskTitle}&quot;? This action cannot be undone.
        </p>
        <div className="flex space-x-3">
          <button
            onClick={onCancel}
            disabled={isDeleting}
            className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isDeleting}
            className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}
