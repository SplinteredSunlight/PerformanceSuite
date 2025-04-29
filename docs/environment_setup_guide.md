# Performance Suite: Environment Setup Guide

This guide provides step-by-step instructions for setting up the two-machine environment for the Performance Suite project by SplinteredSunlight.

## Hardware Requirements

- **Machine 1 (Processing & Audio)**: Mac Mini M4 with 16GB RAM
- **Machine 2 (Rendering)**: Mac Studio M4 with 64GB RAM
- **Network**: 10Gbps Ethernet cable (or 1Gbps minimum)
- **Audio Interface**: PreSonus Quantum 2626 Thunderbolt 3 audio interface

## Network Configuration

### Step 1: Physical Connection
1. Connect both machines directly using an Ethernet cable
2. Ensure both machines are powered on

### Step 2: Configure Static IP Addresses

#### On Machine 1 (Mac Mini):
1. Open System Settings > Network
2. Select the Ethernet connection
3. Click "Details..."
4. Change from "Using DHCP" to "Manually"
5. Set the following:
   - IP Address: 192.168.1.10
   - Subnet Mask: 255.255.255.0
   - Router: 192.168.1.1 (if needed)
6. Click "OK" to save changes

#### On Machine 2 (Mac Studio):
1. Open System Settings > Network
2. Select the Ethernet connection
3. Click "Details..."
4. Change from "Using DHCP" to "Manually"
5. Set the following:
   - IP Address: 192.168.1.20
   - Subnet Mask: 255.255.255.0
   - Router: 192.168.1.1 (if needed)
6. Click "OK" to save changes

### Step 3: Verify Connection
1. On Machine 1, open Terminal and run:
   ```
   ping 192.168.1.20
   ```
2. On Machine 2, open Terminal and run:
   ```
   ping 192.168.1.10
   ```
3. Both should show successful ping responses with low latency (<1ms)

## Keyboard/Mouse/Display Sharing Setup

### Option 1: Universal Control (Recommended)

#### Prerequisites:
- Both Macs must be signed in to the same Apple ID
- Both Macs must have Bluetooth, Wi-Fi, and Handoff turned on
- Both Macs must be running macOS Monterey or later

#### Setup:
1. On both machines, go to System Settings > Displays > Advanced
2. Enable "Allow your pointer and keyboard to move between any nearby Mac or iPad"
3. On the same screen, ensure "Push through the edge of a display to connect a nearby Mac or iPad" is enabled
4. Position your displays in the arrangement you prefer
5. Move your cursor to the edge of one display to seamlessly transition to the other Mac

### Option 2: Barrier (Alternative)

If Universal Control doesn't work well for your setup, you can use Barrier, an open-source software KVM:

#### Installation:
1. Download Barrier from https://github.com/debauchee/barrier/releases for both machines
2. Install on both machines

#### Configuration:
1. On your primary machine (where keyboard/mouse are physically connected):
   - Launch Barrier
   - Select "Server (share this computer's mouse and keyboard)"
   - Configure the screen arrangement
   - Start the server
   
2. On your secondary machine:
   - Launch Barrier
   - Select "Client (use another computer's mouse and keyboard)"
   - Enter the server's IP address (e.g., 192.168.1.10)
   - Start the client

## Software Environment Setup

### Machine 1 (Mac Mini) Setup:

1. **Install Python and Dependencies**:
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python 3.11
   brew install python@3.11
   
   # Install Miniconda
   brew install --cask miniconda
   
   # Initialize conda
   conda init zsh  # or bash if you use bash
   
   # Create virtual environment
   conda create -n performance-suite python=3.11
   
   # Activate environment
   conda activate performance-suite
   
   # Clone repository (if not already done)
   git clone https://github.com/SplinteredSunlight/PerformanceSuite.git
   cd PerformanceSuite
   
   # Install project dependencies
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Configure Audio Interface**:
   - Install PreSonus Universal Control software from the PreSonus website
   - Connect the Quantum 2626 via Thunderbolt
   - Open Universal Control and configure:
     - Sample Rate: 96kHz
     - Buffer Size: 32-64 samples
     - Bit Depth: 24-bit

### Machine 2 (Mac Studio) Setup:

