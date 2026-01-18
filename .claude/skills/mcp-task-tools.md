# MCP Task Management Tools

**Description**: Standard MCP tools for todo task CRUD operations with user isolation and database persistence

---

## Skill Purpose

Provide reusable MCP (Model Context Protocol) tools for task management that can be invoked by Claude agents to perform CRUD operations on todo tasks with proper user isolation and error handling.

---

## MCP Tools Overview

This skill defines 5 core MCP tools for task management:

1. **add_task** - Create a new task
2. **list_tasks** - Retrieve filtered tasks
3. **complete_task** - Mark a task as completed
4. **delete_task** - Remove a task
5. **update_task** - Update task properties

---

## Tool Definitions

### 1. add_task

**Purpose**: Create a new task in the database

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID for security isolation"
    },
    "title": {
      "type": "string",
      "description": "Task title (required, 1-200 chars)"
    },
    "description": {
      "type": "string",
      "description": "Optional task description (max 1000 chars)"
    },
    "due_date": {
      "type": "string",
      "description": "Optional due date in ISO 8601 format"
    }
  },
  "required": ["user_id", "title"]
}
```

**Response Format**:
```json
{
  "success": true,
  "task": {
    "id": "task_123",
    "user_id": "user_456",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "due_date": "2026-01-20T00:00:00Z",
    "created_at": "2026-01-17T10:30:00Z",
    "updated_at": "2026-01-17T10:30:00Z"
  },
  "message": "Task created successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Validation error: title cannot be empty",
  "code": "VALIDATION_ERROR"
}
```

---

### 2. list_tasks

**Purpose**: Retrieve tasks with optional filtering

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID for security isolation"
    },
    "status": {
      "type": "string",
      "enum": ["all", "active", "completed"],
      "description": "Filter by completion status (default: all)"
    },
    "due_before": {
      "type": "string",
      "description": "Filter tasks due before this date (ISO 8601)"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of tasks to return (default: 100)"
    }
  },
  "required": ["user_id"]
}
```

**Response Format**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task_123",
      "user_id": "user_456",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "due_date": "2026-01-20T00:00:00Z",
      "created_at": "2026-01-17T10:30:00Z",
      "updated_at": "2026-01-17T10:30:00Z"
    }
  ],
  "count": 1,
  "filtered_by": {
    "status": "active"
  }
}
```

---

### 3. complete_task

**Purpose**: Mark a task as completed

**Input Schema**:
```json
{
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
```

**Response Format**:
```json
{
  "success": true,
  "task": {
    "id": "task_123",
    "user_id": "user_456",
    "title": "Buy groceries",
    "completed": true,
    "completed_at": "2026-01-17T11:00:00Z",
    "updated_at": "2026-01-17T11:00:00Z"
  },
  "message": "Task marked as completed"
}
```

---

### 4. delete_task

**Purpose**: Permanently remove a task

**Input Schema**:
```json
{
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
```

**Response Format**:
```json
{
  "success": true,
  "message": "Task deleted successfully",
  "deleted_task_id": "task_123"
}
```

---

### 5. update_task

**Purpose**: Update task properties

**Input Schema**:
```json
{
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
      "description": "New task title (1-200 chars)"
    },
    "description": {
      "type": "string",
      "description": "New task description (max 1000 chars)"
    },
    "due_date": {
      "type": "string",
      "description": "New due date in ISO 8601 format"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Response Format**:
```json
{
  "success": true,
  "task": {
    "id": "task_123",
    "user_id": "user_456",
    "title": "Buy groceries and cook dinner",
    "description": "Updated description",
    "completed": false,
    "due_date": "2026-01-21T00:00:00Z",
    "updated_at": "2026-01-17T12:00:00Z"
  },
  "message": "Task updated successfully"
}
```

---

## Implementation Pattern

### MCP Server Structure

Create an MCP server in `backend/mcp_server/task_tools.py`:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
from sqlmodel import Session, select
from models import Task
from database import get_session
from datetime import datetime
import json

# Initialize MCP server
server = Server("task-management")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Register all task management tools"""
    return [
        Tool(
            name="add_task",
            description="Create a new task for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "due_date": {"type": "string"}
                },
                "required": ["user_id", "title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="Retrieve tasks with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["all", "active", "completed"]},
                    "limit": {"type": "integer"}
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Permanently remove a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update task properties",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "due_date": {"type": "string"}
                },
                "required": ["user_id", "task_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to appropriate handlers"""

    try:
        if name == "add_task":
            result = await handle_add_task(arguments)
        elif name == "list_tasks":
            result = await handle_list_tasks(arguments)
        elif name == "complete_task":
            result = await handle_complete_task(arguments)
        elif name == "delete_task":
            result = await handle_delete_task(arguments)
        elif name == "update_task":
            result = await handle_update_task(arguments)
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {name}",
                "code": "UNKNOWN_TOOL"
            }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "code": "INTERNAL_ERROR"
            }, indent=2)
        )]
