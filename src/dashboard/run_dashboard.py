#!/usr/bin/env python3
"""
Dashboard Launcher

This script provides a simple way to launch the Performance Suite dashboard.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def get_project_root():
    """Get the project root directory."""
    # Start from the current file's directory
    current_dir = Path(__file__).parent.absolute()
    
    # Go up until we find the project root (where setup.py is)
    while current_dir.name and not (current_dir / 'setup.py').exists():
        parent = current_dir.parent
        if parent == current_dir:  # Reached filesystem root
            break
        current_dir = parent
    
    return current_dir

def run_dashboard():
    """Run the dashboard server and open it in a browser."""
    # Get the project root
    project_root = get_project_root()
    
    # Change to the project root directory
    os.chdir(project_root)
    
    # Define the server port
    port = 8000
    
    print(f"Starting Performance Suite Dashboard on port {port}...")
    print(f"Project root: {project_root}")
    
    # Open the browser
    webbrowser.open(f"http://localhost:{port}")
    
    # Import and run the server
    sys.path.insert(0, str(project_root))
    from src.dashboard.server import run_server
    run_server(port=port)

if __name__ == "__main__":
    run_dashboard()