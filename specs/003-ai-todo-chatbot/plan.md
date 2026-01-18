# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `003-ai-todo-chatbot` | **Date**: 2026-01-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-todo-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add conversational AI chatbot functionality to the existing Phase-II todo application, enabling users to manage tasks through natural language conversations in English and Urdu. The implementation uses OpenRouter API (xiaomi/mimo-v2-flash:free model) with MCP tools for task operations, OpenAI ChatKit for the frontend interface, and Web Speech API for voice input. Architecture maintains backward compatibility with Phase-II while adding Conversation and Message models to the database.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.0+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI SDK (OpenRouter compatible), MCP SDK, Pydantic
- Frontend: Next.js 16+, React 18+, OpenAI ChatKit, Web Speech API, Tailwind CSS
**Storage**: Neon PostgreSQL (existing Phase-II database, add Conversation and Message tables)
**Testing**: pytest + pytest-asyncio (backend), Jest + React Testing Library (frontend)
**Target Platform**: Web application (modern browsers with Web Speech API support)
**Project Type**: Web (monorepo with frontend/ and backend/ directories)
**Performance Goals**:
- Chat response time: <2 seconds (p95)
- Voice transcription: <1 second
- Concurrent users: 100+
- API throughput: 50 requests/second
**Constraints**:
- Stateless architecture (conversation state in database only)
- Backward compatible with Phase-II (no breaking changes to existing Task API)
- OpenRouter API rate limits (free tier: xiaomi/mimo-v2-flash:free)
- Browser Web Speech API availability (graceful degradation to text-only)
**Scale/Scope**:
- Multi-user SaaS with user isolation
- Conversation history storage (unlimited messages per user)
- Support 2 languages (English, Urdu)
- 5 MCP tools for task operations
- 1 new chat endpoint + 2 new database models

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Spec-Driven Development
**Status**: ✅ PASS
**Verification**: Feature specification exists at `/specs/003-ai-todo-chatbot/spec.md` with complete requirements, acceptance criteria, and technical approach. No code will be written before completing this plan and generating tasks.

### Gate 2: Agent Collaboration
**Status**: ✅ PASS
**Verification**:
- `todo-chat-agent`: Handles conversational AI logic and MCP tool orchestration
- `voice-input-agent`: Manages speech-to-text functionality
- `backend-api-developer`: Creates chat endpoint with JWT verification
- `database-orm-specialist`: Designs Conversation and Message models
- `frontend-dev-specialist`: Integrates ChatKit UI and voice input
Each agent operates within its domain and uses /sp.* skills for cross-cutting concerns.

### Gate 3: User Isolation
**Status**: ✅ PASS
**Verification**:
- All MCP tools require `user_id` parameter and validate ownership
- Chat endpoint filters conversations by authenticated user's JWT token
- Database queries include `WHERE user_id = {authenticated_user_id}`
- No cross-user data access possible
- Conversation and Message models include user_id foreign key

### Gate 4: Security First
**Status**: ✅ PASS
**Verification**:
- POST /api/{user_id}/chat requires JWT token verification via `Depends(verify_token)`
- User ID in URL must match JWT token user ID (403 if mismatch)
- OpenRouter API key stored in environment variable (OPENROUTER_API_KEY)
- No secrets in code or conversation logs
- Input validation via Pydantic models

### Gate 5: Type Safety
**Status**: ✅ PASS
**Verification**:
- Backend: Pydantic models for ChatRequest/ChatResponse
- Backend: SQLModel for Conversation and Message with type annotations
- Frontend: TypeScript strict mode for all components
- Frontend: Typed props for ChatKit components
- MCP tool schemas define input/output types
- No `any` types without justification

### Gate 6: Clean Architecture
**Status**: ✅ PASS
**Verification**:
- Presentation Layer: ChatKit UI components (frontend/components/chat/)
- API Layer: FastAPI chat endpoint (backend/app/api/chat.py)
- Service Layer: ChatService with OpenRouter integration (backend/app/services/chat_service.py)
- Data Layer: SQLModel Conversation/Message models (backend/app/models/)
- MCP Layer: Task management tools (backend/mcp_server/task_tools.py)
- Dependency direction: UI → API → Services → Models
- No business logic in UI components

