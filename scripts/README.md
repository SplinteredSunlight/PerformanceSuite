# Scripts Directory

This directory contains various scripts used in the PerformanceSuite project. The scripts are organized by functionality.

## Core Scripts

These scripts are essential for the main functionality of the PerformanceSuite:

- **remote_control_mcp.py**: MCP server for remote control functionality between machines
- **remote_control_client.py**: Client for communicating with the remote control server
- **setup_mac_studio_remote.py**: Script to set up the Mac Studio environment remotely
- **task_manager_mcp.py**: MCP server for task management
- **github_desktop_mcp.py**: MCP server for GitHub Desktop integration
- **restart_dashboard.sh**: Script to restart the dashboard server

## Test Scripts

These scripts are used for testing various components:

- **test_audio_analysis.py**: Test script for audio analysis functionality
- **test_osc_receiver.py**: Test script for OSC message receiving
- **test_osc_sender.py**: Test script for OSC message sending
- **test_remote_control.py**: Test script for remote control functionality

## Utility Scripts

These scripts provide utility functions:

- **discover_mac_studio.py**: Script to discover the Mac Studio on the network
- **mac_studio_connect.sh**: Script to establish connection with the Mac Studio
- **mac_studio_transfer.sh**: Script to transfer files to/from the Mac Studio
- **simulate_midi.py**: Script to simulate MIDI input for testing
- **force_refresh.js**: JavaScript utility for forcing dashboard refresh
- **mock_osc.py**: Script to mock OSC messages for testing
- **msg_inspector.py**: Utility to inspect message formats
- **simple_file_transfer.py**: Simple utility for file transfers

## Two-Machine Architecture

The PerformanceSuite uses a two-machine architecture:

1. **Mac Mini M4**: Handles audio processing and analysis
   - Runs the main PerformanceSuite application
   - Connects to audio interface (Quantum 2626)
   - Sends control messages to the Mac Studio

2. **Mac Studio M4**: Handles rendering and visualization
   - Runs the rendering engine
   - Receives control messages from the Mac Mini
   - Generates visual output

The remote control scripts facilitate communication between these two machines.