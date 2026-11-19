"""Registration and state sharing through Core's coordinator API."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from amplifier_module_tool_todo import TodoTool, mount


@pytest.mark.asyncio
async def test_mount_registers_the_tool_and_shares_todo_state():
    coordinator = SimpleNamespace(mount=AsyncMock())
    assert await mount(coordinator) is None

    tool = coordinator.mount.await_args.args[1]
    assert isinstance(tool, TodoTool)
    coordinator.mount.assert_awaited_once_with("tools", tool, name="todo")
    assert coordinator.todo_state == []

    todos = [{"content": "Verify registration", "activeForm": "Verifying", "status": "pending"}]
    result = await tool.execute({"action": "create", "todos": todos})
    assert result.success
    assert coordinator.todo_state == todos
    assert (await tool.execute({"action": "list"})).output["todos"] == todos