### Gate 7: Test-Driven Development
**Status**: ✅ PASS (with implementation requirement)
**Verification**:
- Unit tests required for ChatService (mock OpenRouter API)
- Integration tests required for /api/{user_id}/chat endpoint
- Contract tests required for MCP tools
- Frontend tests required for ChatKit integration
- Voice input tests required for Web Speech API
- Target: 80%+ coverage across all modules
- Tests must pass before merge

### Gate 8: Backward Compatibility
**Status**: ✅ PASS
**Verification**:
- No changes to existing Task model or API endpoints
- New Conversation/Message models are additive only
- Existing Phase-II functionality unaffected
- Database migration adds tables without modifying existing schema
- Frontend chat feature is opt-in (separate route)

### Gate 9: Technology Stack Compliance
**Status**: ✅ PASS
**Verification**:
- Frontend: Next.js 16+ with App Router ✓
- Backend: FastAPI with SQLModel ✓
- Database: Neon PostgreSQL ✓
- Styling: Tailwind CSS (no inline styles) ✓
- Auth: Better Auth JWT tokens ✓
- Async patterns for all I/O operations ✓

### Pre-Phase 0 Gate Summary
**Overall Status**: ✅ ALL GATES PASS - Proceed to Phase 0 Research

No constitution violations detected. Feature aligns with all core principles. No complexity justification required.

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-todo-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.json   # MCP tool schemas
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── conversation.py      # NEW: Conversation SQLModel
│   │   ├── message.py           # NEW: Message SQLModel
│   │   └── task.py              # EXISTING: No changes
│   ├── services/
│   │   ├── chat_service.py      # NEW: OpenRouter integration
│   │   └── task_service.py      # EXISTING: No changes
│   ├── api/
│   │   ├── chat.py              # NEW: POST /api/{user_id}/chat
│   │   └── tasks.py             # EXISTING: No changes
│   ├── dependencies.py          # EXISTING: get_session, verify_token
│   └── main.py                  # EXISTING: Add chat router
├── mcp_server/
│   └── task_tools.py            # NEW: MCP tools implementation
├── tests/
│   ├── unit/
│   │   ├── test_chat_service.py # NEW: ChatService tests
│   │   └── test_mcp_tools.py    # NEW: MCP tool tests
│   ├── integration/
│   │   └── test_chat_api.py     # NEW: Chat endpoint tests
│   └── contract/
│       └── test_mcp_contract.py # NEW: MCP contract tests
└── requirements.txt             # ADD: openai, mcp

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx             # NEW: Chat page with ChatKit
│   └── (existing routes)        # EXISTING: No changes
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx    # NEW: ChatKit wrapper
│   │   ├── VoiceInput.tsx       # NEW: Microphone button + Web Speech API
│   │   └── MessageBubble.tsx    # NEW: Custom message styling
│   └── (existing components)    # EXISTING: No changes
├── lib/
│   ├── chat-api.ts              # NEW: Chat API client
│   └── speech-recognition.ts    # NEW: Web Speech API wrapper
├── tests/
│   ├── components/
│   │   ├── ChatInterface.test.tsx   # NEW
│   │   └── VoiceInput.test.tsx      # NEW
│   └── lib/
│       └── speech-recognition.test.ts # NEW
└── package.json                 # ADD: @openai/chatkit

.claude/
├── agents/
│   ├── todo-chat-agent.md       # EXISTING: Updated with MCP tools
│   └── voice-input-agent.md     # EXISTING: Updated with Web Speech API
└── skills/
    └── mcp-task-tools.md        # EXISTING: Reference for implementation

