/**
 * @jest-environment jsdom
 */

import { sendChatMessage, getConversations, getConversationMessages } from "@/lib/chat-api";
import * as auth from "@/lib/auth";

// Mock the auth module
jest.mock("@/lib/auth");

// Mock fetch
global.fetch = jest.fn();

describe("chat-api", () => {
  const mockGetAuthToken = auth.getAuthToken as jest.MockedFunction<
    typeof auth.getAuthToken
  >;
  const mockGetAuthUser = auth.getAuthUser as jest.MockedFunction<
    typeof auth.getAuthUser
  >;
  const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    jest.clearAllMocks();
    process.env.NEXT_PUBLIC_API_URL = "http://localhost:8000";
  });

  describe("sendChatMessage", () => {
    it("sends chat message with authentication token", async () => {
      const mockUser = { id: "user123", email: "test@example.com" };
      const mockToken = "test-token";
      const mockResponse = {
        message: {
          id: 2,
          conversation_id: 1,
          role: "assistant",
          content: "Task created!",
          created_at: "2024-01-01T00:00:00Z",
        },
        conversation_id: 1,
      };

      mockGetAuthUser.mockReturnValue(mockUser);
      mockGetAuthToken.mockReturnValue(mockToken);
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await sendChatMessage("Add buy milk");

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/user123/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
          body: JSON.stringify({ message: "Add buy milk" }),
        }
      );

      expect(result).toEqual(mockResponse);
    });

    it("sends chat message with conversation ID", async () => {
      const mockUser = { id: "user123", email: "test@example.com" };
      const mockToken = "test-token";
      const mockResponse = {
        message: {
          id: 4,
          conversation_id: 1,
          role: "assistant",
          content: "Done!",
          created_at: "2024-01-01T00:00:00Z",
        },
        conversation_id: 1,
      };

      mockGetAuthUser.mockReturnValue(mockUser);
      mockGetAuthToken.mockReturnValue(mockToken);
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await sendChatMessage("List my tasks", 1);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/user123/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
          body: JSON.stringify({
            message: "List my tasks",
            conversation_id: 1,
          }),
        }
      );

      expect(result).toEqual(mockResponse);
    });

    it("throws error when user is not authenticated", async () => {
      mockGetAuthUser.mockReturnValue(null);

      await expect(sendChatMessage("Test message")).rejects.toThrow(
        "User not authenticated"
      );

      expect(mockFetch).not.toHaveBeenCalled();
    });

    it("throws error when API request fails", async () => {
      const mockUser = { id: "user123", email: "test@example.com" };
      const mockToken = "test-token";

      mockGetAuthUser.mockReturnValue(mockUser);
      mockGetAuthToken.mockReturnValue(mockToken);
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: "Internal server error" }),
      } as Response);

      await expect(sendChatMessage("Test message")).rejects.toThrow(
        "Internal server error"
      );
    });

    it("handles network errors gracefully", async () => {
      const mockUser = { id: "user123", email: "test@example.com" };
      const mockToken = "test-token";

      mockGetAuthUser.mockReturnValue(mockUser);
      mockGetAuthToken.mockReturnValue(mockToken);
      mockFetch.mockRejectedValueOnce(new Error("Network error"));

      await expect(sendChatMessage("Test message")).rejects.toThrow(
        "Network error"
      );
    });

    it("handles malformed error responses", async () => {
      const mockUser = { id: "user123", email: "test@example.com" };
      const mockToken = "test-token";

      mockGetAuthUser.mockReturnValue(mockUser);
      mockGetAuthToken.mockReturnValue(mockToken);
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error("Invalid JSON");
        },
      } as Response);

      await expect(sendChatMessage("Test message")).rejects.toThrow(
        "Request failed"
      );
    });
  });

  describe("getConversations", () => {
    it("fetches conversations for authenticated user", async () => {
      const mockUser = { id: "user123", email: "test@example.com" };
      const mockToken = "test-token";
      const mockConversations = [
        {
          id: 1,
          user_id: "user123",
          title: "Task Management",
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-01T00:00:00Z",
        },
      ];

      mockGetAuthUser.mockReturnValue(mockUser);
      mockGetAuthToken.mockReturnValue(mockToken);
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockConversations,
      } as Response);

      const result = await getConversations();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/user123/conversations",
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
        }
      );

      expect(result).toEqual(mockConversations);
    });

    it("throws error when user is not authenticated", async () => {
      mockGetAuthUser.mockReturnValue(null);

      await expect(getConversations()).rejects.toThrow(
        "User not authenticated"
      );
    });
  });

  describe("getConversationMessages", () => {
    it("fetches messages for a specific conversation", async () => {
      const mockUser = { id: "user123", email: "test@example.com" };
      const mockToken = "test-token";
      const mockMessages = [
        {
          id: 1,
          conversation_id: 1,
          role: "user" as const,
          content: "Add task",
          created_at: "2024-01-01T00:00:00Z",
        },
        {
          id: 2,
          conversation_id: 1,
          role: "assistant" as const,
          content: "Task added!",
          created_at: "2024-01-01T00:01:00Z",
        },
      ];

      mockGetAuthUser.mockReturnValue(mockUser);
      mockGetAuthToken.mockReturnValue(mockToken);
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMessages,
      } as Response);

      const result = await getConversationMessages(1);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/user123/conversations/1/messages",
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer test-token",
          },
        }
      );

      expect(result).toEqual(mockMessages);
    });

    it("throws error when user is not authenticated", async () => {
      mockGetAuthUser.mockReturnValue(null);

      await expect(getConversationMessages(1)).rejects.toThrow(
        "User not authenticated"
      );
    });
  });
});
