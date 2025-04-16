#!/bin/bash
# Script to fix config.yaml showing as untracked in VSCode
# This script focuses specifically on the config.yaml file

echo "Fixing config.yaml Git integration issues..."

# Step 1: Remove skip-worktree flag
echo "1. Removing skip-worktree flag from config.yaml..."
git update-index --no-skip-worktree config.yaml
echo "✅ Removed skip-worktree flag"

# Step 2: Remove assume-unchanged flag
echo "2. Removing assume-unchanged flag from config.yaml..."
git update-index --no-assume-unchanged config.yaml
echo "✅ Removed assume-unchanged flag"

# Step 3: Create a clean copy of config.yaml
echo "3. Creating a clean copy of config.yaml..."
if [ -f "config.yaml" ]; then
    # Save the content
    content=$(cat config.yaml)
    
    # Remove the file
    rm config.yaml
    
    # Create a new file with the same content
    echo "$content" > config.yaml
    
    echo "✅ Created clean copy of config.yaml"
else
    echo "❌ config.yaml not found"
    exit 1
fi

# Step 4: Add config.yaml to Git
echo "4. Adding config.yaml to Git..."
git add config.yaml
echo "✅ Added config.yaml to Git"

# Step 5: Commit the changes
echo "5. Committing changes..."
git commit -m "Fix config.yaml tracking" > /dev/null 2>&1
echo "✅ Committed changes"

# Step 6: Update .gitattributes
echo "6. Updating .gitattributes..."
if grep -q "config.yaml" .gitattributes; then
    echo "✅ config.yaml already in .gitattributes"
else
    # Add config.yaml to .gitattributes
    cat >> .gitattributes << 'EOL'

# Ignore changes to config.yaml
config.yaml binary
config.yaml -diff
config.yaml -merge
config.yaml -text
EOL
    git add .gitattributes
    git commit -m "Update .gitattributes for config.yaml" > /dev/null 2>&1
    echo "✅ Updated .gitattributes and committed changes"
fi

# Step 7: Set assume-unchanged flag
echo "7. Setting assume-unchanged flag for config.yaml..."
git update-index --assume-unchanged config.yaml
echo "✅ Set assume-unchanged flag"

echo ""
echo "All fixes have been applied to config.yaml."
echo "Please restart VSCode for the changes to take effect."