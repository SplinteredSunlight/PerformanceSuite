#!/usr/bin/env python3
"""
Dashboard Server

This script provides a web server for the Performance Suite dashboard.
It serves the dashboard UI and provides API endpoints for accessing task data.
"""

import json
import re
import os
import sys
import subprocess
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Constants
TASK_FILE_PATH = "memory-bank/taskManagement.md"
TASK_ID_PATTERN = r"MB-(\d+)"
TASK_ENTRY_PATTERN = r"\* ([^\n]+)\s+\* \*\*ID\*\*: (MB-\d+)\s+\* \*\*Status\*\*: ([^\n]+)\s+\* \*\*Priority\*\*: ([^\n]+)\s+\* \*\*Component\*\*: ([^\n]+)\s+\* \*\*Effort\*\*: ([^\n]+)\s+\* \*\*Description\*\*: ([^\n]+)(?:\s+\* \*\*Dependencies\*\*: ([^\n]+))?(?:\s+\* \*\*Notes\*\*: ([^\n]+))?"

# Task status options
VALID_STATUSES = ["Not Started", "In Progress", "Blocked", "Completed"]
VALID_COMPONENTS = ["Audio Analysis", "Agent System", "Rendering", "Infrastructure"]
VALID_PRIORITIES = ["High", "Medium", "Low"]
VALID_EFFORTS = ["Large", "Medium", "Small"]

# MCP Server definitions
MCP_SERVERS = [
    {
        "id": "dashboard",
        "name": "Dashboard Server",
        "script": "src/dashboard/run_dashboard.py",
        "description": "Serves the Performance Suite dashboard UI"
    },
    {
        "id": "task_manager",
        "name": "Task Manager MCP",
        "script": "scripts/task_manager_mcp.py",
        "description": "Manages tasks in the Memory Bank taskManagement.md file"
    },
    {
        "id": "github_desktop",
        "name": "GitHub Desktop MCP",
        "script": "scripts/github_desktop_mcp.py",
        "description": "Provides GitHub Desktop integration"
    },
    {
        "id": "remote_control",
        "name": "Remote Control MCP",
        "script": "scripts/remote_control_mcp.py",
        "description": "Controls the Mac Studio from the Mac Mini"
    }
]

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
            print(f"Error loading tasks: {str(e)}", file=sys.stderr)
            self.tasks = []

    def list_tasks(self, status: Optional[str] = None, component: Optional[str] = None) -> List[Dict[str, str]]:
        """List tasks, optionally filtered by status or component."""
        filtered_tasks = self.tasks
        
        if status:
            if status not in VALID_STATUSES:
                return []
            filtered_tasks = [task for task in filtered_tasks if task["status"] == status]
        
        if component:
            if component not in VALID_COMPONENTS:
                return []
            filtered_tasks = [task for task in filtered_tasks if task["component"] == component]
        
        return filtered_tasks

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

    def get_tasks_by_component(self) -> Dict[str, List[Dict[str, str]]]:
        """Group tasks by component."""
        result = {}
        for component in VALID_COMPONENTS:
            result[component] = [task for task in self.tasks if task["component"] == component]
        return result

def is_process_running(script_name):
    """Check if a process is running by script name."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and len(cmdline) > 1:
                if script_name in ' '.join(cmdline):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.task_manager = TaskManager()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urllib.parse.urlparse(self.path)
        
        # API endpoints
        if parsed_path.path == '/api/tasks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            
            # Parse query parameters
            query = urllib.parse.parse_qs(parsed_path.query)
            status = query.get('status', [None])[0]
            component = query.get('component', [None])[0]
            
            tasks = self.task_manager.list_tasks(status, component)
            self.wfile.write(json.dumps(tasks).encode())
            return
        
        elif parsed_path.path == '/api/statistics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            
            stats = self.task_manager.get_task_statistics()
            self.wfile.write(json.dumps(stats).encode())
            return
        
        elif parsed_path.path == '/api/components':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            
            components = self.task_manager.get_tasks_by_component()
            self.wfile.write(json.dumps(components).encode())
            return
            
        elif parsed_path.path == '/api/mcp_servers':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            
            # Get MCP server status
            mcp_servers = []
            for server in MCP_SERVERS:
                server_info = server.copy()
                server_info['running'] = is_process_running(server['script'])
                mcp_servers.append(server_info)
            
            self.wfile.write(json.dumps(mcp_servers).encode())
            return
            
        elif parsed_path.path.startswith('/api/mcp_action/'):
            # Extract server ID and action from path
            parts = parsed_path.path.split('/')
            if len(parts) >= 4:
                server_id = parts[3]
                action = parts[4] if len(parts) >= 5 else 'status'
                
                # Find the server
                server = next((s for s in MCP_SERVERS if s['id'] == server_id), None)
                
                if server:
                    result = {'status': 'error', 'message': 'Invalid action'}
                    
                    if action == 'start':
                        # Start the server
                        if not is_process_running(server['script']):
                            try:
                                subprocess.Popen(['python', server['script']], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE)
                                result = {'status': 'success', 'message': f"Started {server['name']}"}
                            except Exception as e:
                                result = {'status': 'error', 'message': str(e)}
                        else:
                            result = {'status': 'info', 'message': f"{server['name']} is already running"}
                    
                    elif action == 'stop':
                        # Stop the server
                        try:
                            subprocess.run(['pkill', '-f', server['script']])
                            result = {'status': 'success', 'message': f"Stopped {server['name']}"}
                        except Exception as e:
                            result = {'status': 'error', 'message': str(e)}
                    
                    elif action == 'restart':
                        # Restart the server
                        try:
                            subprocess.run(['pkill', '-f', server['script']])
                            subprocess.Popen(['python', server['script']], 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE)
                            result = {'status': 'success', 'message': f"Restarted {server['name']}"}
                        except Exception as e:
                            result = {'status': 'error', 'message': str(e)}
                    
                    elif action == 'status':
                        # Get server status
                        running = is_process_running(server['script'])
                        result = {
                            'status': 'success', 
                            'running': running,
                            'message': f"{server['name']} is {'running' if running else 'stopped'}"
                        }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    return
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'error', 'message': 'Server not found'}).encode())
                    return
        
        # Serve static files
        if parsed_path.path == '/':
            self.path = '/src/dashboard/templates/index.html'
        elif parsed_path.path.startswith('/static/'):
            self.path = '/src/dashboard' + parsed_path.path
            
            # Add cache-busting headers for CSS and JS files
            if parsed_path.path.endswith('.css') or parsed_path.path.endswith('.js'):
                self.send_response(200)
                if parsed_path.path.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                else:
                    self.send_header('Content-type', 'application/javascript')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                
                # Read the file content
                try:
                    with open(os.getcwd() + self.path, 'rb') as f:
                        content = f.read()
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except:
                    pass
        
        return SimpleHTTPRequestHandler.do_GET(self)

def run_server(port=8000):
    """Run the dashboard server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"Starting dashboard server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()