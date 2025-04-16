# GitHub Projects Configuration

This directory contains configuration files for the Performance Suite GitHub Project.

## Files

- `project-config.yml`: Defines the project structure, statuses, and custom fields
- `project-views.yml`: Defines different views for the project board
- `../workflows/project-automation.yml`: Workflow file for automating project management tasks

## Setup Instructions

1. Create a new GitHub Project in your organization or repository
2. Set the project URL in the workflow file (`project-automation.yml`)
3. Create a `PROJECT_TOKEN` secret in your repository settings with appropriate permissions
4. Configure the project according to the configuration files

## Custom Fields

The project uses the following custom fields:

- **Priority**: Indicates the importance of an item
  - 🔥 High
  - 🔶 Medium
  - 🔷 Low

- **Component**: Categorizes items by system component
  - Audio Processing
  - MIDI Generation
  - AI Bandmates
  - Visual Components
  - Control Interface
  - Infrastructure
  - Documentation

- **Effort**: Estimates the amount of work required
  - Small
  - Medium
  - Large

- **Milestone**: Links items to project milestones

## Views

The project includes the following views:

- **Board**: Default kanban board view by status
- **Roadmap**: Timeline view grouped by milestone
- **Component View**: Board view grouped by component
- **Priority View**: Board view grouped by priority
- **All Items**: Table view with all items and fields

## Automation

The workflow automates the following tasks:

- Adding new issues and PRs to the project
- Setting initial status based on item type
- Updating status when items are closed or ready for review