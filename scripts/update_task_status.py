#!/usr/bin/env python3
"""
Update Task Status Script

This script updates a task's status using the task manager MCP server
and then runs the fix_task_management.py script to ensure the file remains clean.
"""

import sys
import json
import subprocess
import argparse

def update_task(task_id, status, notes=None):
    """Update a task's status using the task manager MCP server."""
    print(f"Updating task {task_id} to status '{status}'...")
    
    # Prepare the request
    params = {
        "task_id": task_id,
        "status": status
    }
    
    if notes:
        params["notes"] = notes
    
    request = {
        "tool": "update_task",
        "params": params
    }
    
    # Send the request to the task manager MCP server
    try:
        result = subprocess.run(
            ["echo", json.dumps(request)],
            stdout=subprocess.PIPE,
            text=True
        )
        
        echo_output = result.stdout.strip()
        
        result = subprocess.run(
            ["python", "scripts/task_manager_mcp.py"],
            input=echo_output,
            stdout=subprocess.PIPE,
            text=True
        )
        
        response = result.stdout.strip()
        
        # Parse the response
        lines = response.split("\n")
        if len(lines) >= 2:
            try:
                response_data = json.loads(lines[1])
                if response_data.get("status") == "success":
                    print(f"Successfully updated task {task_id} to status '{status}'")
                else:
                    print(f"Error updating task: {response_data.get('message', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print(f"Error parsing response: {lines[1]}")
                return False
        else:
            print("Invalid response from task manager MCP server")
            return False
    
    except Exception as e:
        print(f"Error updating task: {str(e)}")
        return False
    
    # Run the fix_task_management.py script to clean up the file
    print("Cleaning up taskManagement.md file...")
    try:
        subprocess.run(["python", "scripts/fix_task_management.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cleaning up file: {str(e)}")
        return False
    
    return True

def get_task_statistics():
    """Get task statistics from the task manager MCP server."""
    request = {
        "tool": "get_task_statistics",
        "params": {}
    }
    
    try:
        result = subprocess.run(
            ["echo", json.dumps(request)],
            stdout=subprocess.PIPE,
            text=True
        )
        
        echo_output = result.stdout.strip()
        
        result = subprocess.run(
            ["python", "scripts/task_manager_mcp.py"],
            input=echo_output,
            stdout=subprocess.PIPE,
            text=True
        )
        
        response = result.stdout.strip()
        
        # Parse the response
        lines = response.split("\n")
        if len(lines) >= 2:
            try:
                response_data = json.loads(lines[1])
                if response_data.get("status") == "success":
                    stats = response_data.get("data", {})
                    print("\nTask Statistics:")
                    print(f"- Total Tasks: {stats.get('total_tasks', 0)}")
                    print(f"- Not Started: {stats.get('not_started', 0)}")
                    print(f"- In Progress: {stats.get('in_progress', 0)}")
                    print(f"- Blocked: {stats.get('blocked', 0)}")
                    print(f"- Completed: {stats.get('completed', 0)}")
                    print(f"- Completion Rate: {stats.get('completion_rate', '0.0%')}")
                else:
                    print(f"Error getting statistics: {response_data.get('message', 'Unknown error')}")
            except json.JSONDecodeError:
                print(f"Error parsing response: {lines[1]}")
        else:
            print("Invalid response from task manager MCP server")
    
    except Exception as e:
        print(f"Error getting statistics: {str(e)}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Update a task's status")
    parser.add_argument("task_id", help="Task ID (e.g., MB-001)")
    parser.add_argument("status", choices=["Not Started", "In Progress", "Blocked", "Completed"], 
                        help="New status for the task")
    parser.add_argument("--notes", help="Additional notes for the task")
    
    args = parser.parse_args()
    
    if update_task(args.task_id, args.status, args.notes):
        get_task_statistics()

if __name__ == "__main__":
    main()