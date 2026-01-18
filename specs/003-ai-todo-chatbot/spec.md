# Feature Specification: AI-Powered Todo Chatbot

**Feature ID**: 003-ai-todo-chatbot
**Status**: Draft
**Created**: 2026-01-17
**Last Updated**: 2026-01-17

## Overview

Add conversational AI chatbot functionality to the existing Phase-II todo application, enabling users to manage tasks through natural language conversations in English and Urdu.

## Business Context

Users need a more intuitive way to interact with their todo lists. Natural language conversation removes friction from task management and makes the application accessible to users who prefer voice or chat interfaces over traditional forms.

## Requirements

### Functional Requirements

#### FR1: Conversational Task Management
- Users can create tasks via natural language (e.g., "Add buy groceries to my list")
- Users can list tasks with filters (e.g., "Show me today's tasks", "What's due this week?")
- Users can complete tasks (e.g., "Mark grocery shopping as done")
- Users can update tasks (e.g., "Change the deadline to tomorrow")
- Users can delete tasks (e.g., "Remove the meeting task")

#### FR2: Multi-Language Support
- Support English and Urdu input
- Detect language automatically from user input
- Respond in the same language as the user's input

#### FR3: Voice Input
- Users can speak their requests instead of typing
- Speech-to-text conversion using Web Speech API
- Support for both English and Urdu speech recognition

#### FR4: Conversation History
- Store conversation history in database
- Users can view past conversations
- Conversation context maintained across sessions

#### FR5: Chat Interface
- Modern chat UI using OpenAI ChatKit
- Message bubbles for user and assistant
- Typing indicators during processing
- Microphone button for voice input

### Non-Functional Requirements

#### NFR1: Performance
- Chat responses within 2 seconds
- Voice transcription within 1 second
- Support 100+ concurrent users

#### NFR2: Security
- All chat endpoints require JWT authentication
- User isolation: users only see their own conversations
- No sensitive data in conversation logs

#### NFR3: Reliability
- Graceful degradation if OpenRouter API is unavailable
- Retry logic for transient failures
- Error messages in user's language

#### NFR4: Maintainability
- Stateless architecture (conversation state in database)
- MCP tools for task operations
- Backward compatible with Phase-II

## Technical Approach

### Architecture Components

1. **Database Layer**
   - Add `Conversation` model (id, user_id, created_at, updated_at)
   - Add `Message` model (id, conversation_id, role, content, timestamp)
   - Maintain existing Task model (no changes)

2. **MCP Server**
   - Implement 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
   - Tools accept user_id for security isolation
   - Return standardized JSON responses

3. **Backend API**
   - POST /api/{user_id}/chat endpoint
   - Accept: { message: string, conversation_id?: string }
   - Return: { response: string, conversation_id: string }
   - JWT verification required

4. **AI Agent Integration**
   - Use OpenRouter API (not OpenAI)
   - Model: xiaomi/mimo-v2-flash:free
   - Agent has access to MCP tools
   - Interprets natural language and calls appropriate tools

5. **Frontend**
   - Integrate OpenAI ChatKit library
   - Add chat page/component
   - Microphone button for voice input
   - Web Speech API for speech-to-text

### Technology Stack

- **Backend**: FastAPI, SQLModel, OpenAI SDK (OpenRouter compatible), MCP SDK
- **Frontend**: Next.js 16+, OpenAI ChatKit, Web Speech API
- **Database**: Neon PostgreSQL (existing)
- **AI**: OpenRouter API (xiaomi/mimo-v2-flash:free model)

### Agents

- **todo-chat-agent**: Handles conversational AI logic, interprets user intent, calls MCP tools
- **voice-input-agent**: Manages speech-to-text functionality, language detection

## Acceptance Criteria

### AC1: Task Creation via Chat
- Given a user types "Add buy milk to my tasks"
- When the message is sent
- Then a new task "buy milk" is created
- And the chatbot confirms "Task created: buy milk"

### AC2: Task Listing via Chat
- Given a user has 3 active tasks
- When the user types "Show me my tasks"
- Then the chatbot lists all 3 tasks
- And displays title and due date for each

### AC3: Voice Input
- Given a user clicks the microphone button
- When the user speaks "Add meeting tomorrow"
- Then the speech is transcribed to text
- And the task is created from the transcription

### AC4: Multi-Language Support
- Given a user types in Urdu "میرے کام دکھاؤ"
- When the message is sent
- Then the chatbot responds in Urdu
- And lists the user's tasks

### AC5: Conversation History
- Given a user has had previous conversations
- When the user opens the chat interface
- Then previous messages are displayed
- And conversation context is maintained

## Out of Scope

- Voice output (text-to-speech)
- Image/file attachments in chat
- Group conversations or task sharing
- Custom AI model training
- Languages beyond English and Urdu

## Dependencies

- Existing Phase-II infrastructure (Next.js, FastAPI, Neon PostgreSQL)
- Better Auth JWT tokens for authentication
- OpenRouter API account and API key
- Browser support for Web Speech API

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| OpenRouter API rate limits | High | Implement request queuing and user feedback |
| Web Speech API browser compatibility | Medium | Provide fallback to text input |
| Urdu language accuracy | Medium | Test with native speakers, iterate on prompts |
| Conversation context management | Medium | Limit context window, implement summarization |

## Success Metrics

- 80%+ of chat requests successfully create/modify tasks
- <2s average response time for chat messages
- 90%+ speech recognition accuracy for English
- 70%+ speech recognition accuracy for Urdu
- Zero cross-user data leakage incidents

## References

- Phase-II Todo App: /specs/001-todo-web-app/
- MCP Task Tools Skill: /.claude/skills/mcp-task-tools.md
- OpenRouter API Docs: https://openrouter.ai/docs
- OpenAI ChatKit: https://github.com/openai/chatkit