.env
# ADD: OPENROUTER_API_KEY=sk-or-...
```

**Structure Decision**: Web application (Option 2) selected. This is a monorepo with separate `backend/` and `frontend/` directories, consistent with Phase-II architecture. New files are additive only - no modifications to existing Task model or API endpoints. MCP server is a new subdirectory under `backend/`. Chat feature is isolated in its own route and components, ensuring backward compatibility.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations - this section is empty.

All constitution gates passed. No complexity justification required.

---

## Implementation Phases

### Phase 0: Research ✅ COMPLETED
**Artifacts**: `research.md`
**Duration**: Completed
**Status**: All technology decisions documented with rationale

**Deliverables**:
- ✅ OpenRouter API vs alternatives evaluated
- ✅ ChatKit vs custom UI evaluated
- ✅ Web Speech API vs third-party evaluated
- ✅ MCP architecture designed
- ✅ Database schema approach decided
- ✅ Multi-language strategy defined
- ✅ Error handling strategy defined
- ✅ Performance optimization approach defined
- ✅ Testing strategy defined
- ✅ Security layers defined

---

### Phase 1: Design ✅ COMPLETED
**Artifacts**: `data-model.md`, `contracts/`, `quickstart.md`
**Duration**: Completed
**Status**: All design artifacts created

**Deliverables**:
- ✅ Conversation and Message SQLModel schemas defined
- ✅ Database migration script created
- ✅ OpenAPI spec for chat endpoint (chat-api.yaml)
- ✅ MCP tool schemas documented (mcp-tools.json)
- ✅ Quickstart guide with setup instructions
- ✅ Agent context files updated

---

### Phase 2: Task Generation (Next Step)
**Command**: `/sp.tasks`
**Artifacts**: `tasks.md`
**Estimated Tasks**: 25-30 tasks
**Status**: Ready to execute

**Expected Task Breakdown**:

**Backend Tasks (15-18 tasks)**:
1. Database models (Conversation, Message)
2. Database migration
3. MCP server implementation (5 tools)
4. Chat service (OpenRouter integration)
5. Chat API endpoint
6. JWT verification
7. User isolation enforcement
8. Error handling
9. Unit tests (ChatService, MCP tools)
10. Integration tests (chat endpoint)
11. Contract tests (MCP tools)

**Frontend Tasks (8-10 tasks)**:
1. Chat page component
2. ChatInterface component (ChatKit wrapper)
3. VoiceInput component
4. MessageBubble component
5. Chat API client
6. Speech recognition wrapper
7. Language detection
8. Component tests
9. Integration with existing auth

**Infrastructure Tasks (2-3 tasks)**:
1. Environment variable configuration
2. MCP server registration
3. Dependencies installation

---

### Phase 3: Implementation
**Command**: `/sp.implement`
**Duration**: Estimated 2-3 days (with agents)
**Status**: Pending Phase 2 completion

**Agent Assignment**:
- **database-orm-specialist**: Conversation/Message models, migration
- **backend-api-developer**: Chat endpoint, ChatService, JWT verification
- **todo-chat-agent**: MCP tools implementation, OpenRouter integration
- **frontend-dev-specialist**: ChatKit integration, chat page, components
- **voice-input-agent**: VoiceInput component, Web Speech API wrapper

**Execution Strategy**:
1. Database layer first (models + migration)
2. MCP tools second (enables testing)
3. Backend service + API third (depends on MCP tools)
4. Frontend components fourth (depends on backend API)
5. Tests throughout (TDD approach)

---

### Phase 4: Testing & Validation
**Duration**: Continuous during implementation
**Coverage Target**: 80%+

**Test Execution**:
1. Unit tests run after each component
2. Integration tests after API completion
3. Contract tests after MCP tools completion
4. Frontend tests after component completion
5. End-to-end tests after full integration

**Validation Checklist**:
- [ ] All unit tests pass (80%+ coverage)
- [ ] All integration tests pass
- [ ] All contract tests pass
- [ ] Manual testing: task creation via chat
- [ ] Manual testing: task listing via chat
- [ ] Manual testing: voice input
- [ ] Manual testing: Urdu language
- [ ] Manual testing: conversation history
- [ ] Security audit: JWT verification
- [ ] Security audit: user isolation
- [ ] Performance testing: <2s response time

---

### Phase 5: Deployment
**Command**: `/sp.git.commit_pr`
**Duration**: 1-2 hours
**Status**: After Phase 4 validation

**Deployment Steps**:
1. Commit all changes with descriptive messages
2. Create pull request with summary
3. Run CI/CD pipeline (tests, linting, type checking)
4. Deploy to staging environment
5. Run smoke tests in staging
6. Deploy to production (Vercel)
7. Run smoke tests in production
8. Monitor for errors

**Environment Configuration**:
- Set `OPENROUTER_API_KEY` in Vercel environment variables
- Verify `DATABASE_URL` points to production Neon database
- Ensure `JWT_SECRET` matches Better Auth configuration
- Enable HTTPS (required for Web Speech API)

---

## Component Dependencies

### Dependency Graph

```
Constitution ✅
    ↓
