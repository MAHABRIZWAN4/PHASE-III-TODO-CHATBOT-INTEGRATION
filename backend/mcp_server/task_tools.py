"""MCP Task Management Tools.

This module implements 5 MCP tools for task CRUD operations:
- add_task: Create new task
- list_tasks: Retrieve tasks with filtering
- complete_task: Mark task as completed
- delete_task: Remove task
- update_task: Modify task properties

All tools enforce user isolation and return standardized JSON responses.

Reference: T009-T015 from specs/003-ai-todo-chatbot/tasks.md
"""

import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# Import models and database
from models import Task
from db import async_session_maker


# ============================================================================
# MCP Tool Implementations (T009-T013)
# ============================================================================


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = "medium",
    category: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new task for a user.

    Args:
        user_id: User ID for security isolation (must match authenticated user)
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)
        due_date: Optional due date in ISO 8601 format
        priority: Task priority (high, medium, low), defaults to medium
        category: Task category (personal, work, shopping, etc.)

    Returns:
        Dict with success status, task object, and message or error

    Reference: T009 - Implement add_task MCP tool
    """
    try:
        # Validate inputs
        if not user_id or not user_id.strip():
            return {
                "success": False,
                "error": "User ID is required",
                "code": "VALIDATION_ERROR"
            }

        if not title or not title.strip():
            return {
                "success": False,
                "error": "Title cannot be empty",
                "code": "VALIDATION_ERROR"
            }

        if len(title) > 200:
            return {
                "success": False,
                "error": "Title must be 200 characters or less",
                "code": "VALIDATION_ERROR"
            }

        if description and len(description) > 1000:
            return {
                "success": False,
                "error": "Description must be 1000 characters or less",
                "code": "VALIDATION_ERROR"
            }

        # Validate priority
        if priority and priority.lower() not in ["high", "medium", "low"]:
            return {
                "success": False,
                "error": "Priority must be 'high', 'medium', or 'low'",
                "code": "VALIDATION_ERROR"
            }

        # Validate category length
        if category and len(category) > 50:
            return {
                "success": False,
                "error": "Category must be 50 characters or less",
                "code": "VALIDATION_ERROR"
            }

        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return {
                    "success": False,
                    "error": "Invalid due_date format. Use ISO 8601 format (e.g., 2026-01-20T00:00:00Z)",
                    "code": "VALIDATION_ERROR"
                }

        # Create task in database
        async with async_session_maker() as session:
            new_task = Task(
                user_id=user_id,
                title=title.strip(),
                description=description.strip() if description else None,
                due_date=parsed_due_date,
                priority=priority.lower() if priority else "medium",
                category=category.strip() if category else None,
                completed=False
            )

            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)

            # Build response
            return {
                "success": True,
                "task": {
                    "id": str(new_task.id),
                    "user_id": new_task.user_id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "completed": new_task.completed,
                    "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                    "priority": new_task.priority,
                    "category": new_task.category,
                    "created_at": new_task.created_at.isoformat(),
                    "updated_at": new_task.updated_at.isoformat()
                },
                "message": "Task created successfully"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR"
        }


async def list_tasks(
    user_id: str,
    status: str = "all",
    due_before: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Retrieve tasks with optional filtering.

    Args:
        user_id: User ID for security isolation
        status: Filter by completion status (all/active/completed)
        due_before: Filter tasks due before this date (ISO 8601)
        limit: Maximum number of tasks to return (1-100, default 100)

    Returns:
        Dict with success status, tasks array, count, and filtered_by info

    Reference: T010 - Implement list_tasks MCP tool
    """
    try:
        # Validate inputs
        if not user_id or not user_id.strip():
            return {
                "success": False,
                "error": "User ID is required",
                "code": "VALIDATION_ERROR"
            }

        if status not in ["all", "active", "completed"]:
            return {
                "success": False,
                "error": "Status must be 'all', 'active', or 'completed'",
                "code": "VALIDATION_ERROR"
            }

        if limit < 1 or limit > 100:
            return {
                "success": False,
                "error": "Limit must be between 1 and 100",
                "code": "VALIDATION_ERROR"
            }

        # Parse due_before if provided
        parsed_due_before = None
        if due_before:
            try:
                parsed_due_before = datetime.fromisoformat(due_before.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return {
                    "success": False,
                    "error": "Invalid due_before format. Use ISO 8601 format",
                    "code": "VALIDATION_ERROR"
                }

        # Query tasks
        async with async_session_maker() as session:
            query = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "active":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)

            # Apply due_before filter
            if parsed_due_before:
                query = query.where(Task.due_date <= parsed_due_before)

            # Apply limit and order
            query = query.order_by(Task.created_at.desc()).limit(limit)

            result = await session.exec(query)
            tasks = result.all()

            # Build response
            task_list = [
                {
                    "id": str(task.id),
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "category": task.category,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]

            filtered_by = {"status": status}
            if due_before:
                filtered_by["due_before"] = due_before

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list),
                "filtered_by": filtered_by
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR"
        }


