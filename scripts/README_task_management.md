# Task Management Scripts

This directory contains scripts for managing tasks in the Performance Suite project.

## Scripts

### 1. task_manager_mcp.py

An MCP server for managing tasks in the Memory Bank taskManagement.md file. It allows listing, creating, and updating tasks directly from Roo.

**Usage:**
```bash
# Start the MCP server
python scripts/task_manager_mcp.py

# Use the MCP server (in another terminal)
echo '{"tool": "list_tasks", "params": {}}' | python scripts/task_manager_mcp.py
echo '{"tool": "get_task_statistics", "params": {}}' | python scripts/task_manager_mcp.py
```

### 2. fix_task_management.py

A script to fix the taskManagement.md file by removing duplicate tasks and ensuring proper formatting.

**Usage:**
```bash
python scripts/fix_task_management.py
```

### 3. update_task_status.py

A script to update a task's status using the task manager MCP server and then run the fix_task_management.py script to ensure the file remains clean.

**Usage:**
```bash
# Update a task status
python scripts/update_task_status.py <task_id> <status> [--notes <notes>]

# Examples
python scripts/update_task_status.py MB-008 "In Progress" --notes "Starting OSC implementation"
python scripts/update_task_status.py MB-007 "Completed" --notes "Network configuration complete"
```

Valid status values:
- "Not Started"
- "In Progress"
- "Blocked"
- "Completed"

## Task Management Workflow

1. **View Tasks**: Use `task_manager_mcp.py` to list tasks and get statistics.
2. **Update Tasks**: Use `update_task_status.py` to update task statuses.
3. **Fix Issues**: If you encounter any issues with duplicate tasks or formatting, run `fix_task_management.py`.

## Task Format

Each task follows this format in the taskManagement.md file:

```markdown
* Task Title
  * **ID**: MB-001
  * **Status**: In Progress | Completed | Blocked | Not Started
  * **Priority**: High | Medium | Low
  * **Component**: Audio Analysis | Agent System | Rendering | Infrastructure
  * **Effort**: Large | Medium | Small
  * **Description**: Detailed description of the task
  * **Dependencies**: MB-002, MB-003
  * **Notes**: Additional notes or context
```

## Task Board View

The taskManagement.md file includes a Task Board View section that organizes tasks by status:
- Not Started
- In Progress
- Blocked
- Completed

## Task Statistics

The taskManagement.md file includes a Task Statistics section that shows:
- Total Tasks
- Not Started
- In Progress
- Blocked
- Completed
- Completion Rate