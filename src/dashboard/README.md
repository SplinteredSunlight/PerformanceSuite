# Performance Suite Dashboard

A web-based dashboard for visualizing and managing the Performance Suite project.

## Features

- **Project Overview**: View key project statistics and completion status
- **Task Board**: Kanban-style board showing tasks by status
- **Gantt Timeline**: Visual timeline of tasks with estimated durations
- **Component Progress**: Track progress of different project components
- **Task Details**: View detailed information about individual tasks
- **Dark Theme**: Modern dark theme with colorful component-based styling
- **Resizable Sections**: Drag handles to resize dashboard sections
- **Responsive Design**: Adapts to different screen sizes

## Getting Started

### Prerequisites

- Python 3.7+
- Web browser (Chrome, Firefox, Safari, or Edge recommended)

### Running the Dashboard

1. Make sure you're in the project root directory (`PerformanceSuite`)
2. Run the dashboard using:

```bash
python src/dashboard/run_dashboard.py
```

Or directly execute the script:

```bash
./src/dashboard/run_dashboard.py
```

3. The dashboard will automatically open in your default web browser at http://localhost:8000

### Restarting the Dashboard

If you need to restart the dashboard after making changes, use the provided script:

```bash
./scripts/restart_dashboard.sh
```

This will stop any running dashboard server and start a new one.

## Dashboard Sections

### Project Overview

Shows high-level project statistics including:
- Total number of tasks
- Completion rate
- Task distribution by status (chart)

### Task Board

Displays tasks organized by status:
- Not Started
- In Progress
- Blocked
- Completed

Tasks are color-coded by component and show priority levels. Click on any task card to view its details.

### Gantt Timeline

Shows a timeline view of tasks with:
- Task start and end dates (estimated)
- Color-coding by component
- Chronological arrangement

### Component Progress

Shows progress for each project component:
- Audio Analysis
- Agent System
- Rendering
- Infrastructure

Progress bars indicate completion percentage for each component.

### Task Details

When a task is selected, displays detailed information including:
- Title and ID
- Status and Priority
- Component and Effort
- Description
- Dependencies (if any)
- Notes (if any)

## Customization

### Resizing Sections

Each section of the dashboard can be resized by dragging the resize handle in the bottom-right corner of the section.

### Color Scheme

The dashboard uses a color scheme based on components:
- Blue: Audio Analysis and Agent System
- Purple: Rendering
- Orange: Infrastructure

## Technical Details

The dashboard consists of:

1. **Backend Server**: Python-based HTTP server that reads task data from the Memory Bank
2. **Frontend UI**: HTML, CSS, and JavaScript for the user interface
3. **API Endpoints**:
   - `/api/tasks`: Returns all tasks (can be filtered by status or component)
   - `/api/statistics`: Returns project statistics
   - `/api/components`: Returns tasks grouped by component

## Integration with Memory Bank

The dashboard reads task data directly from the `memory-bank/taskManagement.md` file, ensuring it always displays the most up-to-date information.

## Troubleshooting

- If the dashboard doesn't open automatically, manually navigate to http://localhost:8000 in your browser
- If you see a "Failed to load dashboard data" error, ensure the task manager MCP server is running
- If the server fails to start, check that port 8000 is not already in use
- If the dashboard appears too small or elements are not properly sized, try resizing your browser window or use the resize handles