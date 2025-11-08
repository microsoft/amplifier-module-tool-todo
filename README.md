# amplifier-module-tool-todo

AI self-accountability tool for managing todo lists during complex multi-step tasks.

## Purpose

Provides cognitive scaffolding for AI agents to maintain focus through long, complex turns where context fills up and plans might get buried. Works with `amplifier-module-hooks-todo-reminder` for automatic context injection.

**This is NOT for showing task progress to users** - it's for AI self-management to prevent wandering or forgetting steps.

## The Problem It Solves

**Typical failure pattern:**
1. AI gets complex task, creates plan [Step 1, Step 2, Step 3, Step 4, Step 5]
2. Completes steps 1-2, context fills with results (30k+ tokens)
3. At step 3: AI forgets original plan buried in context
4. Risk: AI wanders, declares done prematurely, abandons steps 4-5

**Solution:**
- AI creates todo list using this tool
- Hook injects reminders before each turn
- AI sees: "✓1 done, ✓2 done, ☐3 pending, ☐4 pending, ☐5 pending"
- AI stays on track, completes all commitments

## Installation

```bash
uv add amplifier-module-tool-todo
```

## Configuration

Add to your profile:

```yaml
tools:
  - module: tool-todo
    source: git+https://github.com/microsoft/amplifier-module-tool-todo@main
    config: {}  # No configuration needed
```

## AI Usage Patterns

### Pattern 1: Create Plan at Task Start

```
User: "Implement a new authentication system"

AI thought process:
1. This is complex, I should create a plan
2. Use todo tool to create list
3. Work through systematically
```

**AI action:**
```json
{
  "action": "create",
  "todos": [
    {"content": "Research auth requirements", "activeForm": "Researching auth requirements", "status": "pending"},
    {"content": "Design auth flow", "activeForm": "Designing auth flow", "status": "pending"},
    {"content": "Implement auth module", "activeForm": "Implementing auth module", "status": "pending"},
    {"content": "Write auth tests", "activeForm": "Writing auth tests", "status": "pending"},
    {"content": "Document auth usage", "activeForm": "Documenting auth usage", "status": "pending"}
  ]
}
```

### Pattern 2: Update After Each Step

```
[AI completes research]

AI action:
```json
{
  "action": "update",
  "todos": [
    {"content": "Research auth requirements", "activeForm": "Researching auth requirements", "status": "completed"},
    {"content": "Design auth flow", "activeForm": "Designing auth flow", "status": "in_progress"},
    {"content": "Implement auth module", "activeForm": "Implementing auth module", "status": "pending"},
    {"content": "Write auth tests", "activeForm": "Writing auth tests", "status": "pending"},
    {"content": "Document auth usage", "activeForm": "Documenting auth usage", "status": "pending"}
  ]
}
```

**Result:** AI updates plan, hook will inject reminder in next turn

### Pattern 3: Check Status Anytime

```json
{
  "action": "list"
}
```

**Returns:** Current todo list with all items and their statuses

## Todo Item Schema

Each todo must have:

```typescript
{
  content: string      // Imperative: "Run tests", "Build project"
  activeForm: string   // Present continuous: "Running tests", "Building project"
  status: "pending" | "in_progress" | "completed"
}
```

**Rules:**
- Keep ONE item as "in_progress" at a time (guidance, not enforced)
- Mark "completed" immediately after finishing each step
- Use imperative for content, present continuous for activeForm

## Tool Interface

### Actions

**create**: Replace entire list with new todos
```json
{
  "action": "create",
  "todos": [...]
}
```

**update**: Replace entire list (AI manages transitions)
```json
{
  "action": "update",
  "todos": [...]  // Full list with updated statuses
}
```

**list**: Return current todos
```json
{
  "action": "list"
}
```

### Responses

**create/update:**
```json
{
  "status": "created|updated",
  "count": 5,
  "pending": 3,
  "in_progress": 1,
  "completed": 1,
  "todos": [...]  // Full list returned
}
```

**list:**
```json
{
  "status": "listed",
  "count": 5,
  "todos": [...]
}
```

## How It Works

1. **AI calls tool** to create/update todo list
2. **Tool stores** in `coordinator.todo_state` (session-scoped)
3. **Hook watches** for `prompt:submit` events
4. **Hook injects** formatted reminder into AI's context
5. **AI sees** reminder before each response
6. **AI stays focused** on completing all steps

## Philosophy Alignment

- ✅ **Mechanism not policy**: Tool provides storage, hook provides injection, AI decides usage
- ✅ **Ruthless simplicity**: In-memory, basic CRUD, no complex validation
- ✅ **Session-scoped**: State lives only during conversation
- ✅ **AI self-management**: No enforcement, just scaffolding
- ✅ **Non-interference**: Failures don't crash session

## Implementation Details

- **Storage:** `coordinator.todo_state = []` (dynamic attribute)
- **Scope:** Session-only (cleared when session ends)
- **Validation:** Schema validation only (required fields, valid statuses)
- **Events:** Emits TOOL_PRE and TOOL_POST for observability

## See Also

- [amplifier-module-hooks-todo-reminder](../amplifier-module-hooks-todo-reminder/README.md) - Hook that injects reminders
- [Hook Context Injection Spec](../amplifier-core/docs/specs/HOOKS_CONTEXT_INJECTION.md) - How injection works
- [bd-35](../.beads/amplifier-dev.jsonl) - Original investigation and design

## Testing

Run integration tests:

```bash
# Unit test: Tool operations
python test_todo_integration.py

# Multi-turn test: Accountability loop
python test_todo_multi_turn.py
```

Both tests verify:
- Tool CRUD operations work correctly
- Hook injects reminders on prompt:submit
- Context receives injected messages
- Format matches TodoWrite display (✓/☐ symbols)
