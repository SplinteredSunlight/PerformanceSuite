#!/usr/bin/env python3
"""
Task Manager MCP Server

This script provides an MCP server for managing tasks in the Memory Bank taskManagement.md file.
It allows listing, creating, and updating tasks directly from Roo.
"""

import json
import sys
import re
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Constants
TASK_FILE_PATH = "memory-bank/taskManagement.md"
TASK_ID_PATTERN = r"MB-(\d+)"
TASK_SECTION_PATTERN = r"## Current Tasks\s+### ([^\n]+)"
TASK_ENTRY_PATTERN = r"\* ([^\n]+)\s+\* \*\*ID\*\*: (MB-\d+)\s+\* \*\*Status\*\*: ([^\n]+)\s+\* \*\*Priority\*\*: ([^\n]+)\s+\* \*\*Component\*\*: ([^\n]+)\s+\* \*\*Effort\*\*: ([^\n]+)\s+\* \*\*Description\*\*: ([^\n]+)(?:\s+\* \*\*Dependencies\*\*: ([^\n]+))?(?:\s+\* \*\*Notes\*\*: ([^\n]+))?"
TASK_BOARD_PATTERN = r"## Task Board View\s+### Not Started\s+([\s\S]+?)(?=### In Progress|$)\s*### In Progress\s+([\s\S]+?)(?=### Blocked|$)\s*### Blocked\s+([\s\S]+?)(?=### Completed|$)\s*### Completed\s+([\s\S]+?)(?=## Task Statistics|$)"
TASK_STATS_PATTERN = r"## Task Statistics\s+- Total Tasks: (\d+)\s+- Not Started: (\d+)\s+- In Progress: (\d+)\s+- Blocked: (\d+)\s+- Completed: (\d+)\s+- Completion Rate: ([^\n]+)\s+\s+Last Updated: ([^\n]+)"

# Task status options
VALID_STATUSES = ["Not Started", "In Progress", "Blocked", "Completed"]
VALID_COMPONENTS = ["Audio Analysis", "Agent System", "Rendering", "Infrastructure"]
VALID_PRIORITIES = ["High", "Medium", "Low"]
VALID_EFFORTS = ["Large", "Medium", "Small"]

