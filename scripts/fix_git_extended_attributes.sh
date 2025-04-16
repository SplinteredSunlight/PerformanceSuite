#!/bin/bash
# Script to fix Git extended attributes issues in VSCode
# This script helps resolve issues where files with extended attributes
# show as modified in VSCode's Git integration even though Git CLI
# doesn't see any changes.

echo "Fixing Git extended attributes issues in VSCode..."

# Step 1: Tell Git to ignore changes to file modes
git config --local core.fileMode false
echo "✅ Set git config core.fileMode to false"

# Step 2: Remove extended attributes from problematic files
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS, removing extended attributes..."
    
    # Find all files with extended attributes
    files_with_xattr=$(find . -type f -not -path "*/\.*" -exec ls -la {} \; | grep @ | awk '{print $NF}')
    
    if [ -z "$files_with_xattr" ]; then
        echo "No files with extended attributes found."
    else
        echo "Found files with extended attributes:"
        echo "$files_with_xattr"
        echo ""
        
        echo "Removing extended attributes..."
        for file in $files_with_xattr; do
            xattr -c "$file" 2>/dev/null
            echo "  Processed: $file"
        done
    fi
else
    echo "Not running on macOS, skipping extended attributes removal."
fi

# Step 3: Tell Git to assume these files are unchanged
echo "Setting Git to assume unchanged for problematic files..."
git update-index --assume-unchanged config.yaml .roo/system-prompt-architect 2>/dev/null
echo "✅ Set Git to assume unchanged for known problematic files"

# Step 4: Refresh Git status
git status
echo "✅ Refreshed Git status"

echo ""
echo "Done! If you still see files marked as modified in VSCode:"
echo "1. Try reloading the VSCode window (Cmd+Shift+P > Reload Window)"
echo "2. Check if the .vscode/settings.json file is properly configured"
echo "3. For persistent issues, you may need to close and reopen VSCode"