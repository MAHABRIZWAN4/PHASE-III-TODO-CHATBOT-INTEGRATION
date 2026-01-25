"""Debug script to test chat task creation flow.

Run this script to verify:
1. Chat endpoint is working
2. Tasks are being created in database
3. Response structure is correct
"""

import asyncio
import sys
from datetime import datetime

from sqlmodel import select
from app.services.chat_service import chat_service
from app.models.requests import ChatRequest
from models import Task
from db import async_session_maker


async def test_chat_task_creation():
    """Test the complete chat task creation flow."""

    # Test user ID (replace with your actual user ID from localStorage)
    test_user_id = "test-user-123"

    print("=" * 60)
    print("CHAT TASK CREATION DEBUG TEST")
    print("=" * 60)
    print()

    # Step 1: Check existing tasks for this user
    print(f"Step 1: Checking existing tasks for user: {test_user_id}")
    async with async_session_maker() as session:
        result = await session.exec(
            select(Task).where(Task.user_id == test_user_id)
        )
        existing_tasks = result.all()
        print(f"   Found {len(existing_tasks)} existing tasks")
        for task in existing_tasks:
            print(f"   - Task #{task.id}: {task.title} (completed: {task.completed})")
    print()

    # Step 2: Send a chat message to create a task
    print("Step 2: Sending chat message to create task...")
    chat_request = ChatRequest(
        message="Add task to buy groceries tomorrow with high priority in shopping category"
    )

    try:
        async with async_session_maker() as session:
            response = await chat_service.send_message(
                user_id=test_user_id,
                request=chat_request,
                session=session
            )

        print("   ✓ Chat service responded successfully")
        print(f"   Conversation ID: {response.conversation_id}")
        print(f"   Message ID: {response.message_id}")
        print(f"   Response: {response.response[:100]}...")
        print()

        # Step 3: Check metadata for tool calls
        print("Step 3: Checking metadata for tool calls...")
        if response.metadata and response.metadata.get("tool_calls"):
            tool_calls = response.metadata["tool_calls"]
            print(f"   Found {len(tool_calls)} tool call(s)")

            for i, call in enumerate(tool_calls):
                print(f"   Tool Call #{i+1}:")
                print(f"      Tool: {call.get('tool')}")
                print(f"      Success: {call.get('success')}")
                if call.get('result'):
                    result = call['result']
                    print(f"      Result Success: {result.get('success')}")
                    if result.get('task'):
                        task = result['task']
                        print(f"      Task ID: {task.get('id')}")
                        print(f"      Task Title: {task.get('title')}")
                if call.get('error'):
                    print(f"      Error: {call.get('error')}")
        else:
            print("   ⚠ No tool calls found in metadata!")
            print(f"   Metadata: {response.metadata}")
        print()

        # Step 4: Verify task was created in database
        print("Step 4: Verifying task in database...")
        async with async_session_maker() as session:
            result = await session.exec(
                select(Task)
                .where(Task.user_id == test_user_id)
                .order_by(Task.created_at.desc())
            )
            tasks = result.all()

            if len(tasks) > len(existing_tasks):
                print(f"   ✓ New task created! Total tasks: {len(tasks)}")
                new_task = tasks[0]
                print(f"   Task Details:")
                print(f"      ID: {new_task.id}")
                print(f"      Title: {new_task.title}")
                print(f"      User ID: {new_task.user_id}")
                print(f"      Priority: {new_task.priority}")
                print(f"      Category: {new_task.category}")
                print(f"      Due Date: {new_task.due_date}")
                print(f"      Completed: {new_task.completed}")
                print(f"      Created: {new_task.created_at}")
            else:
                print(f"   ✗ No new task created! Still {len(tasks)} tasks")
        print()

    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print()

    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print()
    print("INSTRUCTIONS:")
    print("1. Replace 'test-user-123' with your actual user ID from browser localStorage")
    print("2. Run: cd backend && python test_chat_debug.py")
    print("3. Check if task is created in database")
    print("4. If task is created, the issue is in the frontend refresh mechanism")
    print("5. If task is NOT created, the issue is in the backend MCP tool")


if __name__ == "__main__":
    asyncio.run(test_chat_task_creation())
