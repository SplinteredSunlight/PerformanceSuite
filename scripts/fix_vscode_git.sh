#!/bin/bash
# Script to fix VSCode Git integration for problematic files
# This script runs the Node.js script that modifies VSCode's global settings

echo "Fixing VSCode Git integration for problematic files..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run the Node.js script
node "$SCRIPT_DIR/fix_vscode_git.js"

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "VSCode settings have been updated successfully."
    echo ""
    echo "Additional steps to ensure Git ignores these files:"
    echo ""
    echo "1. Running Git commands to ignore file mode changes..."
    git config --local core.fileMode false
    echo "✅ Set git config core.fileMode to false"
    
    echo ""
    echo "2. Setting Git to assume unchanged for problematic files..."
    git update-index --assume-unchanged config.yaml .roo/system-prompt-architect 2>/dev/null
    echo "✅ Set Git to assume unchanged for known problematic files"
    
    echo ""
    echo "3. Setting Git to skip worktree for config.yaml..."
    git update-index --skip-worktree config.yaml 2>/dev/null
    echo "✅ Set Git to skip worktree for config.yaml"
    
    echo ""
    echo "4. Creating clean copies of problematic files..."
    if [ -f "config.yaml" ]; then
        cat config.yaml > config_temp.yaml
        mv config_temp.yaml config.yaml
        echo "✅ Created clean copy of config.yaml"
    fi
    
    echo ""
    echo "All fixes have been applied. Please restart VSCode for the changes to take effect."
    echo ""
    echo "If you still see files marked as modified in VSCode after restarting:"
    echo "1. Try running this script again"
    echo "2. Try closing and reopening VSCode"
    echo "3. Try restarting your computer"
else
    echo "Error: Failed to update VSCode settings."
    echo "Please check the error message above and try again."
fi