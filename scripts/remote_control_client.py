#!/usr/bin/env python3
"""
Remote Control MCP Client

This script provides an MCP client for controlling a remote Mac machine.
It connects to the remote_control_mcp.py server running on the remote machine.

Usage:
    On the local machine (Mac Mini):
        python3 scripts/remote_control_client.py

This will start the MCP client that communicates with Roo and forwards
requests to the remote server.
"""

import json
import sys
import os
import socket
import base64
from typing import Dict, List, Optional, Any, Tuple

# Constants
DEFAULT_REMOTE_HOST = "192.168.1.20"  # Mac Studio IP
DEFAULT_REMOTE_PORT = 5000

class RemoteControlClient:
    def __init__(self, remote_host: str = DEFAULT_REMOTE_HOST, remote_port: int = DEFAULT_REMOTE_PORT):
        self.remote_host = remote_host
        self.remote_port = remote_port
    
    def connect(self) -> socket.socket:
        """Connect to the remote server."""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.remote_host, self.remote_port))
        return client_socket
    
    def send_request(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the remote server."""
        try:
            # Create the request
            request = {
                "tool": tool_name,
                "params": params
            }
            
            # Connect to the server
            client_socket = self.connect()
            
            # Send the request
            client_socket.sendall(json.dumps(request).encode('utf-8'))
            
            # Receive the response
            data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                
                # Check if we have a complete JSON message
                try:
                    # Try to decode as JSON to see if it's complete
                    json.loads(data.decode('utf-8'))
                    break
                except:
                    # Not complete yet, continue receiving
                    continue
            
            # Parse the response
            response = json.loads(data.decode('utf-8'))
            
            # Close the connection
            client_socket.close()
            
            return response
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error sending request: {str(e)}"
            }
    
    def remote_execute(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """Execute a command on the remote machine."""
        params = {
            "command": command
        }
        
        if cwd:
            params["cwd"] = cwd
        
        return self.send_request("remote_execute", params)
    
    def remote_transfer_send(self, source: str, destination: str) -> Dict[str, Any]:
        """Send a file to the remote machine."""
        try:
            # Read the source file
            with open(source, 'rb') as f:
                file_content = f.read()
            
            # Encode the content as base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            # Create the params
            params = {
                "source": source,
                "destination": destination,
                "direction": "send",
                "content": encoded_content
            }
            
            return self.send_request("remote_transfer", params)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error sending file: {str(e)}"
            }
    
    def remote_transfer_receive(self, source: str, destination: str) -> Dict[str, Any]:
        """Receive a file from the remote machine."""
        try:
            # Create the params
            params = {
                "source": source,
                "destination": destination,
                "direction": "receive"
            }
            
            # Send the request
            response = self.send_request("remote_transfer", params)
            
            # Check if the request was successful
            if response.get("status") == "success":
                # Get the encoded content
                encoded_content = response.get("data", {}).get("content")
                
                if encoded_content:
                    # Decode the content
                    file_content = base64.b64decode(encoded_content)
                    
                    # Ensure the destination directory exists
                    os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
                    
                    # Write the file
                    with open(destination, 'wb') as f:
                        f.write(file_content)
                    
                    # Update the response message
                    response["data"]["message"] = f"File received and saved to {destination}"
            
            return response
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error receiving file: {str(e)}"
            }
    
    def remote_status(self, status_type: str = "system") -> Dict[str, Any]:
        """Get status information from the remote machine."""
        params = {
            "type": status_type
        }
        
        return self.send_request("remote_status", params)

def send_response(data: Any) -> None:
    """Send a response to the MCP client."""
    response = {
        "status": "success",
        "data": data
    }
    print(json.dumps(response))
    sys.stdout.flush()

def send_error(message: str) -> None:
    """Send an error response to the MCP client."""
    response = {
        "status": "error",
        "message": message
    }
    print(json.dumps(response))
    sys.stdout.flush()

def handle_request(request: Dict[str, Any]) -> None:
    """Handle an incoming MCP request."""
    try:
        tool_name = request.get("tool")
        params = request.get("params", {})
        
        # Create the client
        client = RemoteControlClient()
        
        if tool_name == "remote_execute":
            command = params.get("command")
            cwd = params.get("cwd")
            
            if not command:
                send_error("Missing required parameter: command")
                return
            
            result = client.remote_execute(command, cwd)
            send_response(result)
        
        elif tool_name == "remote_transfer":
            source = params.get("source")
            destination = params.get("destination")
            direction = params.get("direction", "send")  # "send" or "receive"
            
            if not source or not destination:
                send_error("Missing required parameters: source and destination")
                return
            
            if direction == "send":
                result = client.remote_transfer_send(source, destination)
            else:
                result = client.remote_transfer_receive(source, destination)
            
            send_response(result)
        
        elif tool_name == "remote_status":
            status_type = params.get("type", "system")
            
            result = client.remote_status(status_type)
            send_response(result)
        
        else:
            send_error(f"Unknown tool: {tool_name}")
    
    except Exception as e:
        send_error(f"Error handling request: {str(e)}")

def main() -> None:
    """Main entry point for the MCP client."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Remote Control MCP Client")
    parser.add_argument("--host", default=DEFAULT_REMOTE_HOST, help="Remote host to connect to")
    parser.add_argument("--port", type=int, default=DEFAULT_REMOTE_PORT, help="Remote port to connect to")
    args = parser.parse_args()
    
    # Send a startup message
    print(json.dumps({"status": "ready"}))
    sys.stdout.flush()
    
    # Process incoming requests
    for line in sys.stdin:
        try:
            request = json.loads(line)
            handle_request(request)
        except json.JSONDecodeError:
            send_error("Invalid JSON request")
        except Exception as e:
            send_error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()