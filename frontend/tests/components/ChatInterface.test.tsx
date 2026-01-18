/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ChatInterface from "@/components/chat/ChatInterface";
import * as chatApi from "@/lib/chat-api";

// Mock the chat API
jest.mock("@/lib/chat-api");

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

describe("ChatInterface", () => {
  const mockSendChatMessage = chatApi.sendChatMessage as jest.MockedFunction<
    typeof chatApi.sendChatMessage
  >;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders empty state with welcome message", () => {
    render(<ChatInterface />);

    expect(screen.getByText("Start a conversation")).toBeInTheDocument();
    expect(
      screen.getByText(/Ask me to create tasks, list your todos/i)
    ).toBeInTheDocument();
  });

  it("renders message input and send button", () => {
    render(<ChatInterface />);

    expect(screen.getByPlaceholderText(/Type your message/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Send message")).toBeInTheDocument();
  });

  it("sends message when form is submitted", async () => {
    const mockResponse = {
      message: {
        id: 2,
        conversation_id: 1,
        role: "assistant" as const,
        content: "Task created successfully!",
        created_at: new Date().toISOString(),
      },
      conversation_id: 1,
    };

    mockSendChatMessage.mockResolvedValueOnce(mockResponse);

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    const sendButton = screen.getByLabelText("Send message");

    // Type a message
    await userEvent.type(input, "Add buy milk to my tasks");

    // Click send button
    fireEvent.click(sendButton);

    // Wait for API call
    await waitFor(() => {
      expect(mockSendChatMessage).toHaveBeenCalledWith(
        "Add buy milk to my tasks",
        undefined
      );
    });

    // Check that messages are displayed
    await waitFor(() => {
      expect(screen.getByText("Add buy milk to my tasks")).toBeInTheDocument();
      expect(screen.getByText("Task created successfully!")).toBeInTheDocument();
    });
  });

  it("displays loading indicator while sending message", async () => {
    mockSendChatMessage.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await userEvent.type(input, "Test message");

    const sendButton = screen.getByLabelText("Send message");
    fireEvent.click(sendButton);

    // Check for loading state
    await waitFor(() => {
      expect(sendButton).toBeDisabled();
    });
  });

  it("displays error message when API call fails", async () => {
    mockSendChatMessage.mockRejectedValueOnce(
      new Error("Failed to send message")
    );

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await userEvent.type(input, "Test message");

    const sendButton = screen.getByLabelText("Send message");
    fireEvent.click(sendButton);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText("Failed to send message")).toBeInTheDocument();
    });
  });

  it("clears input after successful message send", async () => {
    const mockResponse = {
      message: {
        id: 2,
        conversation_id: 1,
        role: "assistant" as const,
        content: "Response",
        created_at: new Date().toISOString(),
      },
      conversation_id: 1,
    };

    mockSendChatMessage.mockResolvedValueOnce(mockResponse);

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(
      /Type your message/i
    ) as HTMLTextAreaElement;
    await userEvent.type(input, "Test message");

    const sendButton = screen.getByLabelText("Send message");
    fireEvent.click(sendButton);

    // Wait for message to be sent and input to be cleared
    await waitFor(() => {
      expect(input.value).toBe("");
    });
  });

  it("disables send button when input is empty", () => {
    render(<ChatInterface />);

    const sendButton = screen.getByLabelText("Send message");
    expect(sendButton).toBeDisabled();
  });

  it("calls onConversationCreated when new conversation is created", async () => {
    const mockOnConversationCreated = jest.fn();
    const mockResponse = {
      message: {
        id: 2,
        conversation_id: 1,
        role: "assistant" as const,
        content: "Response",
        created_at: new Date().toISOString(),
      },
      conversation_id: 1,
    };

    mockSendChatMessage.mockResolvedValueOnce(mockResponse);

    render(<ChatInterface onConversationCreated={mockOnConversationCreated} />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await userEvent.type(input, "Test message");

    const sendButton = screen.getByLabelText("Send message");
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockOnConversationCreated).toHaveBeenCalledWith(1);
    });
  });

  it("sends message with Enter key (without Shift)", async () => {
    const mockResponse = {
      message: {
        id: 2,
        conversation_id: 1,
        role: "assistant" as const,
        content: "Response",
        created_at: new Date().toISOString(),
      },
      conversation_id: 1,
    };

    mockSendChatMessage.mockResolvedValueOnce(mockResponse);

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await userEvent.type(input, "Test message");

    // Press Enter without Shift
    fireEvent.keyPress(input, { key: "Enter", shiftKey: false });

    await waitFor(() => {
      expect(mockSendChatMessage).toHaveBeenCalled();
    });
  });

  it("dismisses error message when close button is clicked", async () => {
    mockSendChatMessage.mockRejectedValueOnce(new Error("Test error"));

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/Type your message/i);
    await userEvent.type(input, "Test message");

    const sendButton = screen.getByLabelText("Send message");
    fireEvent.click(sendButton);

    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText("Test error")).toBeInTheDocument();
    });

    // Click dismiss button
    const dismissButton = screen.getByLabelText("Dismiss error");
    fireEvent.click(dismissButton);

    // Error should be gone
    await waitFor(() => {
      expect(screen.queryByText("Test error")).not.toBeInTheDocument();
    });
  });
});
