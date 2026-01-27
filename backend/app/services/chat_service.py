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
import re
from datetime import datetime, timedelta
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
        self.model = os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")

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
        print(f"[DEBUG] ChatService.send_message called with user_id: '{user_id}'")
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

        # Step 4.5: Execute tools BEFORE calling AI (so AI can see results)
        tool_calls_metadata, conversation_state = await self._parse_and_execute_tools(
            user_id=user_id,
            ai_response="",  # Not used for intent detection
            user_message=request.message,
            conversation_id=conversation.id,
            session=session
        )

        # Step 4.6: If tools were executed, add results to conversation history
        if tool_calls_metadata:
            # Add tool results as system message for AI to see
            tool_results_text = self._format_tool_results(tool_calls_metadata, detected_language)
            conversation_history.append({
                "role": "system",
                "content": f"Tool execution results:\n{tool_results_text}"
            })

        # Step 5: Call OpenRouter API (AI can now see tool results)
        system_prompt = self._build_system_prompt(detected_language)
        ai_response_text = await self._call_openrouter_simple(
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
                "tool_calls": tool_calls_metadata,
                "conversation_state": conversation_state  # Save state for multi-turn dialogues
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
- Add new tasks (with priority: High/Medium/Low and category: Personal/Work/Shopping)
- List their tasks
- Mark tasks as completed
- Delete tasks
- Update task details

When adding a task, ask for missing information step by step:
1. Task title (required)
2. Due date (optional - ask "Kab tak complete karna hai?")
3. Priority (optional - ask "Priority kya hai? High, Medium, ya Low?")
4. Category (optional - ask "Category? Personal, Work, Shopping, ya koi aur?")

Be conversational and friendly. Keep questions short and clear.
Always respond in Urdu when the user speaks Urdu."""
        else:
            return """You are a helpful task management assistant. You help users manage their todo tasks through natural conversation.

You can help users:
- Add new tasks (with priority: High/Medium/Low and category: Personal/Work/Shopping)
- List their tasks
- Mark tasks as completed
- Delete tasks
- Update task details

When adding a task, ask for missing information step by step:
1. Task title (required)
2. Due date (optional - ask "When do you need this done?")
3. Priority (optional - ask "What's the priority? High, Medium, or Low?")
4. Category (optional - ask "What category? Personal, Work, Shopping, or something else?")

Be conversational and friendly. Keep questions short and clear."""

    async def _call_openrouter_simple(
        self,
        user_id: str,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        user_message: str
    ) -> str:
        """Call OpenRouter API without tool execution (tools already executed).

        Args:
            user_id: User ID for MCP tool calls
            system_prompt: System prompt for the AI
            conversation_history: Previous messages in conversation (may include tool results)
            user_message: Current user message

        Returns:
            AI response text

        Raises:
            HTTPException: If OpenRouter API call fails
        """
        from fastapi import HTTPException, status

        try:
            # Build messages array
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add conversation history (may include tool results)
            if conversation_history:
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

            return ai_response

        except Exception as e:
            # Log error (in production, use proper logging)
            print(f"OpenRouter API error: {str(e)}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI service temporarily unavailable. Please try again."
            )

    def _format_tool_results(self, tool_calls: List[Dict[str, Any]], language: str = "english") -> str:
        """Format tool execution results for AI to understand.

        Args:
            tool_calls: List of tool call results
            language: Language for formatting ("english" or "urdu")

        Returns:
            Formatted string with tool results
        """
        if not tool_calls:
            return "کوئی ٹولز استعمال نہیں ہوئے۔" if language == "urdu" else "No tools were executed."

        formatted_results = []
        for call in tool_calls:
            tool_name = call.get("tool", "unknown")
            success = call.get("success", False)

            if success:
                result = call.get("result", {})

                if tool_name == "list_tasks":
                    # Format task list nicely with sequential positions
                    tasks = result.get("tasks", [])
                    count = result.get("count", 0)

                    if count == 0:
                        msg = "صارف کے پاس کوئی کام نہیں ہے۔" if language == "urdu" else "User has no tasks."
                        formatted_results.append(f"✓ {tool_name}: {msg}")
                    else:
                        task_list = []
                        for position, task in enumerate(tasks[:10], 1):  # Show first 10 with positions
                            title = task.get("title", "Untitled")
                            completed = task.get("completed", False)
                            status = "✓" if completed else "○"
                            priority = task.get("priority", "medium")
                            category = task.get("category", "")

                            # Use sequential position (1, 2, 3) for user-friendly display
                            task_str = f"{position}. {status} {title}"
                            if priority:
                                priority_label = "ترجیح" if language == "urdu" else "Priority"
                                task_str += f" [{priority_label}: {priority}]"
                            if category:
                                category_label = "زمرہ" if language == "urdu" else "Category"
                                task_str += f" [{category_label}: {category}]"

                            task_list.append(task_str)

                        found_msg = f"ملے {count} کام" if language == "urdu" else f"Found {count} tasks"
                        formatted_results.append(
                            f"✓ {tool_name}: {found_msg}:\n" + "\n".join(task_list)
                        )

                elif tool_name == "add_task":
                    # Format task creation result
                    task = result.get("task", {})
                    title = task.get("title", "Untitled")
                    msg = f"کام '{title}' کامیابی سے بنایا گیا" if language == "urdu" else f"Successfully created task '{title}'"
                    formatted_results.append(f"✓ {tool_name}: {msg}")

                elif tool_name == "complete_task":
                    # Format task completion result
                    task = result.get("task", {})
                    title = task.get("title", "Untitled")
                    msg = f"کام '{title}' مکمل ہو گیا" if language == "urdu" else f"Successfully completed task '{title}'"
                    formatted_results.append(f"✓ {tool_name}: {msg}")

                elif tool_name == "delete_task":
                    # Format task deletion result
                    msg = "کام کامیابی سے حذف ہو گیا" if language == "urdu" else "Task deleted successfully"
                    formatted_results.append(f"✓ {tool_name}: {msg}")

                else:
                    # Generic success message
                    msg = "کامیاب" if language == "urdu" else "Success"
                    formatted_results.append(f"✓ {tool_name}: {msg}")
            else:
                # Tool failed
                error = call.get("error", "Unknown error")
                failed_msg = "ناکام" if language == "urdu" else "Failed"
                formatted_results.append(f"✗ {tool_name}: {failed_msg} - {error}")

        return "\n".join(formatted_results)

    async def _parse_and_execute_tools(
        self,
        user_id: str,
        ai_response: str,
        user_message: str,
        conversation_id: UUID,
        session: AsyncSession
    ) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Parse AI response for tool calls and execute them.

        This method detects user intent, manages conversation state for multi-turn
        dialogues, and executes MCP tools when sufficient information is collected.

        Args:
            user_id: User ID for MCP tool calls
            ai_response: AI response text
            user_message: Original user message
            conversation_id: Current conversation ID
            session: Database session

        Returns:
            Tuple of (tool call results, conversation state to persist)

        Reference: T027 - Implement MCP tool calling logic
        """
        tool_calls = []
        conversation_state = None

        # Step 1: Detect intent from user message
        intent = self._detect_intent(user_message)
        print(f"[DEBUG] Detected intent: {intent}")

        # Step 2: Get previous conversation state from last assistant message
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.role == MessageRole.ASSISTANT)
            .order_by(Message.timestamp.desc())
            .limit(1)
        )
        result = await session.exec(query)
        last_assistant_msg = result.first()

        current_state = None
        if last_assistant_msg and last_assistant_msg.meta_data:
            current_state = last_assistant_msg.meta_data.get("conversation_state")

        print(f"[DEBUG] Current state from previous message: {current_state}")

        # Step 3: Handle adding_task intent
        if intent == "adding_task" or (current_state and current_state.get("intent") == "adding_task"):
            # Extract task information from user message
            task_info = self._extract_task_info(user_message, current_state)
            task_info["intent"] = "adding_task"

            print(f"[DEBUG] Task info extracted: {task_info}")
            print(f"[DEBUG] Is complete: {self._is_task_info_complete(task_info)}")

            # Check if we have enough information to create the task
            if self._is_task_info_complete(task_info):
                # We have at least a title, create the task
                print(f"[DEBUG] Creating task with info: {task_info}")

                # Generate description if not provided
                description = task_info.get("description")
                if not description:
                    # Auto-generate description from task details
                    desc_parts = []
                    if task_info.get("priority"):
                        desc_parts.append(f"Priority: {task_info['priority'].capitalize()}")
                    if task_info.get("category"):
                        desc_parts.append(f"Category: {task_info['category'].capitalize()}")
                    if task_info.get("due_date"):
                        desc_parts.append(f"Due: {task_info['due_date'][:10]}")

                    if desc_parts:
                        description = " | ".join(desc_parts)

                try:
                    result = await call_tool(
                        name="add_task",
                        arguments={
                            "user_id": user_id,
                            "title": task_info["title"],
                            "description": description,
                            "due_date": task_info.get("due_date"),
                            "priority": task_info.get("priority", "medium"),
                            "category": task_info.get("category")
                        }
                    )

                    print(f"[DEBUG] MCP tool result: {result}")

                    tool_calls.append({
                        "tool": "add_task",
                        "success": result.get("success", False),
                        "result": result
                    })

                    # Clear conversation state after successful task creation
                    conversation_state = None
                    return tool_calls, conversation_state

                except Exception as e:
                    print(f"[DEBUG] Error calling add_task: {str(e)}")
                    tool_calls.append({
                        "tool": "add_task",
                        "success": False,
                        "error": str(e)
                    })
                    return tool_calls, None
            else:
                # Task info incomplete, save state for next turn
                print(f"[DEBUG] Task info incomplete, saving state: {task_info}")
                conversation_state = task_info
                return tool_calls, conversation_state

        # Step 4: Handle listing_tasks intent
        elif intent == "listing_tasks":
            try:
                print(f"[DEBUG] Calling list_tasks with user_id: '{user_id}'")
                result = await call_tool(
                    name="list_tasks",
                    arguments={
                        "user_id": user_id,
                        "status": "all",
                        "limit": 100
                    }
                )

                print(f"[DEBUG] list_tasks result: success={result.get('success')}, count={result.get('count', 0)}")

                # Save position→ID mapping in conversation state
                if result.get('success') and result.get('tasks'):
                    tasks = result['tasks']
                    task_mapping = {}
                    for position, task in enumerate(tasks, 1):
                        task_id = task.get('id')
                        if task_id:
                            task_mapping[position] = int(task_id)

                    # Store mapping with timestamp
                    conversation_state = {
                        "task_mapping": task_mapping,
                        "mapping_created_at": datetime.utcnow().isoformat(),
                        "task_count": len(tasks)
                    }
                    print(f"[DEBUG] Saved task mapping: {task_mapping}")
                else:
                    conversation_state = None

                tool_calls.append({
                    "tool": "list_tasks",
                    "success": result.get("success", False),
                    "result": result
                })

                return tool_calls, conversation_state

            except Exception as e:
                print(f"[DEBUG] Error in list_tasks: {str(e)}")
                tool_calls.append({
                    "tool": "list_tasks",
                    "success": False,
                    "error": str(e)
                })
                return tool_calls, None

        # Step 5: Handle completing_task intent
        elif intent == "completing_task":
            # Resolve task reference (position, title, or ID)
            task_id = await self._resolve_task_reference(
                user_message=user_message,
                user_id=user_id,
                current_state=current_state,
                session=session
            )

            if task_id:
                print(f"[DEBUG] Resolved task_id: {task_id}")
                try:
                    result = await call_tool(
                        name="complete_task",
                        arguments={
                            "user_id": user_id,
                            "task_id": str(task_id)
                        }
                    )

                    print(f"[DEBUG] complete_task result: {result}")

                    tool_calls.append({
                        "tool": "complete_task",
                        "success": result.get("success", False),
                        "result": result
                    })

                except Exception as e:
                    print(f"[DEBUG] Error calling complete_task: {str(e)}")
                    tool_calls.append({
                        "tool": "complete_task",
                        "success": False,
                        "error": str(e)
                    })
            else:
                print(f"[DEBUG] Could not resolve task reference from message")
                tool_calls.append({
                    "tool": "complete_task",
                    "success": False,
                    "error": "Could not identify which task to complete. Please list your tasks first or specify the task by name."
                })

            # Preserve conversation state (don't lose the mapping!)
            return tool_calls, current_state

        # Step 6: Handle deleting_task intent
        elif intent == "deleting_task":
            # Resolve task reference (position, title, or ID)
            task_id = await self._resolve_task_reference(
                user_message=user_message,
                user_id=user_id,
                current_state=current_state,
                session=session
            )

            if task_id:
                print(f"[DEBUG] Resolved task_id: {task_id}")
                try:
                    result = await call_tool(
                        name="delete_task",
                        arguments={
                            "user_id": user_id,
                            "task_id": str(task_id)
                        }
                    )

                    print(f"[DEBUG] delete_task result: {result}")

                    tool_calls.append({
                        "tool": "delete_task",
                        "success": result.get("success", False),
                        "result": result
                    })

                except Exception as e:
                    print(f"[DEBUG] Error calling delete_task: {str(e)}")
                    tool_calls.append({
                        "tool": "delete_task",
                        "success": False,
                        "error": str(e)
                    })
            else:
                print(f"[DEBUG] Could not resolve task reference from message")
                tool_calls.append({
                    "tool": "delete_task",
                    "success": False,
                    "error": "Could not identify which task to delete. Please list your tasks first or specify the task by name."
                })

            # Preserve conversation state (don't lose the mapping!)
            return tool_calls, current_state

        return tool_calls, conversation_state

    async def _resolve_task_reference(
        self,
        user_message: str,
        user_id: str,
        current_state: Optional[Dict[str, Any]],
        session: AsyncSession
    ) -> Optional[int]:
        """Resolve task reference from user message.

        Supports three methods:
        1. By position: "task 1", "task 2" (uses mapping from conversation state)
        2. By title: "jjs task", "the lunch task" (searches by title)
        3. By ID: "task 36" (direct database ID)

        Priority order: Position > Title > ID

        Args:
            user_message: User's message
            user_id: User ID for task lookup
            current_state: Current conversation state with task mapping
            session: Database session

        Returns:
            Task ID (int) or None if not found
        """
        print(f"[DEBUG] _resolve_task_reference called with message: '{user_message}'")

        # Extract number from message (e.g., "task 1", "task 36")
        number_match = re.search(r'\b(?:task|id)\s*#?(\d+)\b', user_message, re.IGNORECASE)
        number = int(number_match.group(1)) if number_match else None

        # Extract title/text from message ONLY if no number pattern found
        title = None
        if not number:
            # Try multiple patterns for title extraction
            title_patterns = [
                r'(?:complete|delete|mark|finish)\s+(?:the\s+)?([a-zA-Z][a-zA-Z0-9\s]+?)\s+(?:task|as)',  # "complete jjs task"
                r'(?:complete|delete|mark|finish)\s+([a-zA-Z][a-zA-Z0-9\s]+)$',  # "complete jjs"
            ]

            for pattern in title_patterns:
                title_match = re.search(pattern, user_message, re.IGNORECASE)
                if title_match:
                    title = title_match.group(1).strip()
                    break

        print(f"[DEBUG] Extracted - number: {number}, title: '{title}'")

        # Get task mapping from conversation state
        # Note: JSON serialization converts int keys to strings, so we need to convert back
        task_mapping_raw = current_state.get('task_mapping', {}) if current_state else {}
        task_mapping = {}
        if task_mapping_raw:
            # Convert string keys back to integers
            for key, value in task_mapping_raw.items():
                try:
                    task_mapping[int(key)] = value
                except (ValueError, TypeError):
                    pass

        task_count = current_state.get('task_count', 0) if current_state else 0

        print(f"[DEBUG] Task mapping (converted): {task_mapping}, task_count: {task_count}")

        # Priority 1: Position (if number is in valid range and mapping exists)
        if number and task_mapping and 1 <= number <= task_count:
            # Convert position to actual ID using mapping
            task_id = task_mapping.get(number)
            if task_id:
                print(f"[DEBUG] Resolved by POSITION: {number} → ID {task_id}")
                return task_id

        # Priority 2: Title (if text pattern found)
        if title:
            print(f"[DEBUG] Attempting title search for: '{title}'")
            task_id = await self._search_task_by_title(user_id, title, session)
            if task_id:
                print(f"[DEBUG] Resolved by TITLE: '{title}' → ID {task_id}")
                return task_id

        # Priority 3: Direct ID (if number exists and is larger than task count)
        if number and (not task_mapping or number > task_count):
            print(f"[DEBUG] Resolved by DIRECT ID: {number}")
            return number

        print(f"[DEBUG] Could not resolve task reference")
        return None

    async def _search_task_by_title(
        self,
        user_id: str,
        title_query: str,
        session: AsyncSession
    ) -> Optional[int]:
        """Search for a task by title (case-insensitive, partial match).

        Args:
            user_id: User ID for filtering
            title_query: Title to search for
            session: Database session

        Returns:
            Task ID if found, None otherwise
        """
        from models import Task  # Correct import path
        from sqlmodel import select

        try:
            # Search for tasks with matching title (case-insensitive)
            query = select(Task).where(
                Task.user_id == user_id,
                Task.title.ilike(f"%{title_query}%")  # Partial match
            ).limit(5)  # Limit to 5 matches

            result = await session.exec(query)
            tasks = result.all()

            if not tasks:
                print(f"[DEBUG] No tasks found matching title: '{title_query}'")
                return None

            if len(tasks) == 1:
                # Exact match found
                print(f"[DEBUG] Found 1 task matching '{title_query}': ID {tasks[0].id}")
                return tasks[0].id

            # Multiple matches - try exact match first
            for task in tasks:
                if task.title.lower() == title_query.lower():
                    print(f"[DEBUG] Found exact match for '{title_query}': ID {task.id}")
                    return task.id

            # Return first match if no exact match
            print(f"[DEBUG] Multiple matches for '{title_query}', returning first: ID {tasks[0].id}")
            return tasks[0].id

        except Exception as e:
            print(f"[DEBUG] Error searching task by title: {str(e)}")
            return None

    def _detect_intent(self, message: str) -> Optional[str]:
        """Detect user intent from message.

        Args:
            message: User message text

        Returns:
            Intent string or None (adding_task, listing_tasks, completing_task, deleting_task, etc.)
        """
        message_lower = message.lower()

        print(f"[DEBUG] _detect_intent called with message: '{message_lower}'")

        # Check delete patterns FIRST (before list patterns to avoid conflicts)
        delete_patterns = [
            # English patterns
            r'\bdelete\b.*\btask\b',
            r'\bremove\b.*\btask\b',
            r'\btask\b.*\bdelete\b',
            r'\btask\b.*\bremove\b',
            r'\bdelete\b\s+(?:the\s+)?[a-zA-Z]',  # "delete buy", "delete the lunch"
            r'\bremove\b\s+(?:the\s+)?[a-zA-Z]',  # "remove buy", "remove the lunch"

            # Romanized Urdu patterns
            r'\bkaam\b.*\bdelete\b',
            r'\bkaam\b.*\bhatao\b',
            r'\bhatao\b.*\btask\b',

            # Urdu script patterns
            r'حذف.*کام',  # "hazf kaam" (delete task)
            r'کام.*حذف',  # "kaam hazf" (task delete)
            r'ہٹا.*کام',  # "hata kaam" (remove task)
            r'کام.*ہٹا',  # "kaam hata" (task remove)
            r'ڈیلیٹ.*کام',  # "delete kaam"
            r'کام.*ڈیلیٹ',  # "kaam delete"
        ]

        for pattern in delete_patterns:
            if re.search(pattern, message_lower):
                print(f"[DEBUG] Matched delete_pattern: {pattern}")
                return "deleting_task"

        # Check complete patterns SECOND (before list patterns)
        complete_patterns = [
            # English patterns
            r'\bcomplete\b.*\btask\b',
            r'\bmark\b.*\b(?:done|completed)\b',
            r'\bmark\b.*\btask\b.*\b(?:done|completed|complete)\b',
            r'\bfinish\b.*\btask\b',
            r'\btask\b.*\bcomplete\b',
            r'\btask\b.*\bdone\b',

            # Romanized Urdu patterns
            r'\bkaam\b.*\bho\s*gaya\b',
            r'\bkaam\b.*\bcomplete\b',

            # Urdu script patterns
            r'مکمل.*کام',  # "mukammal kaam" (complete task)
            r'کام.*مکمل',  # "kaam mukammal" (task complete)
            r'ہو.*گیا',  # "ho gaya" (done)
            r'ختم.*کام',  # "khatam kaam" (finish task)
            r'کام.*ختم',  # "kaam khatam" (task finish)
            r'کام.*ہو.*گیا',  # "kaam ho gaya" (task done)
        ]

        for pattern in complete_patterns:
            if re.search(pattern, message_lower):
                print(f"[DEBUG] Matched complete_pattern: {pattern}")
                return "completing_task"

        # Add task patterns (English, Romanized Urdu, and Urdu script)
        add_patterns = [
            # English patterns
            r'\badd\b.*\btask\b',
            r'\bcreate\b.*\btask\b',
            r'\bnew\b.*\btask\b',
            r'\btask\b.*\badd\b',

            # Romanized Urdu patterns
            r'\bkaam\b.*\badd\b',
            r'\btask\b.*\bbanao\b',
            r'\bnayi\b.*\btask\b',
            r'\bnaya\b.*\bkaam\b',

            # Urdu script patterns - flexible matching for natural speech
            r'نیا.*کام',  # "naya kaam" (new task)
            r'کام.*شامل',  # "kaam shamil" (add task)
            r'شامل.*کام',  # "shamil kaam" (add task)
            r'کام.*بنا',  # "kaam bana" (create task)
            r'بنا.*کام',  # "bana kaam" (create task)
            r'کام.*ایڈ',  # "kaam add"
            r'ایڈ.*کام',  # "add kaam"

            # Natural Urdu speech patterns with ٹاسک (task)
            r'ٹاسک.*ڈال',  # "task daal" (add task)
            r'ڈال.*ٹاسک',  # "daal task"
            r'ٹاسک.*میں.*ڈال',  # "task mein daal" (add to task)
            r'ٹاسک.*شامل',  # "task shamil"
            r'شامل.*ٹاسک',  # "shamil task"
            r'ٹاسک.*بنا',  # "task bana"
            r'بنا.*ٹاسک',  # "bana task"

            # More natural variations with کام
            r'کام.*ڈال',  # "kaam daal"
            r'ڈال.*کام',  # "daal kaam"
            r'میں.*ڈال',  # "mein daal" (add in)
        ]

        for pattern in add_patterns:
            if re.search(pattern, message_lower):
                print(f"[DEBUG] Matched add_pattern: {pattern}")
                return "adding_task"

        # List tasks patterns (English, Romanized Urdu, and Urdu script) - CHECK LAST to avoid conflicts
        list_patterns = [
            # English patterns
            r'\blist\b.*\btask',
            r'\bshow\b.*\btask',
            r'\bmy\b.*\btask',
            r'\bview\b.*\btask',
            r'\bsee\b.*\btask',
            r'\bhow\s+many\b.*\btask',
            r'\btask.*\blist',

            # Romanized Urdu patterns
            r'\btask\b.*\bdikhao\b',
            r'\bmeray\b.*\bkaam\b',
            r'\bmere\b.*\btask',  # "mere task"
            r'\bkitne\b.*\btask',  # "kitne task"
            r'\bkitnay\b.*\btask',  # "kitnay task"
            r'\btask\b.*\bhein',  # "task hein"
            r'\btask\b.*\bhai',  # "task hai"
            r'\bkaam\b.*\bdikhao',  # "kaam dikhao"
            r'\bkaam\b.*\bhein',  # "kaam hein"

            # Urdu script patterns
            r'کام.*دکھا',  # "kaam dikhao" (show tasks)
            r'دکھا.*کام',  # "dikhao kaam" (show tasks)
            r'میرے.*کام',  # "mere kaam" (my tasks)
            r'کام.*کتنے',  # "kaam kitne" (how many tasks)
            r'کتنے.*کام',  # "kitne kaam" (how many tasks)
            r'کام.*ہیں',  # "kaam hain" (tasks are)
            r'کام.*لسٹ',  # "kaam list"
            r'لسٹ.*کام',  # "list kaam"
        ]

        for pattern in list_patterns:
            if re.search(pattern, message_lower):
                print(f"[DEBUG] Matched list_pattern: {pattern}")
                return "listing_tasks"

        print(f"[DEBUG] No intent pattern matched")
        return None

    def _extract_task_info(self, message: str, current_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract task information from user message.

        Args:
            message: User message text
            current_state: Current conversation state (if any)

        Returns:
            Dictionary with extracted task information
        """
        info = current_state.copy() if current_state else {}

        # Extract title if not already set
        if "title" not in info or not info["title"]:
            # First, try to extract from structured format "Task Title: ..." or "Title: ..."
            title_structured = re.search(r'(?:task\s+)?title\s*[:\-]\s*(.+?)(?:\n|$|,\s*(?:due|priority|category))', message, re.IGNORECASE)
            if title_structured:
                info["title"] = title_structured.group(1).strip()
            else:
                # Try Urdu patterns for title extraction - natural speech
                urdu_title_patterns = [
                    r'نام\s+ہے\s+(.+?)(?:\s*$)',  # "naam hai X" (name is X)
                    r'کام\s+کا\s+نام\s+ہے\s+(.+?)(?:\s*$)',  # "kaam ka naam hai X" (task name is X)
                    r'(?:نیا|نئی)\s+کام\s+(.+?)(?:\s*$)',  # "naya kaam X" (new task X)

                    # Natural speech patterns - extract task from context
                    r'مجھے\s+(.+?)\s+(?:ہے|بنانی\s+ہے|کرنی\s+ہے|کرنا\s+ہے)',  # "mujhe X hai/banana hai/karna hai"
                    r'میں\s+(.+?)\s+(?:بناؤں|کروں|کرنا)',  # "mein X banao/karo/karna"
                    r'(.+?)\s+(?:بنانی\s+ہے|کرنی\s+ہے|کرنا\s+ہے)',  # "X banana hai/karna hai"
                ]

                for pattern in urdu_title_patterns:
                    match = re.search(pattern, message)
                    if match:
                        title = match.group(1).strip()
                        # Clean up temporal words that might be captured
                        title = re.sub(r'\s*(?:کل|آج|اگلے|ہفتے|میرا|میرے|مجھے)\s*', ' ', title).strip()
                        if title and len(title) > 2:  # Ensure we have a meaningful title
                            info["title"] = title
                            break

                # Try English patterns if Urdu didn't match
                if "title" not in info:
                    title_patterns = [
                        # Match "add task to X" but stop before temporal/priority/category words
                        r'(?:add|create|new)\s+(?:task|kaam)\s+(?:to|for)?\s*(.+?)(?:\s+(?:tomorrow|today|next week|yesterday|with|in|for|by|on|at|high|medium|low|personal|work|shopping)|\s*$)',
                        r'task\s+(?:add|banao)\s+(?:karo?)?\s*[:-]?\s*(.+?)(?:\s+(?:tomorrow|today|next week|yesterday|with|in|for|by|on|at|high|medium|low|personal|work|shopping)|\s*$)',
                    ]
                    for pattern in title_patterns:
                        match = re.search(pattern, message, re.IGNORECASE)
                        if match:
                            title = match.group(1).strip()
                            # Clean up common endings and extra words
                            title = re.sub(r'\s+(please|plz|kar\s*do|kar\s*dein|tomorrow|today|with|in).*$', '', title, flags=re.IGNORECASE)
                            title = title.strip()
                            if title:
                                info["title"] = title
                                break

                # If no pattern matched and we're in adding_task state, use the whole message as title
                if "title" not in info and current_state and current_state.get("intent") == "adding_task":
                    # Clean the message - remove other field labels if present
                    cleaned = re.sub(r'(?:due\s+date|priority|category)\s*[:\-].*', '', message, flags=re.IGNORECASE)
                    # Remove Urdu date/time words and common phrases
                    cleaned = re.sub(r'(?:آج|کل|اگلے|ہفتے|پکانی|ہے|کرنا|کرنی|مجھے|میرا|میرے|ٹاسک|میں|ڈالو).*$', '', cleaned)
                    cleaned = cleaned.strip()
                    if cleaned and len(cleaned) > 2:
                        info["title"] = cleaned

        # Extract priority - check structured format first
        priority_structured = re.search(r'priority\s*[:\-]\s*(high|medium|low)', message, re.IGNORECASE)
        if priority_structured:
            info["priority"] = priority_structured.group(1).lower()
        else:
            # Check for English and Urdu priority terms
            priority_patterns = [
                (r'\b(high|medium|low)\b', {'high': 'high', 'medium': 'medium', 'low': 'low'}),
                (r'(اعلیٰ|بلند|زیادہ)', {'اعلیٰ': 'high', 'بلند': 'high', 'زیادہ': 'high'}),
                (r'(درمیانہ|عام)', {'درمیانہ': 'medium', 'عام': 'medium'}),
                (r'(کم|نیچے)', {'کم': 'low', 'نیچے': 'low'}),
            ]
            for pattern, mapping in priority_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    matched_text = match.group(1).lower()
                    info["priority"] = mapping.get(matched_text, matched_text)
                    break

        # Extract category - check structured format first
        category_structured = re.search(r'category\s*[:\-]\s*(\w+)', message, re.IGNORECASE)
        if category_structured:
            info["category"] = category_structured.group(1).lower()
        else:
            # Check for English and Urdu category terms
            category_patterns = [
                (r'\b(personal|work|shopping)\b', {'personal': 'personal', 'work': 'work', 'shopping': 'shopping'}),
                (r'(ذاتی|پرسنل)', {'ذاتی': 'personal', 'پرسنل': 'personal'}),
                (r'(کام|ورک|دفتر)', {'کام': 'work', 'ورک': 'work', 'دفتر': 'work'}),
                (r'(خریداری|شاپنگ|بازار)', {'خریداری': 'shopping', 'شاپنگ': 'shopping', 'بازار': 'shopping'}),
            ]
            for pattern, mapping in category_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    matched_text = match.group(1).lower()
                    info["category"] = mapping.get(matched_text, matched_text)
                    break

        # Extract due date - check structured format first
        due_date_structured = re.search(r'due\s+date\s*[:\-]\s*(.+?)(?:\n|$|,\s*(?:priority|category))', message, re.IGNORECASE)
        if due_date_structured:
            due_date_text = due_date_structured.group(1).strip()
            due_date = self._parse_natural_date(due_date_text)
            if due_date:
                info["due_date"] = due_date
        else:
            # Try natural language parsing
            due_date = self._parse_natural_date(message)
            if due_date:
                info["due_date"] = due_date

        return info

    def _parse_natural_date(self, text: str) -> Optional[str]:
        """Parse natural language date expressions in English and Urdu.

        Args:
            text: Text containing date expression

        Returns:
            ISO 8601 date string or None
        """
        text_lower = text.lower()
        today = datetime.now()

        # Today - English and Urdu
        if re.search(r'\btoday\b|\bآج\b|\baaj\b', text_lower):
            return today.isoformat()

        # Tomorrow - English and Urdu
        if re.search(r'\btomorrow\b|\bکل\b|\bkal\b', text_lower):
            date = today + timedelta(days=1)
            return date.isoformat()

        # Next week - English and Urdu
        if re.search(r'\bnext\s+week\b|\bاگلے\s+ہفتے\b|\bagle\s+hafte\b', text_lower):
            date = today + timedelta(days=7)
            return date.isoformat()

        # Specific weekdays (next occurrence) - English and Romanized Urdu
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6,
            'peer': 0, 'mangal': 1, 'budh': 2, 'jumerat': 3,
            'juma': 4, 'hafta': 5, 'itwaar': 6
        }

        for day_name, day_num in weekdays.items():
            if day_name in text_lower:
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                date = today + timedelta(days=days_ahead)
                return date.isoformat()

        # Urdu weekdays (script)
        urdu_weekdays = {
            'پیر': 0, 'منگل': 1, 'بدھ': 2, 'جمعرات': 3,
            'جمعہ': 4, 'ہفتہ': 5, 'اتوار': 6
        }

        for day_name, day_num in urdu_weekdays.items():
            if day_name in text:
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                date = today + timedelta(days=days_ahead)
                return date.isoformat()

        # ISO date format (YYYY-MM-DD)
        iso_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
        if iso_match:
            return iso_match.group(1) + "T00:00:00Z"

        return None

    def _get_conversation_state(self, conversation_history: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """Get conversation state from the last assistant message metadata.

        Args:
            conversation_history: List of previous messages

        Returns:
            Conversation state dict or None
        """
        # Look for state in the last assistant message
        # In practice, we'd retrieve this from the database Message.meta_data
        # For now, return None (state will be managed in the main flow)
        return None

    def _is_task_info_complete(self, task_info: Dict[str, Any]) -> bool:
        """Check if we have all required information to create a task.

        Args:
            task_info: Task information dictionary

        Returns:
            True if we have at least a title
        """
        return "title" in task_info and task_info["title"]

    def _get_next_question(self, task_info: Dict[str, Any], language: str) -> Optional[str]:
        """Determine what question to ask next based on missing information.

        Args:
            task_info: Current task information
            language: User's language

        Returns:
            Next question to ask or None if all info collected
        """
        if "due_date" not in task_info:
            if language == "urdu":
                return "Kab tak complete karna hai? (tomorrow, next week, ya specific date)"
            else:
                return "When do you need this done? (tomorrow, next week, or a specific date)"

        if "priority" not in task_info:
            if language == "urdu":
                return "Priority kya hai? (High / Medium / Low)"
            else:
                return "What's the priority? (High / Medium / Low)"

        if "category" not in task_info:
            if language == "urdu":
                return "Category? (Personal / Work / Shopping, ya skip karein)"
            else:
                return "What category? (Personal / Work / Shopping, or skip)"

        return None


# Global service instance
chat_service = ChatService()
