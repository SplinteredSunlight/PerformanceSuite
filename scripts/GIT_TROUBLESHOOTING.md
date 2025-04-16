# Git Troubleshooting in VSCode

This directory contains scripts to help troubleshoot and fix Git integration issues in VSCode, particularly with files that have extended attributes on macOS.

## Problem

On macOS, files can have extended attributes (xattrs) that cause them to show as modified in VSCode's Git integration, even though Git itself doesn't see any changes. This is particularly problematic for:

- `config.yaml`
- `.roo/system-prompt-architect`

## Solution

We've created several scripts to fix this issue:

### 1. `fix_vscode_git.sh`

This is the main script you should run when you encounter Git integration issues in VSCode.

```bash
./scripts/fix_vscode_git.sh
```

This script:

1. Modifies VSCode's global Git settings to ignore specific files
2. Configures Git to ignore file mode changes
3. Sets Git to assume unchanged for problematic files
4. Sets Git to skip worktree for `config.yaml`
5. Creates clean copies of problematic files
6. Creates/updates `.gitattributes` to mark problematic files as binary

### 2. `fix_vscode_git.js`

This is a Node.js script that modifies VSCode's global settings. It's called by `fix_vscode_git.sh`.

### 3. `fix_git_extended_attributes.sh`

This script focuses on removing extended attributes from files and configuring Git to ignore changes to specific files.

```bash
./scripts/fix_git_extended_attributes.sh
```

### 4. `fix_config_yaml.sh`

This script specifically fixes issues with `config.yaml` showing as untracked or modified in Git.

```bash
./scripts/fix_config_yaml.sh
```

Use this script if you're still seeing issues with `config.yaml` after running the other scripts.

### 5. `fix_vscode_workspace.sh`

This script modifies VSCode's workspace settings (not global settings) to ignore specific files in Git integration.

```bash
./scripts/fix_vscode_workspace.sh
```

This is the most aggressive approach and should be used if none of the other scripts work. It creates a `.vscode/settings.json` file in your workspace with specific settings to ignore problematic files.

## When to Use

Run these scripts when:

1. You see files incorrectly showing as modified in VSCode's Git integration
2. You've made no actual changes to the files but they still show as modified
3. After pulling changes from a remote repository

## Recommended Order

If you're experiencing Git integration issues, try these scripts in the following order:

1. `fix_git_extended_attributes.sh` - Basic fix for extended attributes
2. `fix_vscode_git.sh` - Comprehensive fix including VSCode global settings
3. `fix_config_yaml.sh` - Specific fix for config.yaml issues
4. `fix_vscode_workspace.sh` - Most aggressive approach using workspace settings

After running each script, restart VSCode completely and check if the issue is resolved before trying the next script.

## After Running the Scripts

After running the scripts:

1. **Restart VSCode completely** (not just reload window)
2. If issues persist, try the additional steps mentioned in the script output

## Technical Details

These scripts use several approaches to fix Git integration issues:

1. **VSCode Settings**: Modifying VSCode's global Git settings
2. **Git Configuration**: Using Git's built-in mechanisms to ignore changes
3. **Extended Attributes**: Removing extended attributes from files
4. **File Recreation**: Creating clean copies of files
5. **Git Attributes**: Using `.gitattributes` to mark files as binary

## Troubleshooting

If you still see issues after running these scripts:

1. Run `git status` in the terminal to check if Git itself sees any changes
2. Check if the files have extended attributes: `ls -la@ config.yaml`
3. Try running the scripts again
4. Try restarting your computer