async def complete_task(
    user_id: str,
    task_id: str
) -> Dict[str, Any]:
    """Mark a task as completed.

    Args:
        user_id: User ID for security isolation
        task_id: ID of the task to complete

    Returns:
        Dict with success status, updated task, and message or error

    Reference: T011 - Implement complete_task MCP tool
    """
    try:
        # Validate inputs
        if not user_id or not user_id.strip():
            return {
                "success": False,
                "error": "User ID is required",
                "code": "VALIDATION_ERROR"
            }

        if not task_id or not task_id.strip():
            return {
                "success": False,
                "error": "Task ID is required",
                "code": "VALIDATION_ERROR"
            }

        # Convert task_id to int
        try:
            task_id_int = int(task_id)
        except ValueError:
            return {
                "success": False,
                "error": "Invalid task ID format",
                "code": "VALIDATION_ERROR"
            }

        # Get and update task
        async with async_session_maker() as session:
            task = await session.get(Task, task_id_int)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "code": "NOT_FOUND"
                }

            # Validate ownership
            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Unauthorized: Task does not belong to this user",
                    "code": "UNAUTHORIZED"
                }

            # Mark as completed
            task.completed = True
            task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()

            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "user_id": task.user_id,
                    "title": task.title,
                    "completed": task.completed,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "updated_at": task.updated_at.isoformat()
                },
                "message": "Task marked as completed"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR"
        }


async def delete_task(
    user_id: str,
    task_id: str
) -> Dict[str, Any]:
    """Permanently remove a task.

    Args:
        user_id: User ID for security isolation
        task_id: ID of the task to delete

    Returns:
        Dict with success status, message, and deleted_task_id or error

    Reference: T012 - Implement delete_task MCP tool
    """
    try:
        # Validate inputs
        if not user_id or not user_id.strip():
            return {
                "success": False,
                "error": "User ID is required",
                "code": "VALIDATION_ERROR"
            }

        if not task_id or not task_id.strip():
            return {
                "success": False,
                "error": "Task ID is required",
                "code": "VALIDATION_ERROR"
            }

        # Convert task_id to int
        try:
            task_id_int = int(task_id)
        except ValueError:
            return {
                "success": False,
                "error": "Invalid task ID format",
                "code": "VALIDATION_ERROR"
            }

        # Get and delete task
        async with async_session_maker() as session:
            task = await session.get(Task, task_id_int)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "code": "NOT_FOUND"
                }

            # Validate ownership
            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Unauthorized: Task does not belong to this user",
                    "code": "UNAUTHORIZED"
                }

            # Delete task
            await session.delete(task)
            await session.commit()

            return {
                "success": True,
                "message": "Task deleted successfully",
                "deleted_task_id": task_id
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR"
        }


async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """Update task properties.

    Args:
        user_id: User ID for security isolation
        task_id: ID of the task to update
        title: New task title (optional, 1-200 characters)
        description: New task description (optional, max 1000 characters)
        due_date: New due date (optional, ISO 8601 format)
        priority: New priority (optional, high/medium/low)
        category: New category (optional, max 50 characters)

    Returns:
        Dict with success status, updated task, and message or error

    Reference: T013 - Implement update_task MCP tool
    """
    try:
        # Validate inputs
        if not user_id or not user_id.strip():
            return {
                "success": False,
                "error": "User ID is required",
                "code": "VALIDATION_ERROR"
            }

        if not task_id or not task_id.strip():
            return {
                "success": False,
                "error": "Task ID is required",
                "code": "VALIDATION_ERROR"
            }

        # Convert task_id to int
        try:
            task_id_int = int(task_id)
        except ValueError:
            return {
                "success": False,
                "error": "Invalid task ID format",
                "code": "VALIDATION_ERROR"
            }

        # Validate optional fields
        if title is not None:
            if not title.strip():
                return {
                    "success": False,
                    "error": "Title cannot be empty",
                    "code": "VALIDATION_ERROR"
                }
            if len(title) > 200:
                return {
                    "success": False,
                    "error": "Title must be 200 characters or less",
                    "code": "VALIDATION_ERROR"
                }

        if description is not None and len(description) > 1000:
            return {
                "success": False,
                "error": "Description must be 1000 characters or less",
                "code": "VALIDATION_ERROR"
            }

        # Validate priority
        if priority is not None and priority.lower() not in ["high", "medium", "low"]:
            return {
                "success": False,
                "error": "Priority must be 'high', 'medium', or 'low'",
                "code": "VALIDATION_ERROR"
            }

        # Validate category length
        if category is not None and len(category) > 50:
            return {
                "success": False,
                "error": "Category must be 50 characters or less",
                "code": "VALIDATION_ERROR"
            }

        # Parse due_date if provided
        parsed_due_date = None
        if due_date is not None:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return {
                    "success": False,
                    "error": "Invalid due_date format. Use ISO 8601 format",
                    "code": "VALIDATION_ERROR"
                }

        # Get and update task
        async with async_session_maker() as session:
            task = await session.get(Task, task_id_int)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "code": "NOT_FOUND"
                }

            # Validate ownership
            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Unauthorized: Task does not belong to this user",
                    "code": "UNAUTHORIZED"
                }

            # Update fields if provided
            if title is not None:
                task.title = title.strip()
            if description is not None:
                task.description = description.strip() if description else None
            if due_date is not None:
                task.due_date = parsed_due_date
            if priority is not None:
                task.priority = priority.lower()
            if category is not None:
                task.category = category.strip() if category else None

            task.updated_at = datetime.utcnow()

            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "category": task.category,
                    "updated_at": task.updated_at.isoformat()
                },
                "message": "Task updated successfully"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR"
        }


