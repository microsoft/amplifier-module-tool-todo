"""AI self-accountability tool for managing todo lists.

This tool enables AI to create and manage its own todo list for tracking
multi-step tasks. Works with hooks-todo-reminder for automatic context injection.
"""

import logging
from typing import Any

from amplifier_core import ModuleCoordinator
from amplifier_core import ToolResult

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None):
    """Mount the todo tool.

    Initializes coordinator.todo_state for session-scoped storage.
    """
    # Initialize state storage (dynamic attribute)
    coordinator.todo_state = []  # type: ignore[attr-defined]

    tool = TodoTool(coordinator)
    # Register tool in mount_points
    coordinator.mount_points["tools"][tool.name] = tool
    logger.info("Mounted tool-todo")
    return


class TodoTool:
    """AI-managed todo list for self-accountability through complex turns."""

    def __init__(self, coordinator: ModuleCoordinator):
        self.coordinator = coordinator

    @property
    def name(self) -> str:
        return "todo"

    @property
    def description(self) -> str:
        return """Manage your todo list for tracking multi-step tasks.

Use this tool to:
- Create a todo list when starting complex multi-step work
- Update the list as you complete each step
- Stay accountable and focused through long turns

Todo items have:
- content: Imperative description (e.g., "Run tests", "Build project")
- activeForm: Present continuous (e.g., "Running tests", "Building project")
- status: "pending" | "in_progress" | "completed"

Recommended pattern:
1. Create list when you start multi-step work
2. Update after completing each step
3. Keep exactly ONE item as "in_progress" at a time
4. Mark items "completed" immediately after finishing"""

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "update", "list"],
                    "description": "Action to perform: create (replace all), update (replace all), list (read current)",
                },
                "todos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Imperative description: 'Run tests', 'Build project'",
                            },
                            "activeForm": {
                                "type": "string",
                                "description": "Present continuous: 'Running tests', 'Building project'",
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                                "description": "Current status of this todo item",
                            },
                        },
                        "required": ["content", "status", "activeForm"],
                    },
                    "description": "List of todos (required for create/update, ignored for list)",
                },
            },
            "required": ["action"],
        }

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        """Execute todo operation.

        Actions:
        - create: Replace entire list with new todos
        - update: Replace entire list (AI manages state transitions)
        - list: Return current todos
        """
        action = input.get("action")

        if action == "create":
            todos = input.get("todos", [])

            # Validate schema
            for i, todo in enumerate(todos):
                if not all(k in todo for k in ["content", "status", "activeForm"]):
                    return ToolResult(
                        success=False,
                        error={"message": f"Todo {i} missing required fields (content, status, activeForm)"},
                    )
                if todo["status"] not in ["pending", "in_progress", "completed"]:
                    return ToolResult(
                        success=False, error={"message": f"Todo {i} has invalid status: {todo['status']}"}
                    )

            # Replace list
            self.coordinator.todo_state = todos  # type: ignore[attr-defined]

            return ToolResult(success=True, output={"status": "created", "count": len(todos), "todos": todos})

        if action == "update":
            todos = input.get("todos", [])

            # Validate schema
            for i, todo in enumerate(todos):
                if not all(k in todo for k in ["content", "status", "activeForm"]):
                    return ToolResult(
                        success=False,
                        error={"message": f"Todo {i} missing required fields (content, status, activeForm)"},
                    )
                if todo["status"] not in ["pending", "in_progress", "completed"]:
                    return ToolResult(
                        success=False, error={"message": f"Todo {i} has invalid status: {todo['status']}"}
                    )

            # Replace list (AI manages transitions)
            self.coordinator.todo_state = todos  # type: ignore[attr-defined]

            # Count states for feedback
            pending = sum(1 for t in todos if t["status"] == "pending")
            in_progress = sum(1 for t in todos if t["status"] == "in_progress")
            completed = sum(1 for t in todos if t["status"] == "completed")

            return ToolResult(
                success=True,
                output={
                    "status": "updated",
                    "count": len(todos),
                    "pending": pending,
                    "in_progress": in_progress,
                    "completed": completed,
                },
            )

        if action == "list":
            # Return current state
            todo_state = getattr(self.coordinator, "todo_state", [])
            return ToolResult(success=True, output={"status": "listed", "count": len(todo_state), "todos": todo_state})

        return ToolResult(
            success=False,
            error={"message": f"Unknown action: {action}. Valid actions: create, update, list"},
        )
