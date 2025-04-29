# Remote Control MCP System

This directory contains scripts for the Remote Control MCP system, which allows controlling the Mac Studio (Machine 2) from the Mac Mini (Machine 1) without needing to switch keyboards or displays.

## Overview

The Remote Control MCP system consists of two main components:

1. **Server (`remote_control_mcp.py`)**: Runs on the Mac Studio and listens for commands.
2. **Client (`remote_control_client.py`)**: Runs on the Mac Mini and sends commands to the server.

This system enables seamless control of the Mac Studio from the Mac Mini, allowing you to execute commands, transfer files, and check system status remotely.

## Setup

### Prerequisites

- Both machines must be connected via Ethernet with static IP addresses configured
- Python 3.11+ installed on both machines
- The `paramiko` library installed for SSH functionality

### Starting the Server

On the Mac Studio (Machine 2):

```bash
cd PerformanceSuite
python scripts/remote_control_mcp.py --port 5000
```

### Starting the Client

On the Mac Mini (Machine 1):

```bash
cd PerformanceSuite
python scripts/remote_control_client.py
```

## Usage with Roo

Once the server and client are running, you can use the following MCP tools in Roo:

### Execute a Command on the Mac Studio

```
remote_execute:
  command: "python3 scripts/test_osc_receiver.py --port 5000"
  cwd: "/path/to/working/directory"  # Optional
```

### Transfer a File to the Mac Studio

```
remote_transfer:
  source: "src/config.py"
  destination: "src/config.py"
  direction: "send"
```

### Transfer a File from the Mac Studio

```
remote_transfer:
  source: "src/config.py"
  destination: "src/config.py"
  direction: "receive"
```

### Get System Status from the Mac Studio

```
remote_status:
  type: "system"  # or "network"
```

## Security Considerations

- The server listens on all interfaces by default, so ensure your network is secure
- Consider implementing authentication if using in a less secure environment
- The system uses direct socket connections rather than SSH for simplicity and performance

## Troubleshooting

### Connection Issues

- Verify that both machines are on and connected to the network
- Check that the server is running on the Mac Studio
- Ensure the correct IP address and port are configured
- Check for any firewall settings that might block the connection

### Command Execution Problems

- Verify that the command exists on the Mac Studio
- Check that the working directory is valid
- Examine the error output for specific issues

## Advanced Configuration

Both the server and client accept command-line arguments to customize their behavior:

### Server Options

- `--host`: Host to listen on (default: 0.0.0.0)
- `--port`: Port to listen on (default: 5000)

### Client Options

- `--host`: Remote host to connect to (default: 192.168.1.20)
- `--port`: Remote port to connect to (default: 5000)