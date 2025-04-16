# GitHub Configuration for Performance Suite

This directory contains configuration files for GitHub features used in the Performance Suite project.

## Directory Structure

- **ISSUE_TEMPLATE/**: Templates for creating different types of issues
  - `bug_report.md`: Template for reporting bugs
  - `feature_request.md`: Template for requesting new features
  - `research_spike.md`: Template for research tasks
  - `technical_debt.md`: Template for tracking technical debt
  - `performance_optimization.md`: Template for performance optimization tasks

- **projects/**: Configuration for GitHub Projects
  - `project-config.yml`: Defines project structure, statuses, and custom fields
  - `project-views.yml`: Defines different views for the project board
  - `milestones.yml`: Defines project milestones
  - `README.md`: Documentation for GitHub Projects configuration

- **workflows/**: GitHub Actions workflow files
  - `ci.yml`: Continuous Integration workflow
  - `project-automation.yml`: Workflow for automating project management tasks
  - `milestone-sync.yml`: Workflow for synchronizing milestones

- **pull_request_template.md**: Template for creating pull requests

## GitHub Projects

The project uses GitHub Projects for task management and tracking. The configuration includes:

### Custom Fields

- **Priority**: Indicates the importance of an item (High, Medium, Low)
- **Component**: Categorizes items by system component
- **Effort**: Estimates the amount of work required
- **Milestone**: Links items to project milestones

### Views

- **Board**: Default kanban board view by status
- **Roadmap**: Timeline view grouped by milestone
- **Component View**: Board view grouped by component
- **Priority View**: Board view grouped by priority
- **All Items**: Table view with all items and fields

### Automation

The project automation workflow handles:

- Adding new issues and PRs to the project
- Setting initial status based on item type
- Updating status when items are closed or ready for review

## Issue Templates

The project includes specialized issue templates for different types of tasks:

- **Bug Report**: For reporting bugs and issues
- **Feature Request**: For suggesting new features
- **Research Spike**: For research tasks and investigations
- **Technical Debt**: For tracking technical debt items
- **Performance Optimization**: For performance-related tasks

## Continuous Integration

The CI workflow currently includes:

- Markdown validation
- Link checking

Additional jobs will be added as the project develops.

## Setup Instructions

1. Create a GitHub repository for the project
2. Push this configuration to the repository
3. Create a GitHub Project in the repository or organization
4. Set up the required secrets for the workflows
5. Configure the project according to the configuration files