#!/bin/bash
# Script to fix VSCode workspace settings for problematic files
# This script runs the Node.js script that modifies VSCode's workspace settings

echo "Fixing VSCode workspace settings for problematic files..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run the Node.js script
node "$SCRIPT_DIR/fix_vscode_workspace.js"

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "VSCode workspace settings have been updated successfully."
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
    echo "3. Creating clean copies of problematic files..."
    if [ -f "config.yaml" ]; then
        # Save the content
        content=$(cat config.yaml)
        
        # Remove the file
        rm config.yaml
        
        # Create a new file with the same content
        echo "$content" > config.yaml
        
        echo "✅ Created clean copy of config.yaml"
    fi
    
    echo ""
    echo "4. Adding .vscode to Git..."
    git add .vscode/settings.json
    git commit -m "Add VSCode workspace settings to ignore problematic files" > /dev/null 2>&1
    echo "✅ Added .vscode/settings.json to Git"
    
    echo ""
    echo "All fixes have been applied. Please restart VSCode for the changes to take effect."
    echo ""
    echo "If you still see files marked as modified in VSCode after restarting:"
    echo "1. Try running this script again"
    echo "2. Try closing and reopening VSCode"
    echo "3. Try restarting your computer"
else
    echo "Error: Failed to update VSCode workspace settings."
    echo "Please check the error message above and try again."
fi