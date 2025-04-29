#!/usr/bin/env python3
"""
Simple File Transfer Script

This script transfers files to the Mac Studio using scp.
It's a simpler approach than trying to create scripts directly on the Mac Studio.

Prerequisites:
- SSH must be enabled on the Mac Studio (System Settings > Sharing > Remote Login)
- The Mac Studio must be connected via Ethernet with IP 192.168.1.20
- You must know the username and password for the Mac Studio

Usage:
    python3 scripts/simple_file_transfer.py --username <username>
"""

import os
import sys
import argparse
import getpass
import subprocess
import tempfile
from pathlib import Path

# Default settings
MAC_STUDIO_IP = "192.168.1.20"

def run_command(command):
    """Run a command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_scp_installed():
    """Check if scp is installed."""
    print("Checking if scp is installed...")
    
    try:
        subprocess.run(["which", "scp"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ scp is installed.")
        return True
    except subprocess.CalledProcessError:
        print("❌ scp is not installed.")
        return False

def create_server_script():
    """Create a simple server script."""
    print("Creating server script...")
    
    server_script = """#!/usr/bin/env python3
import socket
import subprocess
import os
import sys
import json

# Server settings
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000

def run_command(command):
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        return {
            'stdout': stdout,
            'stderr': stderr,
            'returncode': process.returncode
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': str(e),
            'returncode': 1
        }

def main():
    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind the socket to the address and port
    server_socket.bind((HOST, PORT))
    
    # Listen for incoming connections
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")
    
    try:
        while True:
            # Accept a connection
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            
            # Receive data
            data = client_socket.recv(1024).decode('utf-8')
            
            if data:
                # Parse the command
                try:
                    command_data = json.loads(data)
                    command = command_data.get('command', '')
                    
                    if command:
                        # Run the command
                        result = run_command(command)
                        
                        # Send the result back to the client
                        client_socket.sendall(json.dumps(result).encode('utf-8'))
                    else:
                        client_socket.sendall(json.dumps({'error': 'No command provided'}).encode('utf-8'))
                except json.JSONDecodeError:
                    client_socket.sendall(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
            
            # Close the connection
            client_socket.close()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
"""
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(server_script)
        server_script_path = f.name
    
    return server_script_path

def create_startup_script():
    """Create a startup script."""
    print("Creating startup script...")
    
    startup_script = """#!/bin/bash
cd ~/remote_control
nohup python3 server.py > server.log 2>&1 &
echo "Server started"
"""
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(startup_script)
        startup_script_path = f.name
    
    return startup_script_path

def create_client_script():
    """Create a client script."""
    print("Creating client script...")
    
    client_script = """#!/usr/bin/env python3
import socket
import json
import sys

# Client settings
HOST = '192.168.1.20'  # Mac Studio IP
PORT = 5000

def send_command(command):
    # Create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server
        client_socket.connect((HOST, PORT))
        
        # Send the command
        command_data = json.dumps({'command': command})
        client_socket.sendall(command_data.encode('utf-8'))
        
        # Receive the response
        response = client_socket.recv(4096).decode('utf-8')
        
        # Parse the response
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            return {'error': 'Invalid response from server'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        # Close the connection
        client_socket.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 remote_client.py <command>")
        return
    
    command = ' '.join(sys.argv[1:])
    result = send_command(command)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print("Command output:")
        print(result.get('stdout', ''))
        if result.get('stderr'):
            print("Error output:")
            print(result.get('stderr'))
        print(f"Return code: {result.get('returncode', 0)}")

if __name__ == "__main__":
    main()
"""
    
    # Write to a file in the scripts directory
    client_script_path = "scripts/remote_client.py"
    with open(client_script_path, 'w') as f:
        f.write(client_script)
    
    # Make it executable
    os.chmod(client_script_path, 0o755)
    
    return client_script_path

def transfer_files(username, password):
    """Transfer files to the Mac Studio."""
    print("\n=== Transferring files to Mac Studio ===\n")
    
    # Create the scripts
    server_script_path = create_server_script()
    startup_script_path = create_startup_script()
    client_script_path = create_client_script()
    
    # Create the remote directory
    print("Creating remote directory...")
    run_command(f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {username}@{MAC_STUDIO_IP} 'mkdir -p ~/remote_control'")
    
    # Transfer the server script
    print("Transferring server script...")
    run_command(f"sshpass -p '{password}' scp -o StrictHostKeyChecking=no {server_script_path} {username}@{MAC_STUDIO_IP}:~/remote_control/server.py")
    
    # Transfer the startup script
    print("Transferring startup script...")
    run_command(f"sshpass -p '{password}' scp -o StrictHostKeyChecking=no {startup_script_path} {username}@{MAC_STUDIO_IP}:~/remote_control/start.sh")
    
    # Make the scripts executable
    print("Making scripts executable...")
    run_command(f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {username}@{MAC_STUDIO_IP} 'chmod +x ~/remote_control/server.py ~/remote_control/start.sh'")
    
    # Start the server
    print("Starting the server...")
    run_command(f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {username}@{MAC_STUDIO_IP} '~/remote_control/start.sh'")
    
    # Clean up temporary files
    os.unlink(server_script_path)
    os.unlink(startup_script_path)
    
    print("\n✅ File transfer complete!")
    print("\nThe server is now running on the Mac Studio.")
    print("You can use the client script to send commands to the Mac Studio:")
    print("  python3 scripts/remote_client.py <command>")
    print("\nFor example:")
    print("  python3 scripts/remote_client.py ls -la")
    print("  python3 scripts/remote_client.py uname -a")
    
    return True

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Transfer files to the Mac Studio")
    parser.add_argument("--username", required=True, help="Username for the Mac Studio")
    parser.add_argument("--ip", default=MAC_STUDIO_IP, help=f"IP address of the Mac Studio (default: {MAC_STUDIO_IP})")
    args = parser.parse_args()
    
    # Get the password securely
    password = getpass.getpass(f"Enter password for {args.username}@{args.ip}: ")
    
    # Check if scp is installed
    if not check_scp_installed():
        print("Please install scp to continue.")
        return 1
    
    # Transfer the files
    transfer_files(args.username, password)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())