class TaskManager:
    def __init__(self):
        self.task_file_path = TASK_FILE_PATH
        self.tasks = []
        self.next_id = 1
        self.load_tasks()

    def load_tasks(self) -> None:
        """Load tasks from the taskManagement.md file."""
        try:
            with open(self.task_file_path, 'r') as f:
                content = f.read()
                
            # Extract tasks using regex
            task_matches = re.finditer(TASK_ENTRY_PATTERN, content, re.MULTILINE)
            self.tasks = []
            
            for match in task_matches:
                title = match.group(1).strip()
                task_id = match.group(2).strip()
                status = match.group(3).strip()
                priority = match.group(4).strip()
                component = match.group(5).strip()
                effort = match.group(6).strip()
                description = match.group(7).strip()
                dependencies = match.group(8).strip() if match.group(8) else ""
                notes = match.group(9).strip() if match.group(9) else ""
                
                self.tasks.append({
                    "title": title,
                    "id": task_id,
                    "status": status,
                    "priority": priority,
                    "component": component,
                    "effort": effort,
                    "description": description,
                    "dependencies": dependencies,
                    "notes": notes
                })
            
            # Find the highest task ID to determine the next ID
            id_numbers = []
            for task in self.tasks:
                id_match = re.search(TASK_ID_PATTERN, task["id"])
                if id_match:
                    id_numbers.append(int(id_match.group(1)))
            
            self.next_id = max(id_numbers) + 1 if id_numbers else 1
            
        except Exception as e:
            send_error(f"Error loading tasks: {str(e)}")

    def save_tasks(self) -> None:
        """Save tasks to the taskManagement.md file."""
        try:
            with open(self.task_file_path, 'r') as f:
                content = f.read()
            
            # Update the task sections
            for component in VALID_COMPONENTS:
                component_tasks = [task for task in self.tasks if task["component"] == component and task["status"] != "Completed"]
                if not component_tasks:
                    continue
                
                component_section = f"### {component}\n\n"
                for task in component_tasks:
                    component_section += self._format_task(task)
                
                # Replace the component section in the content
                component_pattern = f"### {component}\\s+([\\s\\S]+?)(?=###|## Completed Tasks|$)"
                if re.search(component_pattern, content, re.MULTILINE):
                    content = re.sub(component_pattern, f"### {component}\n\n{component_section}", content, flags=re.MULTILINE)
            
            # Update the completed tasks section
            completed_tasks = [task for task in self.tasks if task["status"] == "Completed"]
            completed_section = "## Completed Tasks\n\n"
            for task in completed_tasks:
                completed_section += self._format_task(task)
            
            # Replace the completed tasks section
            completed_pattern = r"## Completed Tasks\s+([\s\S]+?)(?=## Task Board View|$)"
            if re.search(completed_pattern, content, re.MULTILINE):
                content = re.sub(completed_pattern, completed_section, content, flags=re.MULTILINE)
            
            # Update the task board view
            not_started = "\n".join([f"- {task['id']}: {task['title']}" for task in self.tasks if task["status"] == "Not Started"])
            in_progress = "\n".join([f"- {task['id']}: {task['title']}" for task in self.tasks if task["status"] == "In Progress"])
            blocked = "\n".join([f"- {task['id']}: {task['title']}" for task in self.tasks if task["status"] == "Blocked"])
            completed = "\n".join([f"- {task['id']}: {task['title']}" for task in self.tasks if task["status"] == "Completed"])
            
            board_view = f"""## Task Board View

### Not Started
{not_started}

### In Progress
{in_progress}

### Blocked
{blocked}

### Completed
{completed}
"""
            
            # Replace the task board view section
            board_pattern = r"## Task Board View\s+([\s\S]+?)(?=## Task Statistics|$)"
            if re.search(board_pattern, content, re.MULTILINE):
                content = re.sub(board_pattern, board_view, content, flags=re.MULTILINE)
            
            # Update the task statistics
            total_tasks = len(self.tasks)
            not_started_count = len([task for task in self.tasks if task["status"] == "Not Started"])
            in_progress_count = len([task for task in self.tasks if task["status"] == "In Progress"])
            blocked_count = len([task for task in self.tasks if task["status"] == "Blocked"])
            completed_count = len([task for task in self.tasks if task["status"] == "Completed"])
            completion_rate = f"{(completed_count / total_tasks * 100):.1f}%" if total_tasks > 0 else "0.0%"
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            stats_section = f"""## Task Statistics

- Total Tasks: {total_tasks}
- Not Started: {not_started_count}
- In Progress: {in_progress_count}
- Blocked: {blocked_count}
- Completed: {completed_count}
- Completion Rate: {completion_rate}

Last Updated: {now}
"""
            
            # Replace the task statistics section
            stats_pattern = r"## Task Statistics\s+([\s\S]+?)(?=$)"
            if re.search(stats_pattern, content, re.MULTILINE):
                content = re.sub(stats_pattern, stats_section, content, flags=re.MULTILINE)
            
            # Write the updated content back to the file
            with open(self.task_file_path, 'w') as f:
                f.write(content)
            
        except Exception as e:
            send_error(f"Error saving tasks: {str(e)}")

    def _format_task(self, task: Dict[str, str]) -> str:
        """Format a task for inclusion in the markdown file."""
        result = f"* {task['title']}\n"
        result += f"  * **ID**: {task['id']}\n"
        result += f"  * **Status**: {task['status']}\n"
        result += f"  * **Priority**: {task['priority']}\n"
        result += f"  * **Component**: {task['component']}\n"
        result += f"  * **Effort**: {task['effort']}\n"
        result += f"  * **Description**: {task['description']}\n"
        
        if task['dependencies']:
            result += f"  * **Dependencies**: {task['dependencies']}\n"
        
        if task['notes']:
            result += f"  * **Notes**: {task['notes']}\n"
        
        result += "\n"
        return result

    def list_tasks(self, status: Optional[str] = None, component: Optional[str] = None) -> List[Dict[str, str]]:
        """List tasks, optionally filtered by status or component."""
        filtered_tasks = self.tasks
        
        if status:
            if status not in VALID_STATUSES:
                send_error(f"Invalid status: {status}. Valid statuses are: {', '.join(VALID_STATUSES)}")
                return []
            filtered_tasks = [task for task in filtered_tasks if task["status"] == status]
        
        if component:
            if component not in VALID_COMPONENTS:
                send_error(f"Invalid component: {component}. Valid components are: {', '.join(VALID_COMPONENTS)}")
                return []
            filtered_tasks = [task for task in filtered_tasks if task["component"] == component]
        
        return filtered_tasks

    def create_task(self, title: str, description: str, component: str, priority: str, 
                   effort: str, dependencies: Optional[str] = None) -> Dict[str, str]:
        """Create a new task."""
        # Validate inputs
        if not title or not description:
            send_error("Title and description are required")
            return {}
        
        if component not in VALID_COMPONENTS:
            send_error(f"Invalid component: {component}. Valid components are: {', '.join(VALID_COMPONENTS)}")
            return {}
        
        if priority not in VALID_PRIORITIES:
            send_error(f"Invalid priority: {priority}. Valid priorities are: {', '.join(VALID_PRIORITIES)}")
            return {}
        
        if effort not in VALID_EFFORTS:
            send_error(f"Invalid effort: {effort}. Valid efforts are: {', '.join(VALID_EFFORTS)}")
            return {}
        
        # Create the new task
        task_id = f"MB-{self.next_id:03d}"
        self.next_id += 1
        
        new_task = {
            "title": title,
            "id": task_id,
            "status": "Not Started",
            "priority": priority,
            "component": component,
            "effort": effort,
            "description": description,
            "dependencies": dependencies or "",
            "notes": ""
        }
        
        self.tasks.append(new_task)
        self.save_tasks()
        
        return new_task

    def update_task(self, task_id: str, status: Optional[str] = None, notes: Optional[str] = None) -> Dict[str, str]:
        """Update an existing task."""
        # Find the task
        task_to_update = None
        for task in self.tasks:
            if task["id"] == task_id:
                task_to_update = task
                break
        
        if not task_to_update:
            send_error(f"Task with ID {task_id} not found")
            return {}
        
        # Update the task
        if status:
            if status not in VALID_STATUSES:
                send_error(f"Invalid status: {status}. Valid statuses are: {', '.join(VALID_STATUSES)}")
                return {}
            task_to_update["status"] = status
        
        if notes:
            if task_to_update["notes"]:
                task_to_update["notes"] += f" | {notes}"
            else:
                task_to_update["notes"] = notes
        
        self.save_tasks()
        
        return task_to_update

    def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about tasks."""
        total_tasks = len(self.tasks)
        not_started = len([task for task in self.tasks if task["status"] == "Not Started"])
        in_progress = len([task for task in self.tasks if task["status"] == "In Progress"])
        blocked = len([task for task in self.tasks if task["status"] == "Blocked"])
        completed = len([task for task in self.tasks if task["status"] == "Completed"])
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "not_started": not_started,
            "in_progress": in_progress,
            "blocked": blocked,
            "completed": completed,
            "completion_rate": f"{completion_rate:.1f}%"
        }

def send_response(data: Any) -> None:
    """Send a response to the MCP client."""
    response = {
        "status": "success",
        "data": data
    }
    print(json.dumps(response))
    sys.stdout.flush()

def send_error(message: str) -> None:
    """Send an error response to the MCP client."""
    response = {
        "status": "error",
        "message": message
    }
    print(json.dumps(response))
    sys.stdout.flush()

def handle_request(request: Dict[str, Any]) -> None:
    """Handle an incoming MCP request."""
    try:
        tool_name = request.get("tool")
        params = request.get("params", {})
        
        task_manager = TaskManager()
        
        if tool_name == "list_tasks":
            status = params.get("status")
            component = params.get("component")
            tasks = task_manager.list_tasks(status, component)
            send_response(tasks)
        
        elif tool_name == "create_task":
            title = params.get("title")
            description = params.get("description")
            component = params.get("component")
            priority = params.get("priority")
            effort = params.get("effort")
            dependencies = params.get("dependencies")
            
            if not all([title, description, component, priority, effort]):
                send_error("Missing required parameters")
                return
            
            task = task_manager.create_task(title, description, component, priority, effort, dependencies)
            send_response(task)
        
        elif tool_name == "update_task":
            task_id = params.get("task_id")
            status = params.get("status")
            notes = params.get("notes")
            
            if not task_id:
                send_error("Missing required parameter: task_id")
                return
            
            task = task_manager.update_task(task_id, status, notes)
            send_response(task)
        
        elif tool_name == "get_task_statistics":
            stats = task_manager.get_task_statistics()
            send_response(stats)
        
        else:
            send_error(f"Unknown tool: {tool_name}")
    
    except Exception as e:
        send_error(f"Error handling request: {str(e)}")

def main() -> None:
    """Main entry point for the MCP server."""
    # Send a startup message
    print(json.dumps({"status": "ready"}))
    sys.stdout.flush()
    
    # Process incoming requests
    for line in sys.stdin:
        try:
            request = json.loads(line)
            handle_request(request)
        except json.JSONDecodeError:
            send_error("Invalid JSON request")
        except Exception as e:
            send_error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()