1. **Install Required Software**:
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python 3.11 (for utilities)
   brew install python@3.11
   
   # Clone repository (if not already done)
   git clone https://github.com/SplinteredSunlight/PerformanceSuite.git
   cd PerformanceSuite
   
   # Install minimal dependencies
   pip install python-osc
   ```

2. **Install Game Engine**:
   - Download and install your chosen game engine (Godot/Unity/Unreal)
   - Configure for high-performance rendering:
     - Target frame rate: 60fps minimum
     - Graphics settings optimized for performance

## Testing the Setup

1. **Test Network Communication**:
   - On Machine 1, run the OSC test script:
     ```bash
     python scripts/test_osc_sender.py --ip 192.168.1.20 --port 5000
     ```
   - On Machine 2, run the OSC receiver script:
     ```bash
     python scripts/test_osc_receiver.py --port 5000
     ```
   - Verify messages are being received with minimal latency

2. **Test Keyboard/Mouse Sharing**:
   - Move your cursor to the edge of the screen to transition between machines
   - Verify that keyboard input works on both machines

3. **Test Audio Interface**:
   - Play audio through the Quantum 2626
   - Run the audio analysis test script:
     ```bash
     python scripts/test_audio_analysis.py
     ```
   - Verify that audio is being properly captured and analyzed

## Troubleshooting

### Network Issues:
- Ensure both machines have the correct static IP configuration
- Try a different Ethernet cable
- Check network settings for any firewall issues

### Universal Control Issues:
- Ensure both machines are signed in to the same Apple ID
- Verify Bluetooth and Wi-Fi are enabled on both machines
- Restart both machines

### Audio Interface Issues:
- Update to the latest PreSonus drivers
- Try different buffer size settings
- Check Thunderbolt connection

## Remote Setup for Mac Studio

If you haven't yet set up the Mac Studio and only have the Mac Mini configured, you can use the remote setup script to configure the Mac Studio over the network:

1. **Enable Remote Login on Mac Studio**:
   - On the Mac Studio, go to System Settings > Sharing
   - Enable "Remote Login" to allow SSH access

2. **Run the Remote Setup Script**:
   ```bash
   # On the Mac Mini
   cd PerformanceSuite
   python scripts/setup_mac_studio_remote.py --username <your-mac-studio-username>
   ```
   - Enter your Mac Studio password when prompted
   - The script will install Homebrew, Python, clone the repository, and start the remote control server

3. **Verify the Setup**:
   ```bash
   # On the Mac Mini
   python scripts/test_remote_control.py
   ```
   - This will test the connection to the Mac Studio and verify that the remote control server is working

## Remote Control Setup

The Performance Suite includes a remote control system that allows you to control the Mac Studio (Machine 2) directly from the Mac Mini (Machine 1) without needing to switch keyboards or displays.

### Setting Up Remote Control

1. **Install Required Dependencies**:
   ```bash
   pip install paramiko  # For SSH functionality
   ```

2. **Start the Remote Control Server on Machine 2 (Mac Studio)**:
   ```bash
   # On the Mac Studio
   cd PerformanceSuite
   python scripts/remote_control_mcp.py --port 5000
   ```

3. **Start the Remote Control Client on Machine 1 (Mac Mini)**:
   ```bash
   # On the Mac Mini
   cd PerformanceSuite
   python scripts/remote_control_client.py
   ```

4. **Using Remote Control with Roo**:
   Once the server and client are running, you can use the following MCP tools in Roo:

   - Execute a command on the Mac Studio:
     ```
     remote_execute:
       command: "python3 scripts/test_osc_receiver.py --port 5000"
     ```

   - Transfer a file to the Mac Studio:
     ```
     remote_transfer:
       source: "src/config.py"
       destination: "src/config.py"
       direction: "send"
     ```

   - Get system status from the Mac Studio:
     ```
     remote_status:
       type: "system"  # or "network"
     ```

## Next Steps

Once your environment is set up, you can proceed with:
1. Implementing the audio analysis pipeline
2. Developing the agent system
3. Setting up the rendering pipeline
4. Integrating all components

Refer to the Phase 1 Implementation Plan for detailed steps on each of these components.