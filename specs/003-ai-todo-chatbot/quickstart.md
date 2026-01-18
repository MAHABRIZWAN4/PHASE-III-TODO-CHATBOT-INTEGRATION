# Quickstart Guide: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Audience**: Developers setting up the chat feature
**Time to Complete**: ~30 minutes

## Overview

This guide walks you through setting up the AI-powered todo chatbot feature on top of the existing Phase-II todo application. By the end, you'll have a working chat interface where users can manage tasks through natural language conversations.

---

## Prerequisites

### Required (Must Have)
- ✅ Phase-II todo application running (Next.js frontend + FastAPI backend)
- ✅ Neon PostgreSQL database configured and accessible
- ✅ Better Auth JWT authentication working
- ✅ Node.js 18+ and Python 3.11+ installed
- ✅ Git repository cloned locally

### Optional (Recommended)
- OpenRouter API account (free tier available)
- Modern browser with Web Speech API support (Chrome recommended)

---

## Step 1: Get OpenRouter API Key

### Option A: Free Tier (Recommended for Development)

1. Visit https://openrouter.ai/
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-or-...`)

**Note**: Free tier uses `xiaomi/mimo-v2-flash:free` model with rate limits. Sufficient for development and testing.

### Option B: Skip for Now (Use Mock)

If you don't have an API key yet, you can use a mock implementation for local testing. See "Development Mode" section below.

---

## Step 2: Install Dependencies

### Backend Dependencies

```bash
cd backend

# Add new dependencies to requirements.txt
cat >> requirements.txt << EOF
openai>=1.0.0          # OpenRouter API client (OpenAI-compatible)
mcp>=0.1.0             # Model Context Protocol SDK
EOF

# Install dependencies
pip install -r requirements.txt

# Or install directly
pip install openai mcp
```

### Frontend Dependencies

```bash
cd frontend

# Install ChatKit and dependencies
npm install @openai/chatkit

# Or using yarn
yarn add @openai/chatkit
```

---

## Step 3: Configure Environment Variables

### Backend (.env)

Add to `backend/.env`:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-your-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=xiaomi/mimo-v2-flash:free

# Existing variables (no changes)
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET=your-jwt-secret
```

### Frontend (.env.local)

Add to `frontend/.env.local`:

```bash
# Chat API endpoint (points to backend)
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000/api

# Existing variables (no changes)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Step 4: Run Database Migration

### Create Migration

```bash
cd backend

# Generate migration for new tables
alembic revision --autogenerate -m "Add conversation and message tables"

# Review the generated migration
cat alembic/versions/003_*.py
```

### Apply Migration

```bash
# Apply migration to database
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: conversations, messages, tasks, users
```

### Verify Schema

```bash
# Check conversations table
psql $DATABASE_URL -c "\d conversations"

# Check messages table
psql $DATABASE_URL -c "\d messages"
```

---

## Step 5: Start the Application

### Terminal 1: Backend Server

```bash
cd backend

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

### Terminal 2: Frontend Server

```bash
cd frontend

# Start Next.js dev server
npm run dev

# Expected output:
# ▲ Next.js 16.x.x
# - Local:        http://localhost:3000
```

### Terminal 3: MCP Server (Optional)

```bash
cd backend

# Start MCP server for task tools
python -m mcp_server.task_tools

# Expected output:
# MCP Server running: task-management
# Tools registered: add_task, list_tasks, complete_task, delete_task, update_task
```

---

## Step 6: Test the Chat Feature

### 1. Login to Application

1. Open browser: http://localhost:3000
2. Login with existing user credentials
3. Verify JWT token is set (check browser DevTools → Application → Cookies)

### 2. Navigate to Chat

1. Go to http://localhost:3000/chat
2. You should see the chat interface with:
   - Message input box
   - Microphone button (if browser supports Web Speech API)
   - Empty conversation area

### 3. Test Task Creation

**Type in chat**:
```
Add buy groceries to my tasks
```

**Expected response**:
```
Task created: buy groceries
```

**Verify**:
- Check tasks page: http://localhost:3000/tasks
- New task "buy groceries" should appear

### 4. Test Task Listing

**Type in chat**:
```
Show me my tasks
```

**Expected response**:
```
You have 1 active task:
1. buy groceries
```

### 5. Test Voice Input (Optional)

1. Click microphone button
2. Speak: "Add call dentist to my tasks"
3. Wait for transcription
4. Message should appear in input box
5. Press Enter to send

### 6. Test Urdu Language

**Type in chat**:
```
میرے کام دکھاؤ
```

**Expected response** (in Urdu):
```
آپ کے 2 فعال کام ہیں:
1. buy groceries
2. call dentist
```

---

## Step 7: Verify MCP Tools

### Test MCP Tools Directly

```bash
# Test add_task tool
echo '{"user_id": "test_user", "title": "Test task"}' | \
  mcp call task-management add_task

# Expected output:
# {
#   "success": true,
#   "task": { ... },
#   "message": "Task created successfully"
# }

# Test list_tasks tool
echo '{"user_id": "test_user", "status": "active"}' | \
  mcp call task-management list_tasks

# Expected output:
# {
#   "success": true,
#   "tasks": [ ... ],
#   "count": 1
# }
```

