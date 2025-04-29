#!/usr/bin/env python3
"""
Remote Control Test Script

This script tests the remote control functionality between the Mac Mini and Mac Studio.
It performs basic tests to verify that the connection works properly.

Usage:
    On the Mac Mini:
        python scripts/test_remote_control.py
"""

import os
import sys
import socket
import json
import time
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Default settings
DEFAULT_HOST = "192.168.1.20"  # Mac Studio IP
DEFAULT_PORT = 5000
TEST_FILE_NAME = "remote_control_test.txt"

def create_test_file():
    """Create a test file to transfer."""
    test_file_path = project_root / TEST_FILE_NAME
    with open(test_file_path, 'w') as f:
        f.write(f"Remote control test file\nCreated at: {time.ctime()}\n")
    return test_file_path

def test_connection(host, port):
    """Test basic connection to the remote server."""
    print(f"Testing connection to {host}:{port}...")
    try:
        # Create a socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        s.close()
        print("✅ Connection successful!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def send_request(host, port, tool, params):
    """Send a request to the remote server and return the response."""
    try:
        # Create the request
        request = {
            "tool": tool,
            "params": params
        }
        
        # Create a socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((host, port))
        
        # Send the request
        s.sendall(json.dumps(request).encode('utf-8'))
        
        # Receive the response
        data = b""
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                
                # Check if we have a complete JSON message
                try:
                    json.loads(data.decode('utf-8'))
                    break
                except:
                    continue
            except socket.timeout:
                break
        
        # Close the connection
        s.close()
        
        # Parse the response
        if data:
            return json.loads(data.decode('utf-8'))
        else:
            return {"status": "error", "message": "No response received"}
    except Exception as e:
        return {"status": "error", "message": f"Error sending request: {str(e)}"}

def test_remote_execute(host, port):
    """Test executing a command on the remote machine."""
    print("\nTesting remote command execution...")
    response = send_request(host, port, "remote_execute", {
        "command": "echo 'Hello from remote machine'"
    })
    
    if response.get("status") == "success":
        stdout = response.get("data", {}).get("stdout", "").strip()
        if stdout == "Hello from remote machine":
            print(f"✅ Remote execution successful: {stdout}")
            return True
        else:
            print(f"❌ Remote execution returned unexpected output: {stdout}")
            return False
    else:
        print(f"❌ Remote execution failed: {response.get('message')}")
        return False

def test_remote_transfer(host, port):
    """Test transferring a file to and from the remote machine."""
    print("\nTesting file transfer...")
    
    # Create a test file
    test_file_path = create_test_file()
    remote_file_path = f"/tmp/{TEST_FILE_NAME}"
    
    # Read the test file
    with open(test_file_path, 'rb') as f:
        file_content = f.read()
    
    # Encode the content as base64
    import base64
    encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    # Send the file to the remote machine
    print("Sending file to remote machine...")
    response = send_request(host, port, "remote_transfer", {
        "source": str(test_file_path),
        "destination": remote_file_path,
        "direction": "send",
        "content": encoded_content
    })
    
    if response.get("status") != "success":
        print(f"❌ File transfer to remote failed: {response.get('message')}")
        return False
    
    print("✅ File transfer to remote successful")
    
    # Get the file back from the remote machine
    print("Retrieving file from remote machine...")
    response = send_request(host, port, "remote_transfer", {
        "source": remote_file_path,
        "destination": str(test_file_path) + ".received",
        "direction": "receive"
    })
    
    if response.get("status") != "success":
        print(f"❌ File transfer from remote failed: {response.get('message')}")
        return False
    
    # Decode the content
    encoded_content = response.get("data", {}).get("content")
    if not encoded_content:
        print("❌ No file content received")
        return False
    
    received_content = base64.b64decode(encoded_content)
    
    # Write the received file
    with open(str(test_file_path) + ".received", 'wb') as f:
        f.write(received_content)
    
    print("✅ File transfer from remote successful")
    
    # Compare the files
    if file_content == received_content:
        print("✅ File contents match")
        return True
    else:
        print("❌ File contents do not match")
        return False

def test_remote_status(host, port):
    """Test getting status from the remote machine."""
    print("\nTesting remote status...")
    response = send_request(host, port, "remote_status", {
        "type": "system"
    })
    
    if response.get("status") == "success":
        data = response.get("data", {})
        if "uptime" in data and "hostname" in data:
            print(f"✅ Remote status successful")
            print(f"  Hostname: {data.get('hostname')}")
            print(f"  Uptime: {data.get('uptime')}")
            return True
        else:
            print(f"❌ Remote status missing expected data")
            return False
    else:
        print(f"❌ Remote status failed: {response.get('message')}")
        return False

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test the remote control functionality")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Remote host to connect to")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Remote port to connect to")
    args = parser.parse_args()
    
    print("=== Remote Control Test ===")
    print(f"Target: {args.host}:{args.port}")
    
    # Run the tests
    connection_ok = test_connection(args.host, args.port)
    if not connection_ok:
        print("\n❌ Connection test failed. Cannot proceed with other tests.")
        return 1
    
    execute_ok = test_remote_execute(args.host, args.port)
    transfer_ok = test_remote_transfer(args.host, args.port)
    status_ok = test_remote_status(args.host, args.port)
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Connection: {'✅ Pass' if connection_ok else '❌ Fail'}")
    print(f"Command Execution: {'✅ Pass' if execute_ok else '❌ Fail'}")
    print(f"File Transfer: {'✅ Pass' if transfer_ok else '❌ Fail'}")
    print(f"Status Check: {'✅ Pass' if status_ok else '❌ Fail'}")
    
    # Clean up test files
    try:
        os.remove(project_root / TEST_FILE_NAME)
        os.remove(project_root / f"{TEST_FILE_NAME}.received")
    except:
        pass
    
    # Return success if all tests passed
    if connection_ok and execute_ok and transfer_ok and status_ok:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())