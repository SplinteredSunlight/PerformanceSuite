#!/usr/bin/env python3
"""
Fix Task Management File

This script fixes the taskManagement.md file by removing duplicate tasks
and ensuring proper formatting.
"""

import re
import os
from collections import OrderedDict

# Constants
TASK_FILE_PATH = "memory-bank/taskManagement.md"
TASK_ID_PATTERN = r"MB-(\d+)"
TASK_ENTRY_PATTERN = r"\* ([^\n]+)\s+\* \*\*ID\*\*: (MB-\d+)\s+\* \*\*Status\*\*: ([^\n]+)\s+\* \*\*Priority\*\*: ([^\n]+)\s+\* \*\*Component\*\*: ([^\n]+)\s+\* \*\*Effort\*\*: ([^\n]+)\s+\* \*\*Description\*\*: ([^\n]+)(?:\s+\* \*\*Dependencies\*\*: ([^\n]+))?(?:\s+\* \*\*Notes\*\*: ([^\n]+))?"
PHASE_PATTERN = r"### Phase \d+: ([^\n]+)"

def main():
    """Main function to fix the taskManagement.md file."""
    print("Fixing taskManagement.md file...")
    
    # Read the original file
    with open(TASK_FILE_PATH, 'r') as f:
        content = f.read()
    
    # Extract the header (everything before "## Current Tasks")
    header_match = re.search(r"([\s\S]+?)## Current Tasks", content)
    if not header_match:
        print("Error: Could not find header section")
        return
    
    header = header_match.group(1)
    
    # Extract all tasks
    task_matches = re.finditer(TASK_ENTRY_PATTERN, content, re.MULTILINE)
    tasks_by_id = OrderedDict()
    
    for match in task_matches:
        title = match.group(1).strip()
        task_id = match.group(2).strip()
        status = match.group(3).strip()
        priority = match.group(4).strip()
        component = match.group(5).strip()
        effort = match.group(6).strip()
        description = match.group(7).strip()
        dependencies = match.group(8).strip() if match.group(8) else "None"
        notes = match.group(9).strip() if match.group(9) else ""
        
        # Determine the phase by finding the nearest phase header before this task
        task_pos = content.find(title)
        phase = "Unknown"
        if task_pos > 0:
            content_before = content[:task_pos]
            phase_headers = list(re.finditer(r"### Phase \d+: ([^\n]+)", content_before, re.MULTILINE))
            if phase_headers:
                phase = phase_headers[-1].group(1)
        
        # Only keep the first occurrence of each task ID
        if task_id not in tasks_by_id:
            tasks_by_id[task_id] = {
                "title": title,
                "id": task_id,
                "status": status,
                "priority": priority,
                "component": component,
                "effort": effort,
                "description": description,
                "dependencies": dependencies,
                "notes": notes,
                "phase": phase
            }
    
    # Extract all phases
    phase_matches = re.finditer(PHASE_PATTERN, content, re.MULTILINE)
    phases = [match.group(1) for match in phase_matches]
    
    # Create new content
    new_content = header + "## Current Tasks\n\n"
    
    # Group tasks by phase
    for phase in phases:
        new_content += f"### Phase {phases.index(phase)}: {phase}\n\n"
        
        # Get tasks for this phase
        phase_tasks = [task for task in tasks_by_id.values() if task["phase"] == phase]
        
        # Sort tasks by ID
        phase_tasks.sort(key=lambda x: int(re.search(r"MB-(\d+)", x["id"]).group(1)))
        
        # Add tasks to content
        for task in phase_tasks:
            new_content += f"* {task['title']}\n"
            new_content += f"  * **ID**: {task['id']}\n"
            new_content += f"  * **Status**: {task['status']}\n"
            new_content += f"  * **Priority**: {task['priority']}\n"
            new_content += f"  * **Component**: {task['component']}\n"
            new_content += f"  * **Effort**: {task['effort']}\n"
            new_content += f"  * **Description**: {task['description']}\n"
            
            if task['dependencies'] and task['dependencies'] != "None":
                new_content += f"  * **Dependencies**: {task['dependencies']}\n"
            
            if task['notes']:
                new_content += f"  * **Notes**: {task['notes']}\n"
            
            new_content += "\n"
    
    # Create task board view
    new_content += "## Task Board View\n\n"
    
    not_started = [task for task in tasks_by_id.values() if task["status"] == "Not Started"]
    in_progress = [task for task in tasks_by_id.values() if task["status"] == "In Progress"]
    blocked = [task for task in tasks_by_id.values() if task["status"] == "Blocked"]
    completed = [task for task in tasks_by_id.values() if task["status"] == "Completed"]
    
    new_content += "### Not Started\n"
    for task in not_started:
        new_content += f"- {task['id']}: {task['title']}\n"
    new_content += "\n"
    
    new_content += "### In Progress\n"
    for task in in_progress:
        new_content += f"- {task['id']}: {task['title']}\n"
    new_content += "\n"
    
    new_content += "### Blocked\n"
    for task in blocked:
        new_content += f"- {task['id']}: {task['title']}\n"
    new_content += "\n"
    
    new_content += "### Completed\n"
    for task in completed:
        new_content += f"- {task['id']}: {task['title']}\n"
    new_content += "\n"
    
    # Create task statistics
    total_tasks = len(tasks_by_id)
    not_started_count = len(not_started)
    in_progress_count = len(in_progress)
    blocked_count = len(blocked)
    completed_count = len(completed)
    completion_rate = f"{(completed_count / total_tasks * 100):.1f}%" if total_tasks > 0 else "0.0%"
    
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_content += "## Task Statistics\n\n"
    new_content += f"- Total Tasks: {total_tasks}\n"
    new_content += f"- Not Started: {not_started_count}\n"
    new_content += f"- In Progress: {in_progress_count}\n"
    new_content += f"- Blocked: {blocked_count}\n"
    new_content += f"- Completed: {completed_count}\n"
    new_content += f"- Completion Rate: {completion_rate}\n\n"
    new_content += f"Last Updated: {now}\n"
    
    # Backup the original file
    backup_path = TASK_FILE_PATH + ".bak"
    os.rename(TASK_FILE_PATH, backup_path)
    
    # Write the new content
    with open(TASK_FILE_PATH, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed taskManagement.md file. Backup saved to {backup_path}")
    print(f"Task statistics: {total_tasks} total, {not_started_count} not started, {in_progress_count} in progress, {blocked_count} blocked, {completed_count} completed")

if __name__ == "__main__":
    main()