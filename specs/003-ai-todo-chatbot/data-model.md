# Data Model: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Phase**: 1 - Design
**Date**: 2026-01-17

## Overview

This document defines the database schema for conversation storage in the AI-powered todo chatbot feature. The design adds two new models (Conversation and Message) while maintaining backward compatibility with the existing Task model.

---

## Entity Relationship Diagram

```
User (existing, managed by Better Auth)
  |
  | 1:N
  |
  ├─── Task (existing, no changes)
  |
  └─── Conversation (NEW)
         |
         | 1:N
         |
         └─── Message (NEW)
```

---

## Model 1: Conversation

### Purpose
Groups related messages into conversation sessions. Each user can have multiple conversations, and each conversation belongs to exactly one user.

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier"
    )

    # Foreign Keys
    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this conversation (Better Auth user ID)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When the conversation was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="When the conversation was last updated"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Indexes
    class Config:
        indexes = [
            {"fields": ["user_id", "created_at"], "name": "idx_conversations_user_created"}
        ]
```

### Field Specifications

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier |
| user_id | String | FOREIGN KEY (users.id), NOT NULL, INDEXED | Owner of conversation |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW(), ON UPDATE NOW() | Last update timestamp |

### Validation Rules

1. **user_id**: Must reference existing user in Better Auth users table
2. **created_at**: Automatically set on creation, immutable
3. **updated_at**: Automatically updated on any message addition
4. **Deletion**: Cascade delete all messages when conversation deleted

### Indexes

- **Primary Index**: `id` (UUID, clustered)
- **User Lookup**: `user_id` (for filtering conversations by user)
- **Composite Index**: `(user_id, created_at)` (for paginated conversation list queries)

### Business Rules

1. Each conversation must belong to exactly one user
2. Users can only access their own conversations (enforced by API layer)
3. Empty conversations (no messages) are allowed but should be cleaned up periodically
4. Conversations have no explicit "closed" state - all are active

---

## Model 2: Message

### Purpose
Stores individual messages within a conversation. Messages can be from the user or the AI assistant.

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"  # For internal messages (e.g., errors)

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    # Foreign Keys
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Conversation this message belongs to"
    )

    # Message Content
    role: MessageRole = Field(
        nullable=False,
        description="Who sent the message: user, assistant, or system"
    )

    content: str = Field(
        nullable=False,
        max_length=10000,
        description="Message text content"
    )

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Optional metadata (tool calls, errors, language, etc.)"
    )

    # Timestamps
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When the message was sent"
    )

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")

    # Indexes
    class Config:
        indexes = [
            {"fields": ["conversation_id", "timestamp"], "name": "idx_messages_conversation_time"}
        ]
```

### Field Specifications

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier |
| conversation_id | UUID | FOREIGN KEY (conversations.id), NOT NULL, INDEXED | Parent conversation |
| role | Enum | NOT NULL, CHECK IN ('user', 'assistant', 'system') | Message sender |
| content | String | NOT NULL, MAX LENGTH 10000 | Message text |
| metadata | JSON | NULLABLE | Optional structured data |
| timestamp | DateTime | NOT NULL, DEFAULT NOW() | Message timestamp |

### Validation Rules

1. **conversation_id**: Must reference existing conversation
2. **role**: Must be one of: "user", "assistant", "system"
3. **content**:
   - Cannot be empty string
   - Maximum 10,000 characters
   - Must be valid UTF-8 (supports English and Urdu)
4. **metadata**:
   - Optional JSON object
   - Used for storing tool call results, error details, detected language
   - Schema: `{tool_calls?: [], language?: string, error?: string}`
5. **timestamp**: Automatically set on creation, immutable

### Indexes

- **Primary Index**: `id` (UUID, clustered)
- **Conversation Lookup**: `conversation_id` (for fetching all messages in a conversation)
- **Composite Index**: `(conversation_id, timestamp)` (for ordered message retrieval)

### Business Rules

1. Messages are immutable once created (no updates, only inserts)
2. Messages must belong to exactly one conversation
3. Message order determined by `timestamp` field
4. System messages used for internal errors, not shown to user in UI
5. Metadata is optional and extensible

### Metadata Schema

```typescript
interface MessageMetadata {
  // Tool calls made by the assistant
  tool_calls?: Array<{
    tool: string;           // e.g., "add_task"
    arguments: object;      // Tool input
    result: object;         // Tool output
    success: boolean;
  }>;

  // Detected language
  language?: "english" | "urdu";

  // Error information (for system messages)
  error?: {
    code: string;           // e.g., "RATE_LIMIT"
    message: string;
    details?: any;
  };

  // OpenRouter API metadata
  model?: string;           // e.g., "xiaomi/mimo-v2-flash:free"
  tokens?: {
    prompt: number;
    completion: number;
    total: number;
  };
}
```

---

## Model 3: Task (Existing - No Changes)

### Purpose
Stores user tasks. This model is NOT modified by this feature.

### Reference Schema

```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)
```

### Interaction with Chat Feature

- MCP tools (add_task, list_tasks, etc.) operate on this model
- No schema changes required
- Existing API endpoints remain unchanged
- Chat feature creates/modifies tasks via MCP tools only

---

## Database Migration

### Migration Script (Alembic)

