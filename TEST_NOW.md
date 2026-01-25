# 🧪 TEST INSTRUCTIONS

## Quick Test (2 minutes)

1. **Open Chat Page**
   - Go to: http://localhost:3000/chat
   - Press F12 to open DevTools
   - Click on "Console" tab

2. **Send Test Message**
   - Type: "Add task to buy groceries"
   - Press Send

3. **Answer Questions**
   When chatbot asks, reply with:
   - Task Title: Buy groceries
   - Due date: Tomorrow
   - Priority: Medium
   - Category: Shopping

4. **Watch Console**
   You should see these logs:
   ```
   [ChatInterface] Tool calls received: ...
   [ChatInterface] Task added: true
   [ChatInterface] Triggering task refresh...
   [TaskUpdateContext] triggerTaskRefresh called, callbacks: 1
   [TaskList] Task refresh triggered! Fetching tasks...
   ```

5. **Check Dashboard**
   - Go to: http://localhost:3000/dashboard
   - Task "Buy groceries" should appear

## If It Works ✅
Great! The issue is fixed. You can now:
- Remove the console.log statements if you want
- Use the chat normally

## If It Doesn't Work ❌
Take a screenshot of:
1. Browser console (all the logs)
2. Network tab → /api/{user_id}/chat → Response
3. Dashboard page

Then I can debug further.

---

**Backend:** http://localhost:8001 (running with auto-reload)
**Frontend:** http://localhost:3000
