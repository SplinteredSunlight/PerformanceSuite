#!/usr/bin/env python3
"""
GitHub Desktop MCP Server

This script provides an MCP server for interacting with GitHub Desktop and Git operations.
It allows performing Git operations directly from Roo.
"""

import json
import sys
import os
import subprocess
import re
from typing import Dict, List, Optional, Any, Tuple

class GitHubDesktopManager:
    def __init__(self):
        self.repo_path = os.getcwd()
    
    def _run_command(self, command: List[str]) -> Tuple[str, str, int]:
        """Run a shell command and return stdout, stderr, and return code."""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return stdout, stderr, process.returncode
        except Exception as e:
            return "", str(e), 1
    
    def git_status(self) -> Dict[str, Any]:
        """Get the current Git status."""
        stdout, stderr, returncode = self._run_command(["git", "status", "--porcelain"])
        
        if returncode != 0:
            return {
                "success": False,
                "error": stderr
            }
        
        # Parse the status output
        modified_files = []
        untracked_files = []
        staged_files = []
        
        for line in stdout.splitlines():
            if not line.strip():
                continue
            
            status = line[:2]
            file_path = line[3:].strip()
            
            if status.startswith("M"):
                modified_files.append(file_path)
            elif status.startswith("A"):
                staged_files.append(file_path)
            elif status.startswith("??"):
                untracked_files.append(file_path)
            elif status.startswith(" M"):
                modified_files.append(file_path)
            else:
                staged_files.append(file_path)
        
        # Get current branch
        branch_stdout, branch_stderr, branch_returncode = self._run_command(["git", "branch", "--show-current"])
        current_branch = branch_stdout.strip() if branch_returncode == 0 else "unknown"
        
        return {
            "success": True,
            "current_branch": current_branch,
            "modified_files": modified_files,
            "untracked_files": untracked_files,
            "staged_files": staged_files,
            "clean": len(modified_files) == 0 and len(untracked_files) == 0 and len(staged_files) == 0
        }
    
    def git_commit(self, message: str, files: str) -> Dict[str, Any]:
        """Commit changes to the repository."""
        if not message:
            return {
                "success": False,
                "error": "Commit message is required"
            }
        
        # Handle file selection
        file_list = []
        if files.lower() == "all":
            # Stage all files
            stage_stdout, stage_stderr, stage_returncode = self._run_command(["git", "add", "."])
            if stage_returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to stage files: {stage_stderr}"
                }
        else:
            # Stage specific files
            file_list = [f.strip() for f in files.split(",")]
            for file in file_list:
                stage_stdout, stage_stderr, stage_returncode = self._run_command(["git", "add", file])
                if stage_returncode != 0:
                    return {
                        "success": False,
                        "error": f"Failed to stage file {file}: {stage_stderr}"
                    }
        
        # Commit the changes
        stdout, stderr, returncode = self._run_command(["git", "commit", "-m", message])
        
        if returncode != 0:
            return {
                "success": False,
                "error": stderr
            }
        
        return {
            "success": True,
            "message": stdout,
            "files_committed": file_list if files.lower() != "all" else "all"
        }
    
    def git_push(self, remote: Optional[str] = None, branch: Optional[str] = None) -> Dict[str, Any]:
        """Push commits to the remote repository."""
        remote = remote or "origin"
        
        if branch:
            stdout, stderr, returncode = self._run_command(["git", "push", remote, branch])
        else:
            stdout, stderr, returncode = self._run_command(["git", "push", remote])
        
        if returncode != 0:
            return {
                "success": False,
                "error": stderr
            }
        
        return {
            "success": True,
            "message": stdout
        }
    
    def git_pull(self, remote: Optional[str] = None, branch: Optional[str] = None) -> Dict[str, Any]:
        """Pull changes from the remote repository."""
        remote = remote or "origin"
        
        if branch:
            stdout, stderr, returncode = self._run_command(["git", "pull", remote, branch])
        else:
            stdout, stderr, returncode = self._run_command(["git", "pull", remote])
        
        if returncode != 0:
            return {
                "success": False,
                "error": stderr
            }
        
        return {
            "success": True,
            "message": stdout
        }
    
    def git_branch(self, name: str, create: Optional[bool] = False) -> Dict[str, Any]:
        """Create or switch branches."""
        if not name:
            return {
                "success": False,
                "error": "Branch name is required"
            }
        
        if create:
            # Create a new branch
            stdout, stderr, returncode = self._run_command(["git", "checkout", "-b", name])
        else:
            # Switch to an existing branch
            stdout, stderr, returncode = self._run_command(["git", "checkout", name])
        
        if returncode != 0:
            return {
                "success": False,
                "error": stderr
            }
        
        return {
            "success": True,
            "message": stdout,
            "branch": name,
            "created": create
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
        
        git_manager = GitHubDesktopManager()
        
        if tool_name == "git_status":
            result = git_manager.git_status()
            send_response(result)
        
        elif tool_name == "git_commit":
            message = params.get("message")
            files = params.get("files")
            
            if not message or not files:
                send_error("Missing required parameters: message and files")
                return
            
            result = git_manager.git_commit(message, files)
            send_response(result)
        
        elif tool_name == "git_push":
            remote = params.get("remote")
            branch = params.get("branch")
            
            result = git_manager.git_push(remote, branch)
            send_response(result)
        
        elif tool_name == "git_pull":
            remote = params.get("remote")
            branch = params.get("branch")
            
            result = git_manager.git_pull(remote, branch)
            send_response(result)
        
        elif tool_name == "git_branch":
            name = params.get("name")
            create = params.get("create", False)
            
            if not name:
                send_error("Missing required parameter: name")
                return
            
            # Convert string 'true'/'false' to boolean if needed
            if isinstance(create, str):
                create = create.lower() == 'true'
            
            result = git_manager.git_branch(name, create)
            send_response(result)
        
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