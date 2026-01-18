# Research: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Phase**: 0 - Research & Technology Decisions
**Date**: 2026-01-17

## Overview

This document captures research findings, technology decisions, and architectural choices for implementing conversational AI chatbot functionality in the Phase-II todo application.

---

## Decision 1: AI Provider - OpenRouter vs OpenAI

### Decision
Use **OpenRouter API** with `xiaomi/mimo-v2-flash:free` model instead of OpenAI directly.

### Rationale
1. **Cost**: Free tier available with xiaomi/mimo-v2-flash:free model (no API costs during development/testing)
2. **Compatibility**: OpenRouter API is OpenAI-compatible, allowing use of OpenAI SDK without code changes
3. **Flexibility**: Easy to switch models later without changing integration code
4. **Rate Limits**: Sufficient for initial deployment (free tier supports moderate usage)

### Alternatives Considered
- **OpenAI GPT-3.5/4**: Higher cost, requires paid API key, better quality but overkill for task management
- **Anthropic Claude**: Excellent quality but higher cost, no free tier
- **Local LLM (Ollama)**: No API costs but requires infrastructure, deployment complexity, performance concerns

### Implementation Notes
- Use `openai` Python SDK with `base_url="https://openrouter.ai/api/v1"`
- Set `OPENROUTER_API_KEY` environment variable
- Model parameter: `xiaomi/mimo-v2-flash:free`
- Fallback strategy: If rate limited, queue requests or show user-friendly error

### References
- OpenRouter Docs: https://openrouter.ai/docs
- OpenAI SDK Compatibility: https://github.com/openai/openai-python

---

## Decision 2: Frontend Chat UI - OpenAI ChatKit vs Custom

### Decision
Use **OpenAI ChatKit** library for chat interface.

### Rationale
1. **Production-Ready**: Battle-tested UI components from OpenAI
2. **Accessibility**: Built-in ARIA labels, keyboard navigation, screen reader support
3. **Responsive**: Mobile-first design out of the box
4. **Customizable**: Tailwind CSS integration for styling
5. **Time Savings**: Avoid reinventing message bubbles, scroll behavior, input handling

### Alternatives Considered
- **Custom React Components**: Full control but significant development time, accessibility concerns
- **react-chat-widget**: Simpler but less feature-rich, limited customization
- **stream-chat-react**: Overkill (designed for real-time multi-user chat), requires Stream backend

### Implementation Notes
- Install: `npm install @openai/chatkit`
- Wrap in custom `ChatInterface.tsx` component for app-specific logic
- Use Tailwind CSS for theme customization
- Integrate with existing Better Auth session management

### References
- ChatKit GitHub: https://github.com/openai/chatkit
- ChatKit Docs: https://platform.openai.com/docs/chatkit

---

## Decision 3: Voice Input - Web Speech API vs Third-Party

### Decision
Use **Web Speech API** (browser native) for speech-to-text.

### Rationale
1. **Zero Cost**: No API fees, no external service dependencies
2. **Low Latency**: On-device processing (Chrome) or fast cloud processing (other browsers)
3. **Multi-Language**: Built-in support for English and Urdu
4. **Privacy**: No audio data sent to third-party services (in Chrome)
5. **Simple Integration**: Native browser API, no SDK required

### Alternatives Considered
- **Google Cloud Speech-to-Text**: High accuracy but costs $0.006/15 seconds, requires API key
- **AssemblyAI**: Good accuracy but paid service, adds external dependency
- **Whisper API (OpenAI)**: Excellent accuracy but costs $0.006/minute, latency concerns

### Implementation Notes
- Use `SpeechRecognition` or `webkitSpeechRecognition` API
- Language detection: Set `lang` parameter based on user preference or auto-detect
- Graceful degradation: Show text-only input if API unavailable
- Browser support: Chrome (best), Safari (good), Firefox (limited)

### Browser Compatibility Strategy
- Feature detection: Check `'SpeechRecognition' in window || 'webkitSpeechRecognition' in window`
- Fallback: Hide microphone button if unsupported, show text input only
- User feedback: Display browser compatibility message if needed

### References
- MDN Web Speech API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- Browser Support: https://caniuse.com/speech-recognition

---

## Decision 4: MCP Architecture - Tool Design Pattern

### Decision
Implement **5 stateless MCP tools** (add_task, list_tasks, complete_task, delete_task, update_task) with user_id-based isolation.

### Rationale
1. **Separation of Concerns**: AI agent logic separate from task operations
2. **Reusability**: Tools can be used by multiple agents or features
3. **Testability**: Each tool independently testable with clear contracts
4. **Security**: User isolation enforced at tool level, not agent level
5. **Stateless**: No session state in tools, all context in database

### Alternatives Considered
- **Direct Database Access from Agent**: Tight coupling, security risks, hard to test
- **REST API Calls from Agent**: Network overhead, authentication complexity
- **Single "manage_tasks" Tool**: Less granular, harder to test, unclear contracts

