# Environment Setup Implementation Plan

This document outlines the specific steps needed to complete the environment setup for the Performance Suite project based on the updated environment setup guide.

## Current Status

- Both Mac Mini and Mac Studio have macOS installed
- Network connection is configured with static IPs
- Audio interface (Quantum 2626) is connected to the Mac Mini
- Godot is installed on the Mac Studio but not configured
- Remote control MCP server has been configured in `.roo/mcp.json`

## Implementation Steps

### Phase 1: Mac Mini Setup

1. **Install/Verify Homebrew**
   - Check if Homebrew is installed: `which brew`
   - If not installed, run: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

2. **Install/Verify Python 3.11**
   - Check if Python 3.11 is installed: `python3 --version`
   - If not installed or wrong version, run: `brew install python@3.11`

3. **Install/Verify Miniconda**
   - Check if Miniconda is installed: `which conda`
   - If not installed, run: `brew install --cask miniconda`
   - Initialize conda: `conda init zsh` (or bash if using bash)

4. **Create/Verify Virtual Environment**
   - Check if environment exists: `conda env list | grep performance-suite`
   - If not exists, create it: `conda create -n performance-suite python=3.11`
   - Activate environment: `conda activate performance-suite`

5. **Install GitHub Desktop**
   - Check if GitHub Desktop is installed
   - If not installed, run: `brew install --cask github`
   - Configure GitHub Desktop with local repository

6. **Install Project Dependencies**
   - Navigate to project directory: `cd /Users/dc/Projects/PerformanceSuite`
   - Install dependencies: `pip install -r requirements.txt`
   - Install project in development mode: `pip install -e .`
   - Install paramiko: `pip install paramiko`

7. **Configure Audio Interface**
   - Verify PreSonus Universal Control is installed
   - Configure Quantum 2626 settings:
     - Sample Rate: 96kHz
     - Buffer Size: 32-64 samples
     - Bit Depth: 24-bit

### Phase 2: Mac Studio Setup

1. **Install/Verify Homebrew**
   - Check if Homebrew is installed: `which brew`
   - If not installed, run: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

2. **Install/Verify Python 3.11**
   - Check if Python 3.11 is installed: `python3 --version`
   - If not installed or wrong version, run: `brew install python@3.11`

3. **Install Minimal Dependencies**
   - Install required packages: `pip install python-osc paramiko`

4. **Configure Godot**
   - Open Godot and configure performance settings:
     - Set target frame rate to 60fps minimum
     - Optimize graphics settings for performance

5. **Create Project Directory Structure**
   - Create necessary directories:
     ```bash
     mkdir -p ~/PerformanceSuite/scripts
     mkdir -p ~/PerformanceSuite/src
     mkdir -p ~/PerformanceSuite/godot_project
     ```

### Phase 3: Remote Control Setup

1. **Enable Remote Login on Mac Studio**
   - Go to System Settings > Sharing
   - Enable "Remote Login" to allow SSH access

2. **Set up SSH Key-based Authentication**
   - On Mac Mini, generate SSH key: `ssh-keygen -t ed25519 -C "mac-mini-to-mac-studio"`
   - Copy key to Mac Studio: `ssh-copy-id username@192.168.1.20`
   - Create SSH config for easier access:
     ```bash
     echo "Host mac-studio
       HostName 192.168.1.20
       User yourusername
       IdentityFile ~/.ssh/id_ed25519" >> ~/.ssh/config
     ```

3. **Start Remote Control Server on Mac Studio**
   - Transfer necessary scripts to Mac Studio:
     ```bash
     scp scripts/remote_control_mcp.py mac-studio:~/PerformanceSuite/scripts/
     ```
   - Start the server:
     ```bash
     ssh mac-studio "cd ~/PerformanceSuite && python scripts/remote_control_mcp.py --port 5000"
     ```

4. **Start Remote Control Client on Mac Mini**
   - Navigate to project directory: `cd /Users/yourusername/Projects/PerformanceSuite`
   - Start the client: `python scripts/remote_control_client.py`

### Phase 4: Testing

1. **Test Network Communication**
   - Transfer test scripts to Mac Studio:
     ```bash
     scp scripts/test_osc_receiver.py mac-studio:~/PerformanceSuite/scripts/
     ```
   - On Mac Mini, run: `python scripts/test_osc_sender.py --ip 192.168.1.20 --port 5000`
   - On Mac Studio, run: `python scripts/test_osc_receiver.py --port 5000`
   - Verify messages are received with minimal latency

2. **Test Keyboard/Mouse Sharing**
   - Move cursor between machines to verify Universal Control is working
   - Test keyboard input on both machines

3. **Test Audio Interface**
   - Play audio through the Quantum 2626
   - Run audio analysis test: `python scripts/test_audio_analysis.py`
   - Verify audio is properly captured and analyzed

4. **Test Remote Control**
   - On Mac Mini, run: `python scripts/test_remote_control.py`
   - Verify connection to Mac Studio and remote control functionality

## Completion Criteria

The environment setup is considered complete when:

1. All software is installed on both machines
2. Network connectivity is verified
3. Keyboard/mouse sharing is working
4. Audio interface is properly configured
5. Remote control system is functioning
6. All tests pass successfully

## Next Steps After Completion

1. Begin implementing the audio analysis pipeline
2. Develop the agent system
3. Set up the rendering pipeline in Godot
4. Integrate all components

## Troubleshooting Guide

### Common Issues and Solutions

1. **Homebrew Installation Fails**
   - Check internet connection
   - Try running with sudo: `sudo /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

2. **Python Version Issues**
   - Ensure PATH is correctly set: `export PATH="/usr/local/opt/python@3.11/bin:$PATH"`
   - Restart terminal after installation

3. **Conda Environment Problems**
   - Try creating without version specification: `conda create -n performance-suite python`
   - Check for conflicts: `conda list`

4. **Remote Control Connection Issues**
   - Verify IP addresses are correct
   - Check that both machines are on the same network
   - Ensure firewall is not blocking connections
   - Verify SSH access is enabled

5. **Audio Interface Not Detected**
   - Check Thunderbolt connection
   - Restart the audio interface
   - Reinstall PreSonus drivers