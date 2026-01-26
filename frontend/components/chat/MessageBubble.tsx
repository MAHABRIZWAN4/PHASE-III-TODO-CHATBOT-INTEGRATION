import type { Message } from "@/lib/types";

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
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
      role="article"
      aria-label={`${isUser ? "Your" : "Assistant"} message`}
    >
      <div
        className={`max-w-[75%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gray-100 text-gray-900 border border-gray-200"
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

        {/* Timestamp */}
        <div
          className={`text-xs mt-2 ${
            isUser ? "text-blue-100" : "text-gray-500"
          }`}
          dir={isUrdu ? "rtl" : "ltr"}
        >
          {timestamp}
        </div>
      </div>
    </div>
  );
}
