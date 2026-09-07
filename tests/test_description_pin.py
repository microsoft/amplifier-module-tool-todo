"""Byte-for-byte pin on the todo tool description.

The description renders into the tool-schema block of every request in every
session, whether or not the tool is used, so its size is a per-request cost.
This pins the measured v1 lean text (526 chars, down from 667) so the
description cannot silently drift back to the longer form.

Source of the v1 text: amplifier-foundation main (PR #372, 4384805),
docs/lanes/zc6t-lean-head-ship/patches/tool-descriptions/todo.lean.txt
"""

from amplifier_module_tool_todo import TodoTool

DESCRIPTION_V1 = """Manage your todo list for tracking complex multi-step tasks: create a list when starting such work, update it after each completed step, stay accountable through long turns.

Each item has content (imperative, e.g. "Run tests"), activeForm (present continuous, e.g. "Running tests"), and status - one of "pending", "in_progress", "completed". Actions: create and update replace the whole list; list reads the current one.

Keep exactly ONE item "in_progress" at a time; mark an item "completed" immediately after finishing it."""

DESCRIPTION_V1_CHARS = 526


def test_description_is_byte_for_byte_v1():
    """The live description matches the pinned v1 text exactly."""
    assert TodoTool(coordinator=None).description == DESCRIPTION_V1  # type: ignore[arg-type]


def test_pinned_text_length_is_unchanged():
    """Guards the pin itself against an editing/escaping slip."""
    assert len(DESCRIPTION_V1) == DESCRIPTION_V1_CHARS