---

## Development Mode (Without OpenRouter API)

If you don't have an OpenRouter API key, you can use a mock implementation:

### Backend Mock Service

Create `backend/app/services/chat_service_mock.py`:

```python
class MockChatService:
    async def send_message(self, user_id: str, message: str, conversation_id: str = None):
        # Simple rule-based responses for testing
        if "add" in message.lower() or "create" in message.lower():
            return {
                "response": "Task created successfully (mock)",
                "conversation_id": "mock-conversation-id",
                "message_id": "mock-message-id"
            }
        elif "show" in message.lower() or "list" in message.lower():
            return {
                "response": "You have 0 tasks (mock)",
                "conversation_id": "mock-conversation-id",
                "message_id": "mock-message-id"
            }
        else:
            return {
                "response": "I understand. (mock)",
                "conversation_id": "mock-conversation-id",
                "message_id": "mock-message-id"
            }
```

### Enable Mock Mode

In `backend/.env`:
```bash
USE_MOCK_CHAT=true
```

---

## Troubleshooting

### Issue: "Authentication required" error

**Cause**: JWT token missing or invalid

**Solution**:
1. Verify you're logged in
2. Check browser cookies for JWT token
3. Try logging out and back in
4. Check backend logs for JWT verification errors

### Issue: "OpenRouter API error"

**Cause**: Invalid API key or rate limit exceeded

**Solution**:
1. Verify `OPENROUTER_API_KEY` in `.env`
2. Check API key is valid on OpenRouter dashboard
3. Wait 60 seconds if rate limited
4. Use mock mode for development

### Issue: "Conversation not found"

**Cause**: Database migration not applied or conversation deleted

**Solution**:
1. Run `alembic upgrade head`
2. Verify tables exist: `psql $DATABASE_URL -c "\dt"`
3. Start a new conversation (don't pass conversation_id)

### Issue: Microphone button not showing

**Cause**: Browser doesn't support Web Speech API

**Solution**:
1. Use Chrome or Edge (best support)
2. Enable microphone permissions
3. Use HTTPS in production (required for Web Speech API)
4. Fallback to text input if unavailable

### Issue: Urdu text not displaying correctly

**Cause**: Font or encoding issue

**Solution**:
1. Verify UTF-8 encoding in database
2. Check browser font supports Urdu characters
3. Add Urdu font to Tailwind config if needed

### Issue: "User ID mismatch" error

**Cause**: URL user_id doesn't match JWT token user_id

**Solution**:
1. Verify you're accessing `/api/{your_user_id}/chat`
2. Check JWT token payload matches URL
3. Don't manually change user_id in URL

---

## Testing Checklist

Before considering setup complete, verify:

- [ ] Backend server running without errors
- [ ] Frontend server running without errors
- [ ] Database migration applied successfully
- [ ] Can login and see JWT token in cookies
- [ ] Chat page loads at /chat
- [ ] Can send a message and receive response
- [ ] Task creation via chat works
- [ ] Task listing via chat works
- [ ] Conversation history persists across page reloads
- [ ] Voice input button appears (if browser supports)
- [ ] Urdu input/output works correctly
- [ ] Error messages display properly
- [ ] No console errors in browser DevTools

---

## Next Steps

### For Development
1. Run tests: `pytest backend/tests/`
2. Check code coverage: `pytest --cov=app`
3. Review API documentation: http://localhost:8000/docs

### For Production Deployment
1. Set production environment variables
2. Use production OpenRouter API key (paid tier for better performance)
3. Enable HTTPS (required for Web Speech API)
4. Configure rate limiting
5. Set up monitoring and logging
6. Run security audit

### For Feature Enhancement
1. Add conversation search
2. Implement conversation deletion
3. Add task priority support
4. Support more languages
5. Add voice output (text-to-speech)

---

## Useful Commands

### Backend

```bash
# Run tests
pytest backend/tests/

# Run specific test file
pytest backend/tests/unit/test_chat_service.py

# Check code coverage
pytest --cov=app --cov-report=html

# Format code
black backend/app/

# Lint code
flake8 backend/app/

# Type check
mypy backend/app/
```

### Frontend

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Build for production
npm run build

# Type check
npm run type-check

# Lint
npm run lint
```

### Database

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Connect to database
psql $DATABASE_URL
```

---

## Resources

- **OpenRouter Docs**: https://openrouter.ai/docs
- **OpenAI ChatKit**: https://github.com/openai/chatkit
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **MCP Specification**: https://modelcontextprotocol.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs

---

## Support

If you encounter issues not covered in this guide:

1. Check backend logs: `tail -f backend/logs/app.log`
2. Check frontend console: Browser DevTools → Console
3. Review API documentation: http://localhost:8000/docs
4. Check database logs: `psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"`
5. Consult the spec: `/specs/003-ai-todo-chatbot/spec.md`
6. Review the plan: `/specs/003-ai-todo-chatbot/plan.md`

---

**Setup Complete!** You now have a working AI-powered todo chatbot. Start chatting with your tasks! 🎉
