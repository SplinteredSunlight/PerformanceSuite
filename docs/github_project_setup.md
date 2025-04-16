# GitHub Project Setup Guide

This guide explains how to set up and configure the GitHub Project for the Performance Suite repository.

## Important Update: Manual Setup Required

**GitHub has deprecated the classic Projects API in favor of the new Projects experience.**

The automated setup script no longer works with the new GitHub Projects. Please use the [Manual GitHub Project Setup Guide](github_project_setup_manual.md) instead.

## Project Structure

The GitHub Project is configured with:

### Custom Fields

- **Priority**: High, Medium, Low
- **Component**: Audio Processing, MIDI Generation, AI Bandmates, Visual Components, Control Interface, Infrastructure, Documentation
- **Effort**: Small, Medium, Large
- **Milestone**: Links to project milestones

### Views

- **Board**: Default kanban board view by status
- **Roadmap**: Timeline view grouped by milestone
- **Component View**: Board view grouped by component
- **Priority View**: Board view grouped by priority
- **All Items**: Table view with all items and fields

### Automation

The project includes automation for:

- Adding new issues and PRs to the project
- Setting initial status based on item type
- Updating status when items are closed or ready for review
- Synchronizing milestones with the configuration file

## Configuration Files

The project configuration is defined in the following files:

- `.github/projects/project-config.yml`: Project structure, statuses, and custom fields
- `.github/projects/project-views.yml`: Project views configuration
- `.github/projects/milestones.yml`: Project milestones

These files serve as a reference for the manual setup process.

## Next Steps

Please follow the [Manual GitHub Project Setup Guide](github_project_setup_manual.md) to set up your GitHub Project.