#!/bin/bash
# Restart Dashboard Script
# This script stops any running dashboard server and starts a new one

echo "Restarting Performance Suite Dashboard..."

# Find and kill any running dashboard processes
pkill -f "python3 src/dashboard/run_dashboard.py"

# Wait a moment for the port to be released
sleep 2

# Start the dashboard server
python3 src/dashboard/run_dashboard.py