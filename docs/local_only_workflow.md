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