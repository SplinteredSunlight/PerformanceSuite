# Git Troubleshooting Tools

This directory contains tools to help troubleshoot and fix Git integration issues in VSCode, particularly with files that have extended attributes on macOS.

## Problem

On macOS, files can have extended attributes (xattrs) that cause them to show as modified in VSCode's Git integration, even though Git itself doesn't see any changes. This is particularly problematic for:

- `config.yaml`
- `.roo/system-prompt-*` files

## Solution

The `fix_git_issues.sh` script provides a comprehensive solution to these issues by:

1. Updating Git configuration
2. Updating VSCode settings
3. Fixing specific files by recreating them from scratch

## Usage

```bash
./tools/git/fix_git_issues.sh
```

## How It Works

The script performs the following actions:

### 1. Git Configuration

- Sets `core.fileMode` to `false` to ignore file mode changes
- Creates/updates `.gitattributes` to mark problematic files as binary
- Configures Git to ignore diffs, merges, and text conversions for these files

### 2. VSCode Settings

- Creates/updates `.vscode/settings.json` to ignore specific files in Git integration
- Ensures files remain visible in the VSCode file explorer

### 3. File Fixing

For each problematic file, the script:

1. Removes Git tracking flags
2. Creates a backup
3. Removes the original file
4. Creates a new file with the same content
5. Adds the file to Git
6. Sets the `--assume-unchanged` flag
7. Removes the backup

## Troubleshooting

If you still see issues after running the script:

1. Try running the script again
2. Try closing and reopening VSCode
3. Try restarting your computer

## Technical Details

This solution works by combining multiple approaches:

1. Git's native `.gitattributes` mechanism
2. VSCode's Git integration settings
3. Git's file tracking flags
4. File recreation to remove extended attributes