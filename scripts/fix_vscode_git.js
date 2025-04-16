#!/usr/bin/env node
/**
 * This script modifies VSCode's Git extension settings to completely ignore specific files.
 * It directly modifies the VSCode user settings.json file.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Get the path to VSCode settings
const homeDir = os.homedir();
const vscodePath = path.join(homeDir, 'Library', 'Application Support', 'Code', 'User', 'settings.json');

console.log(`Attempting to modify VSCode settings at: ${vscodePath}`);

// Files to ignore in Git
const filesToIgnore = [
  '**/config.yaml',
  '**/.roo/system-prompt-architect'
];

try {
  // Read the current settings
  let settings = {};
  if (fs.existsSync(vscodePath)) {
    const settingsContent = fs.readFileSync(vscodePath, 'utf8');
    settings = JSON.parse(settingsContent);
    console.log('Successfully read VSCode settings');
  } else {
    console.log('VSCode settings file not found, creating new one');
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
  if (!settings['git.decorations.enabled']) {
    settings['git.decorations.enabled'] = true;
  }
  
  // Ensure Git autorefresh is enabled
  settings['git.autorefresh'] = true;

  // Write the updated settings back
  if (updated) {
    fs.writeFileSync(vscodePath, JSON.stringify(settings, null, 2), 'utf8');
    console.log('Successfully updated VSCode settings to ignore specific files in Git');
    console.log('Files now ignored in Git:');
    for (const file of filesToIgnore) {
      console.log(`  - ${file}`);
    }
    console.log('\nPlease restart VSCode for the changes to take effect.');
  } else {
    console.log('No changes needed, files are already ignored in Git settings');
  }

} catch (error) {
  console.error('Error updating VSCode settings:', error.message);
  process.exit(1);
}