Specification ✅
    ↓
Research ✅
    ↓
Design (Data Model + Contracts) ✅
    ↓
Tasks (to be generated)
    ↓
Implementation (parallel tracks):

Track 1: Database
  └─ Conversation Model
  └─ Message Model
  └─ Migration Script
      ↓
Track 2: MCP Tools (depends on Track 1)
  └─ add_task
  └─ list_tasks
  └─ complete_task
  └─ delete_task
  └─ update_task
      ↓
Track 3: Backend Service (depends on Track 2)
  └─ ChatService (OpenRouter integration)
  └─ Language detection
  └─ Error handling
      ↓
Track 4: Backend API (depends on Track 3)
  └─ POST /api/{user_id}/chat
  └─ JWT verification
  └─ User isolation
      ↓
Track 5: Frontend (depends on Track 4)
  └─ Chat page
  └─ ChatInterface component
  └─ VoiceInput component
  └─ Chat API client
      ↓
Track 6: Testing (parallel with all tracks)
  └─ Unit tests
  └─ Integration tests
  └─ Contract tests
  └─ Frontend tests
```

### Critical Path
1. Database models → MCP tools → Backend service → Backend API → Frontend
2. Estimated critical path duration: 2-3 days with agent automation

### Parallel Work Opportunities
- Frontend components can be developed with mock API
- Tests can be written alongside implementation (TDD)
- Documentation can be updated continuously

---

## Testing Strategy

### Test Pyramid

```
        /\
       /E2E\         (5% - End-to-end tests)
      /------\
     /Integration\   (25% - Integration tests)
    /------------\
   /    Unit      \  (70% - Unit tests)
  /----------------\
```

### Unit Tests (70% of tests)

**Backend Unit Tests**:
- `test_chat_service.py`: Mock OpenRouter API, test conversation logic
- `test_mcp_tools.py`: Mock database, test each tool independently
- `test_language_detection.py`: Test English/Urdu detection
- `test_error_handling.py`: Test all error scenarios

**Frontend Unit Tests**:
- `ChatInterface.test.tsx`: Test component rendering, user interactions
- `VoiceInput.test.tsx`: Test microphone button, speech recognition (mocked)
- `speech-recognition.test.ts`: Test Web Speech API wrapper
- `chat-api.test.ts`: Test API client (mocked fetch)

**Coverage Target**: 90%+ for unit tests

### Integration Tests (25% of tests)

**Backend Integration Tests**:
- `test_chat_api.py`: Test full chat endpoint with real database (test DB)
  - Test JWT authentication
  - Test user isolation
  - Test conversation creation
  - Test message persistence
  - Test error responses

**Frontend Integration Tests**:
- Test chat flow: send message → receive response → display in UI
- Test voice input flow: speak → transcribe → send → receive
- Test conversation history: reload page → messages persist

**Coverage Target**: 80%+ for integration tests

### Contract Tests (5% of tests)

**MCP Contract Tests**:
- `test_mcp_contract.py`: Verify tool schemas match implementation
  - Test input validation
  - Test output format
  - Test error codes
  - Test all 5 tools

**Coverage Target**: 100% for contract tests (all tools)

### End-to-End Tests (Manual)

**Critical User Flows**:
1. Login → Navigate to chat → Send message → Verify task created
2. Login → Navigate to chat → Ask for task list → Verify tasks displayed
3. Login → Navigate to chat → Use voice input → Verify transcription → Send
4. Login → Navigate to chat → Send Urdu message → Verify Urdu response
5. Login → Navigate to chat → Reload page → Verify conversation persists

### Test Execution Strategy

**During Development**:
- Run unit tests after each component: `pytest backend/tests/unit/`
- Run integration tests after API completion: `pytest backend/tests/integration/`
- Run frontend tests continuously: `npm test -- --watch`

**Before Commit**:
- Run all tests: `pytest backend/tests/ && npm test`
- Check coverage: `pytest --cov=app --cov-report=term-missing`
- Verify 80%+ coverage threshold

**In CI/CD Pipeline**:
- Run all tests on every PR
- Block merge if tests fail
- Block merge if coverage drops below 80%

---

## Deployment Sequence

### Pre-Deployment Checklist

- [ ] All tests passing (unit, integration, contract)
- [ ] Code coverage ≥ 80%
- [ ] No TypeScript errors (`npm run type-check`)
- [ ] No linting errors (`npm run lint`, `flake8`)
- [ ] Environment variables documented in `.env.example`
- [ ] Database migration tested on staging
- [ ] OpenRouter API key obtained
- [ ] Security audit completed

### Deployment Steps

**Step 1: Database Migration (5 minutes)**
```bash
# Connect to production database
export DATABASE_URL=<production-neon-url>