```

---

### Tool Handler Implementation

```python
async def handle_add_task(args: dict) -> dict:
    """Create a new task"""
    user_id = args.get("user_id")
    title = args.get("title", "").strip()
    description = args.get("description")
    due_date = args.get("due_date")

    # Validation
    if not title:
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

    # Database operation
    try:
        with next(get_session()) as session:
            new_task = Task(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                completed=False
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            return {
                "success": True,
                "task": {
                    "id": str(new_task.id),
                    "user_id": new_task.user_id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "completed": new_task.completed,
                    "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
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

async def handle_list_tasks(args: dict) -> dict:
    """Retrieve tasks with filtering"""
    user_id = args.get("user_id")
    status = args.get("status", "all")
    limit = args.get("limit", 100)

    try:
        with next(get_session()) as session:
            query = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "active":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)

            # Apply limit
            query = query.limit(limit)

            tasks = session.exec(query).all()

            return {
                "success": True,
                "tasks": [
                    {
                        "id": str(task.id),
                        "user_id": task.user_id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                    for task in tasks
                ],
                "count": len(tasks),
                "filtered_by": {"status": status}
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR"
        }

async def handle_complete_task(args: dict) -> dict:
    """Mark task as completed"""
    user_id = args.get("user_id")
    task_id = args.get("task_id")

    try:
        with next(get_session()) as session:
            task = session.get(Task, task_id)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "code": "NOT_FOUND"
                }

            # Security: verify task belongs to user
            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Unauthorized: Task does not belong to user",
                    "code": "UNAUTHORIZED"
                }

            task.completed = True
            task.completed_at = datetime.utcnow()
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "user_id": task.user_id,
                    "title": task.title,
                    "completed": task.completed,
                    "completed_at": task.completed_at.isoformat(),
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

async def handle_delete_task(args: dict) -> dict:
    """Delete a task"""
    user_id = args.get("user_id")
    task_id = args.get("task_id")

    try:
        with next(get_session()) as session:
            task = session.get(Task, task_id)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "code": "NOT_FOUND"
                }

            # Security: verify task belongs to user
            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Unauthorized: Task does not belong to user",
                    "code": "UNAUTHORIZED"
                }

            session.delete(task)
            session.commit()

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

async def handle_update_task(args: dict) -> dict:
    """Update task properties"""
    user_id = args.get("user_id")
    task_id = args.get("task_id")
    title = args.get("title")
    description = args.get("description")
    due_date = args.get("due_date")

    try:
        with next(get_session()) as session:
            task = session.get(Task, task_id)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "code": "NOT_FOUND"
                }

            # Security: verify task belongs to user
            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Unauthorized: Task does not belong to user",
                    "code": "UNAUTHORIZED"
                }

            # Update fields if provided
            if title is not None:
                if not title.strip():
                    return {
                        "success": False,
                        "error": "Title cannot be empty",
                        "code": "VALIDATION_ERROR"
                    }
                task.title = title.strip()

            if description is not None:
                task.description = description

            if due_date is not None:
                task.due_date = due_date

            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
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
```

---

## Error Codes

| Code | Description | HTTP Equivalent |
|------|-------------|-----------------|
| VALIDATION_ERROR | Input validation failed | 400 |
| UNAUTHORIZED | User not authorized for resource | 403 |
| NOT_FOUND | Resource does not exist | 404 |
| DATABASE_ERROR | Database operation failed | 500 |
| INTERNAL_ERROR | Unexpected server error | 500 |
| UNKNOWN_TOOL | Tool name not recognized | 400 |

---

## Security Principles

1. **User Isolation**: Every tool requires `user_id` and validates ownership
2. **Input Validation**: All inputs are validated before database operations
3. **Error Handling**: Graceful error responses without exposing internals
4. **Stateless Design**: No session state; all context in request
5. **Database Transactions**: Proper commit/rollback on errors

---

## MCP Server Configuration

Add to `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "task-management": {
      "command": "python",
      "args": ["-m", "backend.mcp_server.task_tools"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

---

## Usage Examples

### From Claude Agent

```python
# Add a task
result = await use_mcp_tool("add_task", {
    "user_id": "user_123",
    "title": "Complete project documentation",
    "description": "Write README and API docs",
    "due_date": "2026-01-25T00:00:00Z"
})

# List active tasks
result = await use_mcp_tool("list_tasks", {
    "user_id": "user_123",
    "status": "active"
})

# Complete a task
result = await use_mcp_tool("complete_task", {
    "user_id": "user_123",
    "task_id": "task_456"
})

# Update a task
result = await use_mcp_tool("update_task", {
    "user_id": "user_123",
    "task_id": "task_456",
    "title": "Updated title",
    "due_date": "2026-01-30T00:00:00Z"
})

# Delete a task
result = await use_mcp_tool("delete_task", {
    "user_id": "user_123",
    "task_id": "task_456"
})
```

---

## Checklist

- [ ] MCP server file created in `backend/mcp_server/`
- [ ] All 5 tools registered in `list_tools()`
- [ ] Tool handlers implement user isolation
- [ ] Input validation for all required fields
- [ ] Error responses follow standard format
- [ ] Database transactions with rollback on error
- [ ] MCP server registered in `.claude/mcp.json`
- [ ] Environment variables configured
- [ ] Test cases written for all tools
- [ ] Documentation updated with tool usage

---

## Testing

Test each tool with various scenarios:

```bash
# Test add_task
echo '{"user_id": "test_user", "title": "Test task"}' | \
  mcp call task-management add_task

# Test list_tasks
echo '{"user_id": "test_user", "status": "active"}' | \
  mcp call task-management list_tasks

# Test complete_task
echo '{"user_id": "test_user", "task_id": "task_123"}' | \
  mcp call task-management complete_task

# Test update_task
echo '{"user_id": "test_user", "task_id": "task_123", "title": "Updated"}' | \
  mcp call task-management update_task

# Test delete_task
echo '{"user_id": "test_user", "task_id": "task_123"}' | \
  mcp call task-management delete_task
```

---

## Usage

**Todo Chat Agent** and other agents use these MCP tools when:

- User requests task creation via natural language
- Listing tasks with filters (today, this week, completed, etc.)
- Marking tasks as done
- Updating task details
- Deleting tasks

Always ensure `user_id` is properly extracted from the authenticated session context.
