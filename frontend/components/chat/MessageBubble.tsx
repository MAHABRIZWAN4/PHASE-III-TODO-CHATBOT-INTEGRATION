import type { Message } from "@/lib/types";
import { Avatar } from "@/components/ui/Avatar";
import { Brain } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
}

/**
 * Detect if text contains Urdu characters
 * Checks for Arabic/Urdu Unicode range (U+0600 to U+06FF)
 */
function containsUrdu(text: string): boolean {
  const urduRegex = /[\u0600-\u06FF]/;
  return urduRegex.test(text);
}

/**
 * MessageBubble component displays individual chat messages
 * with different styling for user vs assistant messages
 * Supports RTL text direction for Urdu content
 */
export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isUrdu = containsUrdu(message.content);
  const timestamp = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} group animate-fade-in`}
      role="article"
      aria-label={`${isUser ? "Your" : "Assistant"} message`}
    >
      <div className={`flex items-start gap-3 max-w-[85%] sm:max-w-[75%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        {/* Avatar */}
        {!isUser && (
          <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-xl flex items-center justify-center shadow-sm">
            <Brain className="w-5 h-5 text-white" />
          </div>
        )}

        {/* Message Content */}
        <div className="flex flex-col gap-1">
          <div
            className={`rounded-2xl px-4 py-3 shadow-sm transition-all ${
              isUser
                ? "bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-tr-sm"
                : "bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white border border-neutral-200 dark:border-neutral-700 rounded-tl-sm"
            }`}
          >
            {/* Message content with RTL support for Urdu */}
            <div
              className={`whitespace-pre-wrap break-words text-sm leading-relaxed ${
                isUrdu ? "urdu-text" : ""
              }`}
              dir={isUrdu ? "rtl" : "ltr"}
            >
              {message.content}
            </div>
          </div>

          {/* Timestamp - shown on hover */}
          <div
            className={`text-xs text-neutral-500 dark:text-neutral-400 opacity-0 group-hover:opacity-100 transition-opacity px-1 ${
              isUser ? "text-right" : "text-left"
            }`}
            dir={isUrdu ? "rtl" : "ltr"}
          >
            {timestamp}
          </div>
        </div>

        {/* User Avatar */}
        {isUser && (
          <div className="flex-shrink-0">
            <Avatar size="sm" />
          </div>
        )}
      </div>
    </div>
  );
}