```python
"""Add conversation and message tables

Revision ID: 003_add_chat_models
Revises: 002_previous_migration
Create Date: 2026-01-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers
revision = '003_add_chat_models'
down_revision = '002_previous_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for conversations
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_user_created', 'conversations', ['user_id', 'created_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.String(10000), nullable=False),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_message_role'),
    )

    # Create indexes for messages
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_conversation_time', 'messages', ['conversation_id', 'timestamp'])

def downgrade():
    # Drop messages table (cascade will handle foreign keys)
    op.drop_index('idx_messages_conversation_time', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table
    op.drop_index('idx_conversations_user_created', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
```

### Migration Execution

```bash
# Generate migration
alembic revision --autogenerate -m "Add conversation and message tables"

# Review generated migration
cat alembic/versions/003_add_chat_models.py

# Apply migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
psql $DATABASE_URL -c "\d conversations"
psql $DATABASE_URL -c "\d messages"
```

---

## Query Patterns

### Pattern 1: Get User's Conversations (Paginated)

```python
from sqlmodel import select

async def get_user_conversations(
    session: AsyncSession,
    user_id: str,
    limit: int = 20,
    offset: int = 0
) -> List[Conversation]:
    """Fetch user's conversations, most recent first"""
    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.exec(query)
    return result.all()
```

### Pattern 2: Get Conversation Messages (Ordered)

```python
async def get_conversation_messages(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: str
) -> List[Message]:
    """Fetch all messages in a conversation, oldest first"""
    # First verify user owns the conversation
    conversation = await session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.asc())
    )
    result = await session.exec(query)
    return result.all()
```

### Pattern 3: Create Conversation with Initial Message

```python
async def create_conversation_with_message(
    session: AsyncSession,
    user_id: str,
    user_message: str
) -> Conversation:
    """Create new conversation and add user's first message"""
    # Create conversation
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.flush()  # Get conversation.id

    # Add user message
    message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=user_message,
        metadata={"language": detect_language(user_message)}
    )
    session.add(message)

    await session.commit()
    await session.refresh(conversation)
    return conversation
```

### Pattern 4: Add Message to Existing Conversation

```python
async def add_message(
    session: AsyncSession,
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    metadata: Optional[Dict] = None
) -> Message:
    """Add a message to an existing conversation"""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        metadata=metadata
    )
    session.add(message)

    # Update conversation's updated_at timestamp
    conversation = await session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(message)
    return message
```

---

## Performance Considerations

### Indexing Strategy
- **Primary lookups**: UUID primary keys (fast)
- **User filtering**: Index on `user_id` (conversations)
- **Message ordering**: Composite index on `(conversation_id, timestamp)` (messages)
- **Conversation listing**: Composite index on `(user_id, created_at)` (conversations)

### Query Optimization
- Use pagination for conversation lists (LIMIT/OFFSET)
- Fetch messages in batches if conversation is very long
- Consider adding `message_count` field to Conversation for quick stats (denormalized)

### Storage Estimates
- Average conversation: 10-20 messages
- Average message size: 100-500 bytes
- 1000 users × 10 conversations × 15 messages × 300 bytes = ~45 MB
- Neon PostgreSQL free tier: 512 MB (sufficient for initial deployment)

### Cleanup Strategy
- Archive conversations older than 1 year (optional)
- Delete empty conversations after 7 days (optional)
- No automatic deletion of messages (audit trail)

---

## Data Integrity Constraints

### Foreign Key Constraints
1. `conversations.user_id` → `users.id` (CASCADE DELETE)
2. `messages.conversation_id` → `conversations.id` (CASCADE DELETE)

### Check Constraints
1. `messages.role` IN ('user', 'assistant', 'system')
2. `messages.content` LENGTH > 0
3. `conversations.created_at` <= `conversations.updated_at`

### Application-Level Constraints
1. User can only access their own conversations (enforced by API)
2. Messages are immutable (no UPDATE operations)
3. Conversation ownership cannot be transferred

---

## Testing Data

### Test Fixtures

```python
import pytest
from datetime import datetime
from uuid import uuid4

@pytest.fixture
def test_conversation(session, test_user_id):
    """Create a test conversation"""
    conversation = Conversation(
        id=uuid4(),
        user_id=test_user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    return conversation

@pytest.fixture
def test_messages(session, test_conversation):
    """Create test messages"""
    messages = [
        Message(
            conversation_id=test_conversation.id,
            role=MessageRole.USER,
            content="Add buy milk to my tasks",
            timestamp=datetime.utcnow()
        ),
        Message(
            conversation_id=test_conversation.id,
            role=MessageRole.ASSISTANT,
            content="Task created: buy milk",
            metadata={"tool_calls": [{"tool": "add_task", "success": True}]},
            timestamp=datetime.utcnow()
        )
    ]
    for msg in messages:
        session.add(msg)
    session.commit()
    return messages
```

---

## Summary

### New Tables
- **conversations**: 4 columns, 2 indexes, ~100 bytes per row
- **messages**: 6 columns, 2 indexes, ~300 bytes per row (average)

### Relationships
- User → Conversations (1:N)
- Conversation → Messages (1:N)
- No changes to existing Task model

### Migration Impact
- Additive only (no breaking changes)
- Backward compatible with Phase-II
- Estimated migration time: <1 second (empty tables)

### Next Steps
1. Create API contracts (contracts/chat-api.yaml)
2. Create MCP tool schemas (contracts/mcp-tools.json)
3. Create quickstart guide (quickstart.md)
4. Update agent context files
