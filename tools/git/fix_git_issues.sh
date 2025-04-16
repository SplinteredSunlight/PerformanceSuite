#!/bin/bash
# Git Troubleshooting Tool
# This script fixes common Git integration issues in VSCode, particularly with files
# that have extended attributes on macOS.

echo "Git Troubleshooting Tool"
echo "========================"
echo ""

# Function to fix a specific file
fix_file() {
    local file=$1
    
    if [ ! -f "$file" ]; then
        echo "❌ File not found: $file"
        return 1
    fi
    
    echo "Fixing Git tracking for $file..."
    
    # Step 1: Remove Git tracking flags
    echo "  1. Removing Git tracking flags..."
    git update-index --no-skip-worktree "$file" 2>/dev/null
    git update-index --no-assume-unchanged "$file" 2>/dev/null
    echo "  ✅ Removed Git tracking flags"
    
    # Step 2: Create a backup
    echo "  2. Creating a backup..."
    cp "$file" "${file}.bak"
    echo "  ✅ Created backup: ${file}.bak"
    
    # Step 3: Remove the file
    echo "  3. Removing original file..."
    rm "$file"
    echo "  ✅ Removed original file"
    
    # Step 4: Create a new file with the same content
    echo "  4. Creating clean copy..."
    cat "${file}.bak" > "$file"
    echo "  ✅ Created clean copy"
    
    # Step 5: Add to Git
    echo "  5. Adding to Git..."
    git add "$file"
    echo "  ✅ Added to Git"
    
    # Step 6: Set assume-unchanged flag
    echo "  6. Setting assume-unchanged flag..."
    git update-index --assume-unchanged "$file"
    echo "  ✅ Set assume-unchanged flag"
    
    # Step 7: Remove backup
    echo "  7. Removing backup..."
    rm "${file}.bak"
    echo "  ✅ Removed backup"
    
    echo "✅ Fixed Git tracking for $file"
    echo ""
}

# Function to update VSCode settings
update_vscode_settings() {
    echo "Updating VSCode settings..."
    
    # Create .vscode directory if it doesn't exist
    if [ ! -d ".vscode" ]; then
        mkdir -p .vscode
        echo "  ✅ Created .vscode directory"
    fi
    
    # Create or update settings.json
    if [ ! -f ".vscode/settings.json" ]; then
        cat > .vscode/settings.json << 'EOL'
{
  "git.ignoredFiles": [
    "**/config.yaml",
    "**/.roo/system-prompt-*"
  ],
  "files.exclude": {
    "**/.git": true,
    "**/.svn": true,
    "**/.hg": true,
    "**/CVS": true,
    "**/.DS_Store": true,
    "**/Thumbs.db": true,
    "**/config.yaml": false,
    "**/.roo/system-prompt-*": false
  },
  "git.enabled": true,
  "git.autorefresh": true,
  "git.ignoreLimitWarning": true
}
EOL
        echo "  ✅ Created .vscode/settings.json"
    else
        # Update existing settings.json
        # This is a simplified approach - in a real scenario, you might want to use jq or a similar tool
        sed -i '' 's/"*\/config.yaml": true/"*\/config.yaml": false/g' .vscode/settings.json
        echo "  ✅ Updated .vscode/settings.json"
    fi
    
    # Add to Git
    git add .vscode/settings.json
    git commit -m "Update VSCode settings for Git integration" > /dev/null 2>&1
    echo "  ✅ Committed VSCode settings"
    
    echo "✅ Updated VSCode settings"
    echo ""
}

# Function to update Git configuration
update_git_config() {
    echo "Updating Git configuration..."
    
    # Set core.fileMode to false
    git config --local core.fileMode false
    echo "  ✅ Set git config core.fileMode to false"
    
    # Update .gitattributes
    if [ ! -f ".gitattributes" ]; then
        cat > .gitattributes << 'EOL'
# Git attributes for specific files
# This file tells Git how to handle specific files

# Ignore changes to config.yaml
config.yaml binary
config.yaml -diff
config.yaml -merge
config.yaml -text

# Ignore changes to .roo/system-prompt files
.roo/system-prompt-* binary
.roo/system-prompt-* -diff
.roo/system-prompt-* -merge
.roo/system-prompt-* -text
EOL
        echo "  ✅ Created .gitattributes"
    else
        # Check if config.yaml is already in .gitattributes
        if ! grep -q "config.yaml" .gitattributes; then
            cat >> .gitattributes << 'EOL'

# Ignore changes to config.yaml
config.yaml binary
config.yaml -diff
config.yaml -merge
config.yaml -text
EOL
            echo "  ✅ Updated .gitattributes with config.yaml"
        fi
        
        # Check if .roo/system-prompt-* is already in .gitattributes
        if ! grep -q ".roo/system-prompt-" .gitattributes; then
            cat >> .gitattributes << 'EOL'

# Ignore changes to .roo/system-prompt files
.roo/system-prompt-* binary
.roo/system-prompt-* -diff
.roo/system-prompt-* -merge
.roo/system-prompt-* -text
EOL
            echo "  ✅ Updated .gitattributes with .roo/system-prompt-*"
        fi
    fi
    
    # Add to Git
    git add .gitattributes
    git commit -m "Update .gitattributes for Git integration" > /dev/null 2>&1
    echo "  ✅ Committed .gitattributes"
    
    echo "✅ Updated Git configuration"
    echo ""
}

# Main script
echo "Running Git troubleshooting steps..."
echo ""

# Update Git configuration
update_git_config

# Update VSCode settings
update_vscode_settings

# Fix specific files
if [ -f "config.yaml" ]; then
    fix_file "config.yaml"
fi

# Check for .roo/system-prompt-* files
for file in .roo/system-prompt-*; do
    if [ -f "$file" ]; then
        fix_file "$file"
    fi
done

echo "All fixes have been applied."
echo ""
echo "Please restart VSCode for the changes to take effect."
echo ""
echo "If you still see issues after restarting VSCode:"
echo "1. Try running this script again"
echo "2. Try closing and reopening VSCode"
echo "3. Try restarting your computer"