# Project Cleanup Plan

This document outlines the steps to clean up the Performance Suite project, removing GitHub.com integration while keeping GitHub Desktop functionality and the task manager.

## 1. Create Reference Backup

First, create a reference backup of the GitHub workflows:

```bash
# Create reference directory
mkdir -p .github_reference/workflows
mkdir -p .github_reference/projects

# Copy workflows to reference directory
cp -r .github/workflows/* .github_reference/workflows/
cp -r .github/projects/* .github_reference/projects/
```

## 2. Scripts to Remove

Remove the following GitHub integration scripts:

```bash
# Remove GitHub integration scripts
rm scripts/sync_memory_bank_to_github.py
rm scripts/sync_github_issues_to_memory_bank.py
rm scripts/setup_github_project.py
rm scripts/setup_github_project_v2.py
rm scripts/setup_github_project_graphql.py
rm scripts/setup_github_project_graphql_v2.py
rm scripts/setup_github_project_graphql_v3.py
rm scripts/run_memory_bank_to_github_sync.sh
rm scripts/run_memory_bank_sync.sh
rm scripts/update_task_status.py
```

## 3. Rename GitHub Workflows Directory

Move the workflows directory to the reference location:

```bash
# Remove the workflows directory after backing it up
rm -rf .github/workflows
rm -rf .github/projects
```

## 4. Documentation to Remove

Remove GitHub-specific documentation:

```bash
# Remove GitHub integration documentation
rm docs/github_project_setup.md
rm docs/github_project_setup_manual.md
rm docs/github_project_setup_success.md
rm docs/github_to_memory_bank_transition.md
rm docs/mcp_task_github_integration.md
```

## 5. Stop GitHub Integration Processes

Ensure any running GitHub integration processes are stopped:

```bash
# Find and stop any running GitHub integration processes
ps aux | grep sync_memory_bank_to_github.py
ps aux | grep sync_github_issues_to_memory_bank.py
# Use kill command if needed to stop these processes
```

## 6. Update Documentation

Create a new document explaining the local-only workflow:

```bash
# Create a new document explaining the changes
touch docs/local_only_workflow.md
```

Content for `docs/local_only_workflow.md`:

```markdown
# Local-Only Workflow

This document explains the local-only workflow for the Performance Suite project after removing GitHub.com integration.

## Overview

The Performance Suite project now uses a completely local workflow with:

1. **GitHub Desktop**: For Git operations (commits, branches, etc.)
2. **Task Manager MCP Server**: For task management
3. **Memory Bank**: For project documentation and task storage
4. **Dashboard**: For visualizing tasks and project status

## Components

- **GitHub Desktop MCP** (`scripts/github_desktop_mcp.py`): Provides Git operations through the MCP interface
- **Task Manager MCP** (`scripts/task_manager_mcp.py`): Manages tasks in the Memory Bank
- **Dashboard** (`src/dashboard/`): Visualizes tasks and project status

## Workflow

1. Use the Task Manager MCP to create and manage tasks
2. Use GitHub Desktop MCP for Git operations
3. Use the Dashboard to visualize project status

## CI/CD

The CI/CD pipeline will be set up separately based on the reference workflows in `.github_reference/`.
```

## 7. Verify Everything Still Works

After making these changes, verify that the essential components still work:

1. Start the task manager MCP: `python3 scripts/task_manager_mcp.py`
2. Start the GitHub Desktop MCP: `python3 scripts/github_desktop_mcp.py`
3. Start the dashboard: `python3 src/dashboard/run_dashboard.py`
4. Verify that tasks are displayed correctly in the dashboard
5. Verify that Git operations work through the GitHub Desktop MCP

## 8. Update Memory Bank

Update the Memory Bank to reflect these changes:

1. Update `memory-bank/activeContext.md` to mention the removal of GitHub.com integration
2. Update `memory-bank/productContext.md` if needed to reflect the local-only workflow