# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/003-ai-todo-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Test-Driven Development requirement (80%+ coverage target)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/app/`, `frontend/components/`, `frontend/lib/`, `frontend/tests/`
- **MCP Server**: `backend/mcp_server/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install backend dependencies: openai>=1.0.0, mcp>=0.1.0 in backend/requirements.txt
- [X] T002 Install frontend dependencies: @openai/chatkit in frontend/package.json
- [X] T003 [P] Create environment variable template in backend/.env.example (OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL)
- [X] T004 [P] Create MCP server directory structure: backend/mcp_server/__init__.py
- [X] T005 [P] Configure MCP server registration in .claude/mcp.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models

- [X] T006 [P] Create Conversation SQLModel in backend/app/models/conversation.py
- [X] T007 [P] Create Message SQLModel with MessageRole enum in backend/app/models/message.py
- [X] T008 Create Alembic migration script for conversations and messages tables in backend/alembic/versions/003_add_chat_models.py

### MCP Tools Implementation

- [X] T009 [P] Implement add_task MCP tool in backend/mcp_server/task_tools.py
- [X] T010 [P] Implement list_tasks MCP tool in backend/mcp_server/task_tools.py
- [X] T011 [P] Implement complete_task MCP tool in backend/mcp_server/task_tools.py
- [X] T012 [P] Implement delete_task MCP tool in backend/mcp_server/task_tools.py
- [X] T013 [P] Implement update_task MCP tool in backend/mcp_server/task_tools.py
- [X] T014 Register all 5 MCP tools in MCP server list_tools() handler in backend/mcp_server/task_tools.py
- [X] T015 Implement MCP server call_tool() router in backend/mcp_server/task_tools.py

### Core Services

- [X] T016 Create language detection utility in backend/app/utils/language.py (detect English vs Urdu)
- [X] T017 Create error message translations in backend/app/utils/errors.py (English/Urdu)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Chat with Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can send chat messages and create tasks via natural language

**Independent Test**:
1. User logs in with JWT token
2. User sends message "Add buy milk to my tasks"
3. Task "buy milk" is created in database
4. Chatbot responds "Task created: buy milk"

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T018 [P] [US1] Unit test for ChatService.send_message() in backend/tests/unit/test_chat_service.py (mock OpenRouter API)
- [X] T019 [P] [US1] Unit test for MCP add_task tool in backend/tests/unit/test_mcp_tools.py
- [X] T020 [P] [US1] Contract test for POST /api/{user_id}/chat endpoint in backend/tests/contract/test_chat_api.py
- [X] T021 [P] [US1] Integration test for chat → task creation flow in backend/tests/integration/test_chat_flow.py

### Implementation for User Story 1

- [X] T022 [P] [US1] Create ChatRequest Pydantic model in backend/app/models/requests.py
- [X] T023 [P] [US1] Create ChatResponse Pydantic model in backend/app/models/responses.py
- [X] T024 [US1] Implement ChatService with OpenRouter client in backend/app/services/chat_service.py (depends on T022, T023)
- [X] T025 [US1] Implement conversation creation logic in ChatService in backend/app/services/chat_service.py
- [X] T026 [US1] Implement message persistence logic in ChatService in backend/app/services/chat_service.py
- [X] T027 [US1] Implement MCP tool calling logic in ChatService in backend/app/services/chat_service.py
- [X] T028 [US1] Create POST /api/{user_id}/chat endpoint in backend/routes/chat.py with JWT verification
- [X] T029 [US1] Add user ID validation (JWT user_id must match URL user_id) in backend/routes/chat.py
- [X] T030 [US1] Add error handling for OpenRouter API failures in backend/routes/chat.py
- [X] T031 [US1] Register chat router in backend/main.py
- [X] T032 [P] [US1] Create chat API client in frontend/lib/chat-api.ts
- [X] T033 [P] [US1] Create ChatInterface component with ChatKit in frontend/components/chat/ChatInterface.tsx
- [X] T034 [P] [US1] Create MessageBubble component in frontend/components/chat/MessageBubble.tsx
- [X] T035 [US1] Create chat page at frontend/app/chat/page.tsx
- [X] T036 [US1] Add chat link to navigation in frontend/components/Navigation.tsx
- [X] T037 [P] [US1] Frontend test for ChatInterface component in frontend/tests/components/ChatInterface.test.tsx
- [X] T038 [P] [US1] Frontend test for chat API client in frontend/tests/lib/chat-api.test.ts

**Checkpoint**: At this point, User Story 1 should be fully functional - users can chat and create tasks

---

## Phase 4: User Story 2 - Full Task Management via Chat (Priority: P1)

**Goal**: Users can list, complete, update, and delete tasks via natural language

**Independent Test**:
1. User has 3 tasks in database
2. User sends "Show me my tasks" → sees all 3 tasks
3. User sends "Mark task 1 as done" → task marked complete
4. User sends "Delete task 2" → task removed
5. User sends "Change task 3 deadline to tomorrow" → task updated

### Tests for User Story 2

- [ ] T039 [P] [US2] Unit test for list_tasks MCP tool in backend/tests/unit/test_mcp_tools.py
- [ ] T040 [P] [US2] Unit test for complete_task MCP tool in backend/tests/unit/test_mcp_tools.py
- [ ] T041 [P] [US2] Unit test for delete_task MCP tool in backend/tests/unit/test_mcp_tools.py
- [ ] T042 [P] [US2] Unit test for update_task MCP tool in backend/tests/unit/test_mcp_tools.py
- [ ] T043 [P] [US2] Integration test for task listing via chat in backend/tests/integration/test_chat_flow.py
- [ ] T044 [P] [US2] Integration test for task completion via chat in backend/tests/integration/test_chat_flow.py

### Implementation for User Story 2

- [X] T045 [US2] Enhance ChatService to handle list_tasks intent in backend/app/services/chat_service.py
- [X] T046 [US2] Enhance ChatService to handle complete_task intent in backend/app/services/chat_service.py
- [X] T047 [US2] Enhance ChatService to handle delete_task intent in backend/app/services/chat_service.py
- [ ] T048 [US2] Enhance ChatService to handle update_task intent in backend/app/services/chat_service.py
- [X] T049 [US2] Add task formatting for chat responses in backend/app/utils/formatters.py
- [X] T050 [US2] Update ChatInterface to display task lists in frontend/components/chat/ChatInterface.tsx
- [ ] T051 [P] [US2] Frontend test for task list display in frontend/tests/components/ChatInterface.test.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - full task CRUD via chat

---

## Phase 5: User Story 3 - Multi-Language Support (Priority: P2)

**Goal**: Users can interact in English or Urdu, with automatic language detection

**Independent Test**:
1. User sends message in Urdu: "میرے کام دکھاؤ"
2. System detects Urdu language
3. Chatbot responds in Urdu with task list
4. User switches to English: "Add new task"
5. System detects English and responds in English

### Tests for User Story 3

- [ ] T052 [P] [US3] Unit test for language detection in backend/tests/unit/test_language.py
- [ ] T053 [P] [US3] Unit test for Urdu error messages in backend/tests/unit/test_errors.py
- [ ] T054 [P] [US3] Integration test for Urdu conversation flow in backend/tests/integration/test_chat_flow.py

### Implementation for User Story 3

- [X] T055 [US3] Enhance language detection to support Urdu Unicode range in backend/app/utils/language.py
- [X] T056 [US3] Add Urdu system prompts to ChatService in backend/app/services/chat_service.py
- [X] T057 [US3] Implement language-aware response formatting in backend/app/services/chat_service.py
- [X] T058 [US3] Add language metadata to Message model in backend/app/models/message.py
- [X] T059 [P] [US3] Add Urdu font support to Tailwind config in frontend/tailwind.config.js
- [X] T060 [P] [US3] Update MessageBubble to handle RTL text in frontend/components/chat/MessageBubble.tsx
- [ ] T061 [P] [US3] Frontend test for Urdu text display in frontend/tests/components/MessageBubble.test.tsx

**Checkpoint**: All user stories 1, 2, and 3 should work - full multilingual chat

---

## Phase 6: User Story 4 - Voice Input (Priority: P2)

**Goal**: Users can speak their requests instead of typing

**Independent Test**:
1. User clicks microphone button
2. User speaks "Add meeting tomorrow"
3. Speech is transcribed to text
4. Text appears in input field
5. User sends message
6. Task is created

### Tests for User Story 4

- [ ] T062 [P] [US4] Unit test for speech recognition wrapper in frontend/tests/lib/speech-recognition.test.ts (mock Web Speech API)
- [ ] T063 [P] [US4] Unit test for VoiceInput component in frontend/tests/components/VoiceInput.test.tsx

### Implementation for User Story 4

- [ ] T064 [P] [US4] Create speech recognition wrapper in frontend/lib/speech-recognition.ts
- [ ] T065 [P] [US4] Add browser compatibility detection in frontend/lib/speech-recognition.ts
- [ ] T066 [P] [US4] Create VoiceInput component with microphone button in frontend/components/chat/VoiceInput.tsx
- [ ] T067 [US4] Integrate VoiceInput into ChatInterface in frontend/components/chat/ChatInterface.tsx
- [ ] T068 [US4] Add language selection for speech recognition (English/Urdu) in frontend/components/chat/VoiceInput.tsx
- [ ] T069 [US4] Add error handling for unsupported browsers in frontend/components/chat/VoiceInput.tsx

**Checkpoint**: Voice input working - users can speak or type

---

## Phase 7: User Story 5 - Conversation History (Priority: P2)

**Goal**: Users can view past conversations and conversation context is maintained

**Independent Test**:
1. User has 3 previous conversations in database
2. User opens chat page
3. Previous conversations are listed
4. User clicks on conversation
5. All messages from that conversation are displayed
6. User can continue the conversation

### Tests for User Story 5

- [ ] T070 [P] [US5] Unit test for conversation retrieval in backend/tests/unit/test_chat_service.py
- [ ] T071 [P] [US5] Integration test for conversation history in backend/tests/integration/test_chat_flow.py
- [ ] T072 [P] [US5] Frontend test for conversation list in frontend/tests/components/ConversationList.test.tsx

### Implementation for User Story 5

- [ ] T073 [US5] Implement GET /api/{user_id}/conversations endpoint in backend/app/api/chat.py
- [ ] T074 [US5] Implement GET /api/{user_id}/conversations/{conversation_id}/messages endpoint in backend/app/api/chat.py
- [ ] T075 [US5] Add conversation retrieval to ChatService in backend/app/services/chat_service.py
- [ ] T076 [P] [US5] Create ConversationList component in frontend/components/chat/ConversationList.tsx
- [ ] T077 [US5] Add conversation sidebar to chat page in frontend/app/chat/page.tsx
- [ ] T078 [US5] Implement conversation switching in ChatInterface in frontend/components/chat/ChatInterface.tsx
- [ ] T079 [US5] Add "New Conversation" button in frontend/components/chat/ConversationList.tsx

**Checkpoint**: All user stories complete - full chat functionality with history

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T080 [P] Add loading indicators during API calls in frontend/components/chat/ChatInterface.tsx
- [ ] T081 [P] Add typing indicator while AI is responding in frontend/components/chat/ChatInterface.tsx
- [ ] T082 [P] Add rate limiting (10 requests/minute per user) in backend/app/api/chat.py
- [ ] T083 [P] Add request queuing for OpenRouter API in backend/app/services/chat_service.py
- [ ] T084 [P] Add conversation context window management (limit to last 10 messages) in backend/app/services/chat_service.py
- [ ] T085 [P] Add error boundary component in frontend/components/chat/ErrorBoundary.tsx
- [ ] T086 [P] Add retry logic for transient failures in frontend/lib/chat-api.ts
- [ ] T087 [P] Add logging for all chat operations in backend/app/services/chat_service.py
- [ ] T088 [P] Add performance monitoring (response time tracking) in backend/app/api/chat.py
- [ ] T089 [P] Update quickstart.md with final setup instructions
- [ ] T090 Run database migration: alembic upgrade head
- [ ] T091 Verify all tests pass: pytest backend/tests/ && npm test
- [ ] T092 Verify 80%+ code coverage: pytest --cov=app --cov-report=term-missing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (Phase 3): Can start after Foundational - No dependencies on other stories
  - User Story 2 (Phase 4): Depends on User Story 1 (extends chat functionality)
  - User Story 3 (Phase 5): Can start after Foundational - Independent of US1/US2
  - User Story 4 (Phase 6): Can start after Foundational - Independent of other stories
  - User Story 5 (Phase 7): Depends on User Story 1 (needs basic chat working)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - MVP ready after this
- **User Story 2 (P1)**: Depends on US1 (extends task management)
- **User Story 3 (P2)**: Foundation only - Can run parallel with US1/US2
- **User Story 4 (P2)**: Foundation only - Can run parallel with other stories
- **User Story 5 (P2)**: Depends on US1 (needs basic chat)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Backend before frontend
- Core implementation before integration

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T003, T004, T005 can run in parallel

**Foundational Phase (Phase 2)**:
- T006, T007 can run in parallel (different models)
- T009-T013 can run in parallel (different MCP tools)
- T016, T017 can run in parallel (different utilities)

**User Story 1 (Phase 3)**:
- T018-T021 can run in parallel (different test files)
- T022, T023 can run in parallel (different models)
- T032, T033, T034 can run in parallel (different frontend files)
- T037, T038 can run in parallel (different test files)

**User Story 2 (Phase 4)**:
- T039-T044 can run in parallel (different test files)

**User Story 3 (Phase 5)**:
- T052-T054 can run in parallel (different test files)
- T059, T060 can run in parallel (different frontend files)

**User Story 4 (Phase 6)**:
- T062, T063 can run in parallel (different test files)
- T064, T065, T066 can run in parallel (different files)

**User Story 5 (Phase 7)**:
- T070-T072 can run in parallel (different test files)

**Polish Phase (Phase 8)**:
- T080-T089 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for ChatService.send_message() in backend/tests/unit/test_chat_service.py"
Task: "Unit test for MCP add_task tool in backend/tests/unit/test_mcp_tools.py"
Task: "Contract test for POST /api/{user_id}/chat endpoint in backend/tests/contract/test_chat_api.py"
Task: "Integration test for chat → task creation flow in backend/tests/integration/test_chat_flow.py"

# Launch all Pydantic models for User Story 1 together:
Task: "Create ChatRequest Pydantic model in backend/app/models/requests.py"
Task: "Create ChatResponse Pydantic model in backend/app/models/responses.py"

# Launch all frontend components for User Story 1 together:
Task: "Create chat API client in frontend/lib/chat-api.ts"
Task: "Create ChatInterface component with ChatKit in frontend/components/chat/ChatInterface.tsx"
Task: "Create MessageBubble component in frontend/components/chat/MessageBubble.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Basic chat + task creation)
4. Complete Phase 4: User Story 2 (Full task management)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready - this is a functional MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Basic chat MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Full task management!)
4. Add User Story 3 → Test independently → Deploy/Demo (Multi-language support!)
5. Add User Story 4 → Test independently → Deploy/Demo (Voice input!)
6. Add User Story 5 → Test independently → Deploy/Demo (Conversation history!)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 → User Story 2 (sequential, US2 depends on US1)
   - Developer B: User Story 3 (parallel, independent)
   - Developer C: User Story 4 (parallel, independent)
3. After US1 completes:
   - Developer D: User Story 5 (depends on US1)
4. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 92 tasks

**Task Count by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 12 tasks
- Phase 3 (User Story 1): 21 tasks
- Phase 4 (User Story 2): 13 tasks
- Phase 5 (User Story 3): 10 tasks
- Phase 6 (User Story 4): 6 tasks
- Phase 7 (User Story 5): 7 tasks
- Phase 8 (Polish): 13 tasks
- Phase 9 (Validation): 5 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel

**Test Coverage**: 26 test tasks (28% of total) targeting 80%+ coverage

**MVP Scope**: Phases 1-4 (51 tasks) deliver functional chat with full task management

**Complexity Estimates**:
- Simple: 35 tasks (models, utilities, tests)
- Medium: 45 tasks (services, endpoints, components)
- Complex: 12 tasks (ChatService, MCP integration, OpenRouter client)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run `alembic upgrade head` before testing backend
- Run `npm install` and `pip install -r requirements.txt` before starting
- Set OPENROUTER_API_KEY environment variable before testing chat