### Tool Design Principles
- Each tool accepts `user_id` as first parameter
- Validate user ownership before any operation
- Return standardized JSON: `{success: bool, data: any, error?: string, code?: string}`
- Handle errors gracefully with specific error codes
- No side effects beyond database operations

### Implementation Notes
- MCP server in `backend/mcp_server/task_tools.py`
- Use SQLModel for database operations
- Register in `.claude/mcp.json` configuration
- Document tool schemas in `contracts/mcp-tools.json`

### References
- MCP Specification: https://modelcontextprotocol.io/docs
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk

---

## Decision 5: Database Schema - Conversation Storage

### Decision
Add **Conversation** and **Message** models with user_id foreign keys, no changes to existing Task model.

### Rationale
1. **Backward Compatibility**: Existing Task API unchanged
2. **User Isolation**: Conversation and Message tables include user_id for filtering
3. **Conversation Context**: Store full conversation history for context window
4. **Audit Trail**: Track all user interactions for debugging and analytics
5. **Stateless Architecture**: No in-memory session state, all in database

### Schema Design

**Conversation Model**:
- `id` (UUID, primary key)
- `user_id` (String, foreign key, indexed)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Message Model**:
- `id` (UUID, primary key)
- `conversation_id` (UUID, foreign key)
- `role` (Enum: "user" | "assistant")
- `content` (Text)
- `timestamp` (DateTime)
- `metadata` (JSON, optional - for tool calls, errors, etc.)

### Alternatives Considered
- **Single Messages Table**: No conversation grouping, harder to query context
- **Embed in Task Model**: Tight coupling, violates single responsibility
- **NoSQL (MongoDB)**: Adds complexity, Neon PostgreSQL already available

### Migration Strategy
- Alembic migration to add new tables
- No data migration needed (new feature)
- Indexes on user_id and conversation_id for query performance

### References
- SQLModel Docs: https://sqlmodel.tiangolo.com/
- Alembic Migrations: https://alembic.sqlalchemy.org/

---

## Decision 6: Multi-Language Support - Language Detection

### Decision
**Auto-detect language** from user input, respond in same language.

### Rationale
1. **User Experience**: No manual language selection required
2. **Simplicity**: Single chat interface for both languages
3. **Flexibility**: Easy to add more languages later

### Implementation Strategy
- Use simple heuristic: Check for Urdu Unicode range (U+0600 to U+06FF)
- If Urdu detected, set system prompt to respond in Urdu
- If English detected (or default), respond in English
- Pass detected language to OpenRouter API in system prompt

### Language-Specific Considerations
- **English**: Standard prompts, well-supported by all models
- **Urdu**: May require prompt engineering for accuracy, test with native speakers
- **Mixed Input**: Default to English if both languages detected

### Alternatives Considered
- **Manual Language Toggle**: Extra UI complexity, user friction
- **Browser Language Detection**: May not match user's preferred input language
- **Separate Chat Interfaces**: Duplicates code, poor UX

### Implementation Notes
```python
def detect_language(text: str) -> str:
    urdu_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    return "urdu" if urdu_chars > len(text) * 0.3 else "english"
```

---

## Decision 7: Error Handling - Graceful Degradation

### Decision
Implement **multi-layer error handling** with user-friendly messages in user's language.

### Error Handling Layers

1. **MCP Tool Level**:
   - Validate inputs (Pydantic)
   - Return error codes: VALIDATION_ERROR, UNAUTHORIZED, NOT_FOUND, DATABASE_ERROR
   - No exceptions thrown, always return JSON response

2. **Chat Service Level**:
   - Catch OpenRouter API errors (rate limits, timeouts, invalid responses)
   - Retry transient failures (3 attempts with exponential backoff)
   - Fallback message if AI unavailable: "I'm having trouble right now. Please try again."

3. **API Endpoint Level**:
   - Catch all exceptions
   - Return appropriate HTTP status codes
   - Log errors for debugging
   - Never expose internal error details to user

4. **Frontend Level**:
   - Display error messages in chat interface
   - Retry button for failed requests
   - Offline detection and user feedback

### Language-Specific Error Messages
- Maintain error message translations (English/Urdu)
- Detect user's language from last message
- Return errors in appropriate language

### Implementation Notes
```python
ERROR_MESSAGES = {
    "RATE_LIMIT": {
        "en": "I'm receiving too many requests. Please try again in a moment.",
        "ur": "بہت زیادہ درخواستیں موصول ہو رہی ہیں۔ براہ کرم ایک لمحے میں دوبارہ کوشش کریں۔"
    },
    # ... more error messages
}
```

---

## Decision 8: Performance Optimization - Async Patterns

### Decision
Use **async/await** throughout the stack for all I/O operations.

### Rationale
1. **Concurrency**: Handle multiple chat requests simultaneously
2. **Responsiveness**: Non-blocking database and API calls
3. **Scalability**: Support 100+ concurrent users with single server
4. **FastAPI Native**: FastAPI designed for async operations

