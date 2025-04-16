#!/usr/bin/env node
/**
 * This script modifies VSCode's workspace settings to completely ignore specific files.
 * It directly modifies the .vscode/settings.json file in the current workspace.
 */

const fs = require('fs');
const path = require('path');

// Get the path to VSCode workspace settings
const workspacePath = path.join(process.cwd(), '.vscode', 'settings.json');
const workspaceDir = path.join(process.cwd(), '.vscode');

console.log(`Attempting to modify VSCode workspace settings at: ${workspacePath}`);

// Files to ignore in Git
const filesToIgnore = [
  '**/config.yaml',
  '**/.roo/system-prompt-architect'
];

try {
  // Create .vscode directory if it doesn't exist
  if (!fs.existsSync(workspaceDir)) {
    fs.mkdirSync(workspaceDir, { recursive: true });
    console.log('Created .vscode directory');
  }

  // Read the current settings
  let settings = {};
  if (fs.existsSync(workspacePath)) {
    const settingsContent = fs.readFileSync(workspacePath, 'utf8');
    try {
      settings = JSON.parse(settingsContent);
      console.log('Successfully read VSCode workspace settings');
    } catch (e) {
      console.log('Error parsing settings.json, creating new one');
    }
  } else {
    console.log('VSCode workspace settings file not found, creating new one');
  }

  // Update Git settings
  if (!settings['git.ignoredFiles']) {
    settings['git.ignoredFiles'] = [];
  }

  // Add our files to ignore if they're not already there
  let updated = false;
  for (const file of filesToIgnore) {
    if (!settings['git.ignoredFiles'].includes(file)) {
      settings['git.ignoredFiles'].push(file);
      updated = true;
    }
  }

  // Make sure Git is enabled
  settings['git.enabled'] = true;
  
  // Set Git to ignore file mode changes
  settings['git.ignoreLimitWarning'] = true;
  
  // Disable Git file status decorations for the ignored files
  settings['git.decorations.enabled'] = true;
  
  // Ensure Git autorefresh is enabled
  settings['git.autorefresh'] = true;

  // Add files.exclude to hide config.yaml from the explorer
  if (!settings['files.exclude']) {
    settings['files.exclude'] = {
      "**/.git": true,
      "**/.svn": true,
      "**/.hg": true,
      "**/CVS": true,
      "**/.DS_Store": true,
      "**/Thumbs.db": true
    };
  }
  
  // Add config.yaml to files.exclude
  settings['files.exclude']['**/config.yaml'] = true;

  // Write the updated settings back
  fs.writeFileSync(workspacePath, JSON.stringify(settings, null, 2), 'utf8');
  console.log('Successfully updated VSCode workspace settings to ignore specific files');
  console.log('Files now ignored in Git:');
  for (const file of filesToIgnore) {
    console.log(`  - ${file}`);
  }
  console.log('\nPlease restart VSCode for the changes to take effect.');

} catch (error) {
  console.error('Error updating VSCode workspace settings:', error.message);
  process.exit(1);
}