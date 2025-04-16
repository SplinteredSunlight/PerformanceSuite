#!/bin/bash
# Master script to fix all Git and VSCode integration issues
# This script runs all the fix scripts in the recommended order

echo "Running all fix scripts in the recommended order..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Step 1: Run fix_git_extended_attributes.sh
echo ""
echo "Step 1: Running fix_git_extended_attributes.sh..."
"$SCRIPT_DIR/fix_git_extended_attributes.sh"

# Step 2: Run fix_vscode_git.sh
echo ""
echo "Step 2: Running fix_vscode_git.sh..."
"$SCRIPT_DIR/fix_vscode_git.sh"

# Step 3: Run fix_config_yaml.sh
echo ""
echo "Step 3: Running fix_config_yaml.sh..."
"$SCRIPT_DIR/fix_config_yaml.sh"

# Step 4: Run fix_vscode_workspace.sh
echo ""
echo "Step 4: Running fix_vscode_workspace.sh..."
"$SCRIPT_DIR/fix_vscode_workspace.sh"

# Step 5: Make sure config.yaml is visible in VSCode
echo ""
echo "Step 5: Making sure config.yaml is visible in VSCode..."
if [ -f ".vscode/settings.json" ]; then
    # Use sed to replace "**/config.yaml": true with "**/config.yaml": false
    sed -i '' 's/"*\/config.yaml": true/"*\/config.yaml": false/g' .vscode/settings.json
    echo "✅ Updated .vscode/settings.json to make config.yaml visible"
    
    # Add and commit the changes
    git add .vscode/settings.json
    git commit -m "Update VSCode settings to keep config.yaml visible" > /dev/null 2>&1
    echo "✅ Committed changes to .vscode/settings.json"
else
    echo "❌ .vscode/settings.json not found"
fi

echo ""
echo "All fix scripts have been run."
echo ""
echo "Please restart VSCode for the changes to take effect."
echo ""
echo "If you still see issues after restarting VSCode:"
echo "1. Try running this script again"
echo "2. Try closing and reopening VSCode"
echo "3. Try restarting your computer"