# Backup database (Neon automatic backups enabled)
# Run migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

**Step 2: Backend Deployment (10 minutes)**
```bash
# Push to main branch (triggers Vercel deployment)
git push origin 003-ai-todo-chatbot

# Vercel automatically:
# - Installs dependencies
# - Runs build
# - Deploys to production
# - Runs health checks

# Set environment variables in Vercel dashboard:
# - OPENROUTER_API_KEY
# - DATABASE_URL (already set)
# - JWT_SECRET (already set)
```

**Step 3: Frontend Deployment (10 minutes)**
```bash
# Vercel automatically deploys frontend with backend
# No separate step needed (monorepo deployment)

# Verify deployment:
# - Check Vercel dashboard for deployment status
# - Visit production URL
# - Check browser console for errors
```

**Step 4: Smoke Tests (15 minutes)**
```bash
# Test 1: Login
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Test 2: Send chat message
curl -X POST https://api.example.com/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add test task"}'

# Test 3: Verify task created
curl -X GET https://api.example.com/api/{user_id}/tasks \
  -H "Authorization: Bearer {jwt_token}"
```

**Step 5: Monitoring (Continuous)**
- Monitor Vercel logs for errors
- Monitor OpenRouter API usage
- Monitor database performance (Neon dashboard)
- Set up alerts for error rate > 5%

### Rollback Plan

**If deployment fails or critical bugs found**:

**Option 1: Rollback Database Migration**
```bash
# Rollback one migration
alembic downgrade -1

# Verify rollback
psql $DATABASE_URL -c "\dt"
```

**Option 2: Rollback Code Deployment**
```bash
# Revert to previous commit
git revert HEAD

# Push to trigger redeployment
git push origin main

# Or use Vercel dashboard to rollback to previous deployment
```

**Option 3: Feature Flag (Recommended)**
```bash
# Add feature flag in backend/.env
ENABLE_CHAT_FEATURE=false

# Frontend checks flag before showing chat route
# Backend checks flag before processing chat requests
```

### Post-Deployment Validation

**Within 1 hour**:
- [ ] Chat endpoint responding (200 OK)
- [ ] Tasks being created via chat
- [ ] Conversation history persisting
- [ ] No 500 errors in logs
- [ ] OpenRouter API calls succeeding
- [ ] Database queries performing well (<100ms)

**Within 24 hours**:
- [ ] No user-reported issues
- [ ] Error rate < 1%
- [ ] Response time < 2 seconds (p95)
- [ ] OpenRouter API usage within limits

**Within 1 week**:
- [ ] User adoption metrics tracked
- [ ] Performance metrics stable
- [ ] No security incidents
- [ ] Cost within budget

---

## Risk Mitigation

### Risk 1: OpenRouter API Rate Limits
**Impact**: High (chat feature unusable)
**Probability**: Medium (free tier has limits)

**Mitigation**:
- Implement request queuing
- Show user-friendly error message
- Upgrade to paid tier if needed
- Cache common responses (optional)

**Rollback**: Disable chat feature via feature flag

