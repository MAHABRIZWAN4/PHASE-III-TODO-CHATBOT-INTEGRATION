"""Chat service for handling AI-powered conversations.

This service manages chat interactions with the OpenRouter API, including:
- Conversation creation and management
- Message persistence
- OpenRouter API integration
- MCP tool orchestration

Reference: T024-T027 from specs/003-ai-todo-chatbot/tasks.md
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from dotenv import load_dotenv
from openai import AsyncOpenAI
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse
from app.utils.language import detect_language
from mcp_server.task_tools import call_tool

# Load environment variables
load_dotenv()


class ChatService:
    """Service for managing AI chat conversations.

    This service handles all chat-related operations including conversation
    management, message persistence, OpenRouter API calls, and MCP tool execution.

    Attributes:
        openai_client: AsyncOpenAI client configured for OpenRouter
        model: OpenRouter model identifier
        max_tokens: Maximum tokens for AI responses
        temperature: Sampling temperature for AI responses

    Reference: T024 - Implement ChatService with OpenRouter client
    """

    def __init__(self):
        """Initialize ChatService with OpenRouter client.

        Raises:
            ValueError: If OPENROUTER_API_KEY is not set in environment

        Reference: T024 - Initialize OpenRouter client with API key from env
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is not set. "
                "Please set it in your .env file."
            )

        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("OPENROUTER_MODEL", "xiaomi/mimo-v2-flash:free")

        # Initialize OpenAI client with OpenRouter configuration
        self.openai_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        # Configuration
        self.max_tokens = 1000
        self.temperature = 0.7
        self.max_conversation_history = 10  # Limit context window

    async def send_message(
        self,
        user_id: str,
        request: ChatRequest,
        session: AsyncSession
    ) -> ChatResponse:
        """Process a chat message and return AI response.

        This method orchestrates the entire chat flow:
        1. Create or retrieve conversation
        2. Save user message
        3. Build conversation context
        4. Call OpenRouter API
        5. Parse response and execute MCP tools if needed
        6. Save assistant response
        7. Return ChatResponse

        Args:
            user_id: Authenticated user ID
            request: ChatRequest with message and optional conversation_id
            session: Database session

        Returns:
            ChatResponse with conversation_id, message_id, response, and metadata

        Raises:
            HTTPException: For various error conditions (conversation not found, API errors, etc.)

        Reference: T024 - Implement send_message() method with OpenRouter API calls
        """
        # Step 1: Get or create conversation (T025)
        conversation = await self._get_or_create_conversation(
            user_id=user_id,
            conversation_id=request.conversation_id,
            session=session
        )

        # Step 2: Detect language from user message
        detected_language = detect_language(request.message)

        # Step 3: Save user message (T026)
        user_message = await self._save_message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message,
            metadata={"language": detected_language},
            session=session
        )

        # Step 4: Build conversation context
        conversation_history = await self._build_conversation_history(
            conversation_id=conversation.id,
            session=session
        )

        # Step 5: Call OpenRouter API
        system_prompt = self._build_system_prompt(detected_language)
        ai_response_text, tool_calls_metadata = await self._call_openrouter(
            user_id=user_id,
            system_prompt=system_prompt,
            conversation_history=conversation_history,
            user_message=request.message
        )

        # Step 6: Save assistant response (T026)
        assistant_message = await self._save_message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=ai_response_text,
            metadata={
                "language": detected_language,
                "model": self.model,
                "tool_calls": tool_calls_metadata
            },
            session=session
        )

        # Step 7: Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        await session.commit()

        # Step 8: Build and return response
        return ChatResponse(
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            response=ai_response_text,
            metadata={
                "tool_calls": tool_calls_metadata,
                "language": detected_language,
                "model": self.model
            }
        )

    async def _get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[UUID],
        session: AsyncSession
    ) -> Conversation:
        """Get existing conversation or create a new one.

        Args:
            user_id: User ID for ownership validation
            conversation_id: Optional conversation ID to retrieve
            session: Database session

        Returns:
            Conversation object (existing or newly created)

        Raises:
            HTTPException: If conversation_id provided but not found or doesn't belong to user

        Reference: T025 - Implement conversation creation logic
        """
        from fastapi import HTTPException, status

        if conversation_id:
            # Retrieve existing conversation
            conversation = await session.get(Conversation, conversation_id)

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )

            # Validate ownership
            if conversation.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized: Conversation does not belong to this user"
                )

            return conversation
        else:
            # Create new conversation
            new_conversation = Conversation(
                user_id=user_id
            )
            session.add(new_conversation)
            await session.commit()
            await session.refresh(new_conversation)
            return new_conversation

    async def _save_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]],
        session: AsyncSession
    ) -> Message:
        """Save a message to the database.

        Args:
            conversation_id: Conversation this message belongs to
            role: Message role (user, assistant, or system)
            content: Message text content
            metadata: Optional metadata (language, tool calls, etc.)
            session: Database session

        Returns:
            Saved Message object

        Reference: T026 - Implement message persistence logic
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            meta_data=metadata
        )

        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    async def _build_conversation_history(
        self,
        conversation_id: UUID,
        session: AsyncSession
    ) -> List[Dict[str, str]]:
        """Build conversation history for context window.

        Retrieves recent messages from the conversation and formats them
        for the OpenRouter API.

        Args:
            conversation_id: Conversation ID
            session: Database session

        Returns:
            List of message dicts with 'role' and 'content' keys

        Reference: T024 - Build conversation context for OpenRouter
        """
        # Query recent messages (limit to max_conversation_history)
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(self.max_conversation_history)
        )

        result = await session.exec(query)
        messages = result.all()

        # Reverse to get chronological order
        messages = list(reversed(messages))

        # Format for OpenRouter API
        history = []
        for msg in messages:
            history.append({
                "role": msg.role.value,
                "content": msg.content
            })

        return history

    def _build_system_prompt(self, language: str) -> str:
        """Build system prompt based on detected language.

        Args:
            language: Detected language ("english" or "urdu")

        Returns:
            System prompt string

        Reference: T024 - Language-aware system prompts
        """
        if language == "urdu":
            return """You are a helpful task management assistant. You help users manage their todo tasks through natural conversation in Urdu.

