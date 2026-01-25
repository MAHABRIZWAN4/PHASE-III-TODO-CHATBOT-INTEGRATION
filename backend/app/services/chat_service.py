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
            tool_results_text = self._format_tool_results(tool_calls_metadata)
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

    def _format_tool_results(self, tool_calls: List[Dict[str, Any]]) -> str:
        """Format tool execution results for AI to understand.

        Args:
            tool_calls: List of tool call results

        Returns:
            Formatted string with tool results
        """
        if not tool_calls:
            return "No tools were executed."

        formatted_results = []
        for call in tool_calls:
            tool_name = call.get("tool", "unknown")
            success = call.get("success", False)

            if success:
                result = call.get("result", {})

                if tool_name == "list_tasks":
                    # Format task list nicely
                    tasks = result.get("tasks", [])
                    count = result.get("count", 0)

                    if count == 0:
                        formatted_results.append(f"✓ {tool_name}: User has no tasks.")
                    else:
                        task_list = []
                        for i, task in enumerate(tasks[:10], 1):  # Show first 10
                            title = task.get("title", "Untitled")
                            completed = task.get("completed", False)
                            status = "✓" if completed else "○"
                            priority = task.get("priority", "medium")
                            category = task.get("category", "")

                            task_str = f"{i}. {status} {title}"
                            if priority:
                                task_str += f" [Priority: {priority}]"
                            if category:
                                task_str += f" [Category: {category}]"

                            task_list.append(task_str)

                        formatted_results.append(
                            f"✓ {tool_name}: Found {count} tasks:\n" + "\n".join(task_list)
                        )

                elif tool_name == "add_task":
                    # Format task creation result
                    task = result.get("task", {})
                    title = task.get("title", "Untitled")
                    formatted_results.append(f"✓ {tool_name}: Successfully created task '{title}'")

                elif tool_name == "complete_task":
                    # Format task completion result
                    task = result.get("task", {})
                    title = task.get("title", "Untitled")
                    formatted_results.append(f"✓ {tool_name}: Successfully completed task '{title}'")

                else:
                    # Generic success message
                    formatted_results.append(f"✓ {tool_name}: Success")
            else:
                # Tool failed
                error = call.get("error", "Unknown error")
                formatted_results.append(f"✗ {tool_name}: Failed - {error}")

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
                result = await call_tool(
                    name="list_tasks",
                    arguments={
                        "user_id": user_id,
                        "status": "all",
                        "limit": 100
                    }
                )

                tool_calls.append({
                    "tool": "list_tasks",
                    "success": result.get("success", False),
                    "result": result
                })

            except Exception as e:
                tool_calls.append({
                    "tool": "list_tasks",
                    "success": False,
                    "error": str(e)
                })

        # Step 5: Handle completing_task intent
        elif intent == "completing_task":
            # Extract task ID from message
            task_id_match = re.search(r'\b(?:task|id)\s*#?(\d+)\b', user_message, re.IGNORECASE)
            if task_id_match:
                task_id = task_id_match.group(1)
                try:
                    result = await call_tool(
                        name="complete_task",
                        arguments={
                            "user_id": user_id,
                            "task_id": task_id
                        }
                    )

                    tool_calls.append({
                        "tool": "complete_task",
                        "success": result.get("success", False),
                        "result": result
                    })

                except Exception as e:
                    tool_calls.append({
                        "tool": "complete_task",
                        "success": False,
                        "error": str(e)
                    })

        return tool_calls, conversation_state

    def _detect_intent(self, message: str) -> Optional[str]:
        """Detect user intent from message.

        Args:
            message: User message text

        Returns:
            Intent string or None (adding_task, listing_tasks, completing_task, etc.)
        """
        message_lower = message.lower()

        # Add task patterns (English and Urdu)
        add_patterns = [
            r'\badd\b.*\btask\b',
            r'\bcreate\b.*\btask\b',
            r'\bnew\b.*\btask\b',
            r'\btask\b.*\badd\b',
            r'\bkaam\b.*\badd\b',
            r'\btask\b.*\bbanao\b',
            r'\bnayi\b.*\btask\b',
        ]

        for pattern in add_patterns:
            if re.search(pattern, message_lower):
                return "adding_task"

        # List tasks patterns (English and Urdu/Mixed)
        list_patterns = [
            # English patterns
            r'\blist\b.*\btask',
            r'\bshow\b.*\btask',
            r'\bmy\b.*\btask',
            r'\bview\b.*\btask',
            r'\bsee\b.*\btask',
            r'\bhow\s+many\b.*\btask',
            r'\btask.*\blist',

            # Urdu/Mixed patterns
            r'\btask\b.*\bdikhao\b',
            r'\bmeray\b.*\bkaam\b',
            r'\bmere\b.*\btask',  # "mere task"
            r'\bkitne\b.*\btask',  # "kitne task"
            r'\bkitnay\b.*\btask',  # "kitnay task"
            r'\btask\b.*\bhein',  # "task hein"
            r'\btask\b.*\bhai',  # "task hai"
            r'\btask\b.*\blisted',  # "task listed"
            r'\bkaam\b.*\bdikhao',  # "kaam dikhao"
            r'\bkaam\b.*\bhein',  # "kaam hein"
        ]

        for pattern in list_patterns:
            if re.search(pattern, message_lower):
                return "listing_tasks"

        # Complete task patterns
        complete_patterns = [
            r'\bcomplete\b.*\btask\b',
            r'\bmark\b.*\bdone\b',
            r'\bfinish\b.*\btask\b',
            r'\btask\b.*\bcomplete\b',
            r'\bkaam\b.*\bho\s*gaya\b',
        ]

        for pattern in complete_patterns:
            if re.search(pattern, message_lower):
                return "completing_task"

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
                # Try to extract title from "add task to..." or "create task..."
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
                    cleaned = cleaned.strip()
                    if cleaned:
                        info["title"] = cleaned

        # Extract priority - check structured format first
        priority_structured = re.search(r'priority\s*[:\-]\s*(high|medium|low)', message, re.IGNORECASE)
        if priority_structured:
            info["priority"] = priority_structured.group(1).lower()
        else:
            priority_match = re.search(r'\b(high|medium|low)\b', message, re.IGNORECASE)
            if priority_match:
                info["priority"] = priority_match.group(1).lower()

        # Extract category - check structured format first
        category_structured = re.search(r'category\s*[:\-]\s*(\w+)', message, re.IGNORECASE)
        if category_structured:
            info["category"] = category_structured.group(1).lower()
        else:
            category_patterns = [
                r'\b(personal|work|shopping)\b',
            ]
            for pattern in category_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    info["category"] = match.group(1).lower()
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
        """Parse natural language date expressions.

        Args:
            text: Text containing date expression

        Returns:
            ISO 8601 date string or None
        """
        text_lower = text.lower()
        today = datetime.now()

        # Tomorrow
        if re.search(r'\btomorrow\b|\bkal\b', text_lower):
            date = today + timedelta(days=1)
            return date.isoformat()

        # Next week
        if re.search(r'\bnext\s+week\b|\bagle\s+hafte\b', text_lower):
            date = today + timedelta(days=7)
            return date.isoformat()

        # Today
        if re.search(r'\btoday\b|\baaj\b', text_lower):
            return today.isoformat()

        # Specific weekdays (next occurrence)
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