# ============================================================================
# MCP Server Handlers (T014-T015)
# ============================================================================


def list_tools() -> List[Dict[str, Any]]:
    """Register all 5 MCP tools.

    Returns list of tool definitions with input/output schemas.

    Reference: T014 - Register all 5 MCP tools in list_tools() handler
    """
    return [
        {
            "name": "add_task",
            "description": "Create a new task for a user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID for security isolation (must match authenticated user)"
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "description": "Task title (required)"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000,
                        "description": "Optional task description"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Optional due date in ISO 8601 format"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "default": "medium",
                        "description": "Task priority (high, medium, low)"
                    },
                    "category": {
                        "type": "string",
                        "maxLength": 50,
                        "description": "Task category (personal, work, shopping, etc.)"
                    }
                },
                "required": ["user_id", "title"]
            }
        },
        {
            "name": "list_tasks",
            "description": "Retrieve tasks with optional filtering",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID for security isolation"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "active", "completed"],
                        "default": "all",
                        "description": "Filter by completion status"
                    },
                    "due_before": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Filter tasks due before this date"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 100,
                        "description": "Maximum number of tasks to return"
                    }
                },
                "required": ["user_id"]
            }
        },
        {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID for security isolation"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "ID of the task to complete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        },
        {
            "name": "delete_task",
            "description": "Permanently remove a task",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID for security isolation"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "ID of the task to delete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        },
        {
            "name": "update_task",
            "description": "Update task properties",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID for security isolation"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "description": "New task title"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000,
                        "description": "New task description"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "New due date"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "New task priority"
                    },
                    "category": {
                        "type": "string",
                        "maxLength": 50,
                        "description": "New task category"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    ]


async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Route MCP tool calls to appropriate handler.

    Args:
        name: Tool name (add_task, list_tasks, complete_task, delete_task, update_task)
        arguments: Tool arguments as dict

    Returns:
        Tool execution result

    Reference: T015 - Implement MCP server call_tool() router
    """
    if name == "add_task":
        return await add_task(
            user_id=arguments.get("user_id"),
            title=arguments.get("title"),
            description=arguments.get("description"),
            due_date=arguments.get("due_date"),
            priority=arguments.get("priority", "medium"),
            category=arguments.get("category")
        )

    elif name == "list_tasks":
        return await list_tasks(
            user_id=arguments.get("user_id"),
            status=arguments.get("status", "all"),
            due_before=arguments.get("due_before"),
            limit=arguments.get("limit", 100)
        )

    elif name == "complete_task":
        return await complete_task(
            user_id=arguments.get("user_id"),
            task_id=arguments.get("task_id")
        )

    elif name == "delete_task":
        return await delete_task(
            user_id=arguments.get("user_id"),
            task_id=arguments.get("task_id")
        )

    elif name == "update_task":
        return await update_task(
            user_id=arguments.get("user_id"),
            task_id=arguments.get("task_id"),
            title=arguments.get("title"),
            description=arguments.get("description"),
            due_date=arguments.get("due_date"),
            priority=arguments.get("priority"),
            category=arguments.get("category")
        )

    else:
        return {
            "success": False,
            "error": f"Unknown tool: {name}",
            "code": "VALIDATION_ERROR"
        }
