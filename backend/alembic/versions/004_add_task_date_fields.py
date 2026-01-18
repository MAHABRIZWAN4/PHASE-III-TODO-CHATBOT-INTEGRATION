"""Add due_date and completed_at fields to tasks table

Revision ID: 004_add_task_date_fields
Revises: 003_add_chat_models
Create Date: 2026-01-17

This migration adds two new datetime fields to the tasks table:
- due_date: Optional due date for task completion
- completed_at: Timestamp when task was marked as completed

These fields support the AI-Powered Todo Chatbot MCP tools functionality.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '004_add_task_date_fields'
down_revision = '003_add_chat_models'
branch_labels = None
depends_on = None


def upgrade():
    """Add due_date and completed_at columns to tasks table."""

    # Add due_date column (nullable)
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))

    # Add completed_at column (nullable)
    op.add_column('tasks', sa.Column('completed_at', sa.DateTime(), nullable=True))


def downgrade():
    """Remove due_date and completed_at columns from tasks table."""

    # Drop completed_at column
    op.drop_column('tasks', 'completed_at')

    # Drop due_date column
    op.drop_column('tasks', 'due_date')
