"""Add conversation and message tables for AI chat feature

Revision ID: 003_add_chat_models
Revises: 002_previous_migration
Create Date: 2026-01-17

This migration adds two new tables for the AI-Powered Todo Chatbot feature:
- conversations: Stores chat sessions for each user
- messages: Stores individual messages within conversations

Both tables support CASCADE deletion to maintain referential integrity.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic
revision = '003_add_chat_models'
down_revision = None  # Set to previous migration ID if exists
branch_labels = None
depends_on = None


def upgrade():
    """Create conversations and messages tables with indexes and constraints."""

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
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
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('conversation_id', UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.String(10000), nullable=False),
        sa.Column('meta_data', JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_message_role'),
    )

    # Create indexes for messages
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_conversation_time', 'messages', ['conversation_id', 'timestamp'])


def downgrade():
    """Drop messages and conversations tables with all indexes."""

    # Drop messages table (cascade will handle foreign keys)
    op.drop_index('idx_messages_conversation_time', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table
    op.drop_index('idx_conversations_user_created', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
