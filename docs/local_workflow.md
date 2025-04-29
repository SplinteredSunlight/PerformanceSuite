# Local Development Workflow

This document describes the local development workflow for the Performance Suite project, using GitHub Desktop for Git operations and the task manager MCP server for project management.

## Overview

The Performance Suite project uses a completely local workflow with:

1. **GitHub Desktop**: For Git operations (commits, branches, etc.)
2. **Task Manager MCP Server**: For task management (replacing GitHub Projects)
3. **Memory Bank**: For project documentation and task storage
4. **Local Frontend** (planned): For visualizing tasks with roadmap, kanban, and other views

## GitHub Desktop Setup

To set up GitHub Desktop for this project:

1. Open GitHub Desktop
2. Select "Add an Existing Repository from your Hard Drive"
3. Navigate to the Performance Suite project directory
4. GitHub Desktop will recognize the Git repository and allow you to manage it locally

## Task Management

Since GitHub Desktop doesn't include project management features like GitHub Projects, we use our custom Task Manager MCP server to manage tasks locally:

1. Tasks are stored in `memory-bank/taskManagement.md`
2. The Task Manager MCP server (`scripts/task_manager_mcp.py`) provides tools for managing these tasks
3. Tasks can be created, updated, and tracked entirely locally

### Available Task Management Tools

- **list_tasks**: Lists all tasks, optionally filtered by status or component
- **create_task**: Creates a new task with specified details
- **update_task**: Updates an existing task's status or details
- **get_task_statistics**: Gets statistics about tasks (total, completed, etc.)

## Local Frontend (Planned)

A local frontend will be developed to visualize the tasks in various formats:

- Roadmap view
- Kanban board
- Task list
- Statistics dashboard

This frontend will read from and write to the Memory Bank files, providing a visual interface for the task management system.

## Workflow Example

1. **Task Creation**:
   - Use the task_manager_mcp server to create a new task
   - The task is added to `memory-bank/taskManagement.md`

2. **Implementation**:
   - Work on the task in your local environment
   - Make changes to the codebase

3. **Version Control**:
   - Use GitHub Desktop to commit your changes
   - Create branches for features if needed
   - Manage your repository entirely locally

4. **Task Completion**:
   - Use the task_manager_mcp server to update the task status to "Completed"
   - The task is moved to the completed section in `memory-bank/taskManagement.md`

## Benefits of This Approach

- **Complete Local Control**: All project management and version control happens locally
- **No External Dependencies**: No need for GitHub.com or other external services
- **Integrated Workflow**: Task management and version control are integrated through the MCP servers
- **Customizable**: The system can be extended with additional local tools as needed

## Next Steps

- Develop the local frontend for task visualization
- Enhance the task management system with additional features
- Create reporting and analytics tools for project progress