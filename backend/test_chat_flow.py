#!/usr/bin/env python3
"""Test script to debug chat flow and task creation."""

import asyncio
import sys
from uuid import uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.requests import ChatRequest
from app.services.chat_service import ChatService
from db import async_session_maker


async def test_chat_flow():
    """Test the complete chat flow for task creation."""

    # You need to replace this with your actual user ID from localStorage
    USER_ID = "YOUR_USER_ID_HERE"  # Replace this!

    print("=" * 80)
    print("CHAT FLOW TEST - Task Creation")
    print("=" * 80)
    print()

    # Initialize chat service
    chat_service = ChatService()

    async with async_session_maker() as session:
        # Test 1: Send initial message
        print("📤 Test 1: Sending initial message...")
        print("   Message: 'Add task to buy groceries'")
        print()

        request1 = ChatRequest(message="Add task to buy groceries")

        try:
            response1 = await chat_service.send_message(
                user_id=USER_ID,
                request=request1,
                session=session
            )

            print(f"✓ Response received:")
            print(f"  Conversation ID: {response1.conversation_id}")
            print(f"  Response: {response1.response[:100]}...")
            print(f"  Tool calls: {response1.metadata.get('tool_calls', [])}")
            print(f"  Conversation state: {response1.metadata.get('conversation_state')}")
            print()

            conversation_id = response1.conversation_id

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return

        # Test 2: Answer with structured format
        print("📤 Test 2: Answering with structured format...")
        print("   Message: 'Task Title: Buy groceries'")
        print()

        request2 = ChatRequest(
            message="Task Title: Buy groceries",
            conversation_id=conversation_id
        )

        try:
            response2 = await chat_service.send_message(
                user_id=USER_ID,
                request=request2,
                session=session
            )

            print(f"✓ Response received:")
            print(f"  Response: {response2.response[:100]}...")
            print(f"  Tool calls: {response2.metadata.get('tool_calls', [])}")
            print(f"  Conversation state: {response2.metadata.get('conversation_state')}")
            print()

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return

        # Test 3: Continue with due date
        print("📤 Test 3: Providing due date...")
        print("   Message: 'Due date: Tomorrow'")
        print()

        request3 = ChatRequest(
            message="Due date: Tomorrow",
            conversation_id=conversation_id
        )

        try:
            response3 = await chat_service.send_message(
                user_id=USER_ID,
                request=request3,
                session=session
            )

            print(f"✓ Response received:")
            print(f"  Response: {response3.response[:100]}...")
            print(f"  Tool calls: {response3.metadata.get('tool_calls', [])}")
            print(f"  Conversation state: {response3.metadata.get('conversation_state')}")
            print()

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return

        # Test 4: Provide priority
        print("📤 Test 4: Providing priority...")
        print("   Message: 'Priority: Medium'")
        print()

        request4 = ChatRequest(
            message="Priority: Medium",
            conversation_id=conversation_id
        )

        try:
            response4 = await chat_service.send_message(
                user_id=USER_ID,
                request=request4,
                session=session
            )

            print(f"✓ Response received:")
            print(f"  Response: {response4.response[:100]}...")
            print(f"  Tool calls: {response4.metadata.get('tool_calls', [])}")

            if response4.metadata.get('tool_calls'):
                for call in response4.metadata['tool_calls']:
                    print(f"\n  🔧 Tool Call:")
                    print(f"     Tool: {call.get('tool')}")
                    print(f"     Success: {call.get('success')}")
                    if call.get('result'):
                        print(f"     Result: {call.get('result')}")
                    if call.get('error'):
                        print(f"     Error: {call.get('error')}")

            print(f"  Conversation state: {response4.metadata.get('conversation_state')}")
            print()

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return

        # Test 5: Provide category
        print("📤 Test 5: Providing category...")
        print("   Message: 'Category: Shopping'")
        print()

        request5 = ChatRequest(
            message="Category: Shopping",
            conversation_id=conversation_id
        )

        try:
            response5 = await chat_service.send_message(
                user_id=USER_ID,
                request=request5,
                session=session
            )

            print(f"✓ Response received:")
            print(f"  Response: {response5.response[:100]}...")
            print(f"  Tool calls: {response5.metadata.get('tool_calls', [])}")

            if response5.metadata.get('tool_calls'):
                for call in response5.metadata['tool_calls']:
                    print(f"\n  🔧 Tool Call:")
                    print(f"     Tool: {call.get('tool')}")
                    print(f"     Success: {call.get('success')}")
                    if call.get('result'):
                        print(f"     Result: {call.get('result')}")
                    if call.get('error'):
                        print(f"     Error: {call.get('error')}")

            print()

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return

        print("=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    print()
    print("⚠️  IMPORTANT: Edit this file and replace USER_ID with your actual user ID")
    print("   You can get it from browser console: JSON.parse(localStorage.getItem('auth_user')).id")
    print()

    asyncio.run(test_chat_flow())