### Risk 2: Web Speech API Browser Compatibility
**Impact**: Medium (voice input unavailable)
**Probability**: Low (most browsers support it)

**Mitigation**:
- Feature detection on page load
- Hide microphone button if unsupported
- Graceful fallback to text input
- Display browser compatibility message

**Rollback**: No rollback needed (graceful degradation)

### Risk 3: Database Migration Failure
**Impact**: High (feature unusable)
**Probability**: Low (migration is additive only)

**Mitigation**:
- Test migration on staging first
- Backup database before migration
- Use Alembic rollback if needed
- No changes to existing tables (low risk)

**Rollback**: `alembic downgrade -1`

### Risk 4: JWT Token Verification Issues
**Impact**: High (security vulnerability)
**Probability**: Low (existing auth working)

**Mitigation**:
- Reuse existing verify_token dependency
- Test with existing JWT tokens
- No changes to auth logic
- Security audit before deployment

**Rollback**: Disable chat endpoint

### Risk 5: Cross-User Data Leakage
**Impact**: Critical (security breach)
**Probability**: Very Low (multiple layers of protection)

**Mitigation**:
- User isolation at all layers (MCP tools, API, database)
- Integration tests verify isolation
- Security audit before deployment
- Code review focuses on user_id filtering

**Rollback**: Immediate shutdown of chat feature

### Risk 6: Urdu Language Accuracy
**Impact**: Medium (poor UX for Urdu users)
**Probability**: Medium (model may not be optimized for Urdu)

**Mitigation**:
- Test with native Urdu speakers
- Iterate on system prompts
- Consider switching to better Urdu model if needed
- Collect user feedback

**Rollback**: No rollback needed (English still works)

---

## Success Metrics

### Technical Metrics
- **Response Time**: <2 seconds (p95) ✅ Target
- **Error Rate**: <1% ✅ Target
- **Test Coverage**: ≥80% ✅ Target
- **Uptime**: 99.9% ✅ Target

### User Metrics
- **Chat Adoption**: 30% of users try chat in first week
- **Task Creation via Chat**: 20% of tasks created via chat
- **Voice Input Usage**: 10% of chat messages via voice
- **Urdu Usage**: 5% of messages in Urdu

### Business Metrics
- **User Satisfaction**: >4.0/5.0 rating for chat feature
- **Support Tickets**: <5% increase (chat should reduce support load)
- **API Costs**: <$50/month (OpenRouter free tier)

---

## Next Steps

### Immediate (Now)
1. ✅ Complete plan.md (this document)
2. ✅ Create PHR for planning session
3. ⏭️ Run `/sp.tasks` to generate tasks.md
4. ⏭️ Review tasks.md for completeness

### Short-term (Next 2-3 days)
1. Run `/sp.implement` to execute all tasks
2. Monitor agent progress
3. Review generated code
4. Run tests continuously
5. Fix any issues

### Medium-term (Next week)
1. Complete implementation
2. Run full test suite
3. Security audit
4. Deploy to staging
5. User acceptance testing
6. Deploy to production

### Long-term (Next month)
1. Monitor production metrics
2. Collect user feedback
3. Iterate on prompts for better accuracy
4. Consider additional features (conversation search, task priority, more languages)

---

## Conclusion

This implementation plan provides a comprehensive roadmap for adding AI-powered chatbot functionality to the Phase-II todo application. All constitution gates passed, technology decisions documented, design artifacts created, and implementation strategy defined.

**Key Highlights**:
- ✅ Backward compatible with Phase-II
- ✅ Multi-layer security (JWT, user isolation, input validation)
- ✅ Stateless architecture (conversation state in database)
- ✅ Multi-language support (English, Urdu)
- ✅ Voice input capability (Web Speech API)
- ✅ Comprehensive testing strategy (80%+ coverage)
- ✅ Clear deployment and rollback plans

**Ready for Phase 2**: Execute `/sp.tasks` to generate implementation tasks.

---

**Plan Status**: ✅ COMPLETE
**Branch**: 003-ai-todo-chatbot
**Date**: 2026-01-17
**Next Command**: `/sp.tasks`
