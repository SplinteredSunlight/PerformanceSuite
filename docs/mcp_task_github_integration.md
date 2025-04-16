# MCP Task Management and GitHub Desktop Integration

This document describes the MCP servers set up for task management and GitHub Desktop integration in the Performance Suite project.

## Overview

Two MCP servers have been configured:

1. **Task Manager MCP Server**: Provides tools for managing tasks in the Memory Bank taskManagement.md file.
2. **GitHub Desktop MCP Server**: Provides tools for Git operations through GitHub Desktop.

## Task Manager MCP Server

The Task Manager MCP server allows you to manage tasks directly from Roo without having to manually edit the taskManagement.md file.

### Available Tools

- **list_tasks**: Lists all tasks from taskManagement.md, optionally filtered by status or component.
- **create_task**: Creates a new task in taskManagement.md.
- **update_task**: Updates an existing task's status or details.
- **get_task_statistics**: Gets statistics about tasks (total, completed, etc.).

### Usage Examples

#### Listing Tasks

```
list_tasks:
  status: "In Progress"
  component: "Audio Analysis"
```

#### Creating a Task

```
create_task:
  title: "Implement feature X"
  description: "Create a new feature that does X"
  component: "Audio Analysis"
  priority: "High"
  effort: "Medium"
  dependencies: "MB-001, MB-002"
```

#### Updating a Task

```
update_task:
  task_id: "MB-001"
  status: "In Progress"
  notes: "Started implementation on 2025-04-16"
```

#### Getting Task Statistics

```
get_task_statistics:
```

## GitHub Desktop MCP Server

The GitHub Desktop MCP server allows you to perform Git operations directly from Roo.

### Available Tools

- **git_status**: Shows the current Git status.
- **git_commit**: Commits changes with a message.
- **git_push**: Pushes commits to remote repository.
- **git_pull**: Pulls changes from remote repository.
- **git_branch**: Creates or switches branches.

### Usage Examples

#### Checking Git Status

```
git_status:
```

#### Committing Changes

```
git_commit:
  message: "Add new feature X"
  files: "all"
```

Or for specific files:

```
git_commit:
  message: "Update README"
  files: "README.md, docs/usage.md"
```

#### Pushing Changes

```
git_push:
  remote: "origin"
  branch: "main"
```

#### Pulling Changes

```
git_pull:
  remote: "origin"
  branch: "main"
```

#### Creating or Switching Branches

Create a new branch:

```
git_branch:
  name: "feature/new-feature"
  create: true
```

Switch to an existing branch:

```
git_branch:
  name: "main"
```

## Implementation Details

The MCP servers are implemented as Python scripts:

- **Task Manager**: `scripts/task_manager_mcp.py`
- **GitHub Desktop**: `scripts/github_desktop_mcp.py`

These scripts are configured in both the project-specific MCP configuration (`.roo/mcp.json`) and the global MCP settings.

## Troubleshooting

If you encounter issues with the MCP servers:

1. Ensure the Python scripts have execute permissions:
   ```bash
   chmod +x scripts/task_manager_mcp.py scripts/github_desktop_mcp.py
   ```

2. Check that the paths in the MCP configuration files are correct:
   - Project-specific: `.roo/mcp.json`
   - Global: `~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`

3. Verify that the required Python modules are installed.

4. Check the terminal output for any error messages from the MCP servers.