You can help users:
- Add new tasks
- List their tasks
- Mark tasks as completed
- Delete tasks
- Update task details

When a user asks you to perform a task operation, respond naturally in Urdu and indicate what action you would take.

Always respond in Urdu when the user speaks Urdu."""
        else:
            return """You are a helpful task management assistant. You help users manage their todo tasks through natural conversation.

You can help users:
- Add new tasks
- List their tasks
- Mark tasks as completed
- Delete tasks
- Update task details

When a user asks you to perform a task operation, respond naturally and indicate what action you would take.

Always be concise and helpful."""

    async def _call_openrouter(
        self,
        user_id: str,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        user_message: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Call OpenRouter API and parse response.

        Args:
            user_id: User ID for MCP tool calls
            system_prompt: System prompt for the AI
            conversation_history: Previous messages in conversation
            user_message: Current user message

        Returns:
            Tuple of (AI response text, tool calls metadata)

        Raises:
            HTTPException: If OpenRouter API call fails

        Reference: T024 - Implement OpenRouter API calls
        Reference: T027 - Implement MCP tool calling logic
        """
        from fastapi import HTTPException, status

        try:
            # Build messages array
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add conversation history (excluding the current user message which is already in history)
            # We only add history if it doesn't already include the current message
            if conversation_history and conversation_history[-1]["content"] != user_message:
                messages.extend(conversation_history)

            # Ensure the last message is the current user message
            if not messages or messages[-1]["content"] != user_message:
                messages.append({"role": "user", "content": user_message})

            # Call OpenRouter API
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract AI response
            ai_response = response.choices[0].message.content

            # Parse for tool calls (T027)
            tool_calls_metadata = await self._parse_and_execute_tools(
                user_id=user_id,
                ai_response=ai_response
            )

            return ai_response, tool_calls_metadata

        except Exception as e:
            # Log error (in production, use proper logging)
            print(f"OpenRouter API error: {str(e)}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI service temporarily unavailable. Please try again."
            )

    async def _parse_and_execute_tools(
        self,
        user_id: str,
        ai_response: str
    ) -> List[Dict[str, Any]]:
        """Parse AI response for tool calls and execute them.

        This method looks for tool call patterns in the AI response and
        executes the corresponding MCP tools.

        For now, this is a simplified implementation. In a production system,
        you would use function calling features of the AI model or implement
        more sophisticated parsing.

        Args:
            user_id: User ID for MCP tool calls
            ai_response: AI response text

        Returns:
            List of tool call results with metadata

        Reference: T027 - Implement MCP tool calling logic
        """
        tool_calls = []

        # Simple pattern matching for tool calls
        # In production, use AI function calling or more robust parsing

        # Example patterns:
        # - "add task: buy milk" -> call add_task
        # - "list tasks" -> call list_tasks
        # - "complete task 5" -> call complete_task
        # - "delete task 3" -> call delete_task

        # For now, return empty list (tool calling will be enhanced in future iterations)
        # The AI will respond naturally, and we'll add tool execution in a future enhancement

        return tool_calls


# Global service instance
chat_service = ChatService()