### Async Implementation Points
- Database queries: `session.exec()` → `await session.exec()`
- OpenRouter API calls: `openai.ChatCompletion.create()` → `await openai.ChatCompletion.acreate()`
- MCP tool calls: All tool handlers are async functions
- Frontend API calls: Use `fetch()` with async/await

### Performance Targets
- Chat response time: <2 seconds (p95)
- Database query time: <100ms (p95)
- OpenRouter API call: <1.5 seconds (p95)
- Voice transcription: <1 second

### Monitoring Strategy
- Log response times for all operations
- Track OpenRouter API latency separately
- Alert if p95 exceeds targets

---

## Decision 9: Testing Strategy - Multi-Layer Testing

### Decision
Implement **unit, integration, and contract tests** with 80%+ coverage.

### Test Layers

1. **Unit Tests** (backend/tests/unit/):
   - `test_chat_service.py`: Mock OpenRouter API, test conversation logic
   - `test_mcp_tools.py`: Test each MCP tool with mock database
   - Coverage target: 90%+

2. **Integration Tests** (backend/tests/integration/):
   - `test_chat_api.py`: Test full chat endpoint with real database (test DB)
   - Test JWT authentication, user isolation, error handling
   - Coverage target: 80%+

3. **Contract Tests** (backend/tests/contract/):
   - `test_mcp_contract.py`: Verify MCP tool schemas match implementation
   - Test input validation, output format, error codes
   - Coverage target: 100% (all tools)

4. **Frontend Tests** (frontend/tests/):
   - `ChatInterface.test.tsx`: Test component rendering, user interactions
   - `VoiceInput.test.tsx`: Test microphone button, speech recognition (mocked)
   - `speech-recognition.test.ts`: Test Web Speech API wrapper
   - Coverage target: 80%+

### Test Data Strategy
- Use pytest fixtures for database setup/teardown
- Mock OpenRouter API responses (avoid real API calls in tests)
- Mock Web Speech API in frontend tests
- Test with both English and Urdu inputs

### CI/CD Integration
- Run all tests on every PR
- Block merge if coverage drops below 80%
- Run integration tests against test database (not production)

---

## Decision 10: Security - Defense in Depth

### Decision
Implement **multi-layer security** with JWT verification, user isolation, and input validation.

### Security Layers

1. **Authentication Layer**:
   - JWT token verification on all chat endpoints
   - Token must be valid and not expired
   - User ID in URL must match JWT token user ID

2. **Authorization Layer**:
   - All MCP tools validate user_id ownership
   - Database queries filter by authenticated user's ID
   - No cross-user data access possible

3. **Input Validation Layer**:
   - Pydantic models validate all inputs
   - Sanitize user messages (prevent injection attacks)
   - Limit message length (max 2000 characters)
   - Rate limiting: 10 requests/minute per user

4. **Data Protection Layer**:
   - No sensitive data in conversation logs
   - OpenRouter API key in environment variable only
   - Database connection string in environment variable
   - No secrets in code or version control

### Threat Model
- **Cross-User Access**: Mitigated by user_id filtering at all layers
- **Prompt Injection**: Mitigated by input sanitization and system prompt design
- **API Key Exposure**: Mitigated by environment variables and .gitignore
- **Rate Limit Abuse**: Mitigated by per-user rate limiting

### Security Testing
- Test unauthorized access attempts (wrong user_id)
- Test expired/invalid JWT tokens
- Test SQL injection attempts (SQLModel prevents this)
- Test prompt injection attempts

---

## Implementation Phases

### Phase 0: Research ✅ (This Document)
- Technology decisions documented
- Architectural choices justified
- Alternatives evaluated

### Phase 1: Design (Next)
- Create data-model.md with Conversation/Message schemas
- Create contracts/chat-api.yaml with OpenAPI spec
- Create contracts/mcp-tools.json with MCP tool schemas
- Create quickstart.md with setup instructions
- Update agent context files

### Phase 2: Tasks (After Phase 1)
- Generate tasks.md with /sp.tasks command
- Break down implementation into testable tasks
- Assign tasks to appropriate agents

### Phase 3: Implementation (After Phase 2)
- Execute tasks with /sp.implement command
- Run tests continuously
- Verify 80%+ coverage

### Phase 4: Deployment (After Phase 3)
- Deploy to Vercel (frontend + backend)
- Configure environment variables
- Run smoke tests in production

---

## Open Questions

None - all technical decisions resolved during research phase.

---

## References

1. OpenRouter API: https://openrouter.ai/docs
2. OpenAI ChatKit: https://github.com/openai/chatkit
3. Web Speech API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
4. MCP Specification: https://modelcontextprotocol.io/docs
5. SQLModel: https://sqlmodel.tiangolo.com/
6. FastAPI: https://fastapi.tiangolo.com/
7. Next.js 16: https://nextjs.org/docs

---

**Research Complete**: All technology decisions documented with rationale and alternatives. Ready to proceed to Phase 1 (Design).
