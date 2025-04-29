#!/usr/bin/env python3
"""
Remote Control MCP Server

This script provides an MCP server for controlling a remote Mac machine.
It allows executing commands, transferring files, and checking status remotely.

Usage:
    On the remote machine (Mac Studio):
        python3 scripts/remote_control_mcp.py

    This will start the server listening on port 5000 by default.
"""

import json
import sys
import os
import subprocess
import socket
import threading
import base64
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Constants
DEFAULT_PORT = 5000
DEFAULT_HOST = "0.0.0.0"  # Listen on all interfaces
MAX_BUFFER_SIZE = 1024 * 1024 * 10  # 10MB max buffer size

class RemoteControlServer:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []
        
    def start(self):
        """Start the remote control server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(json.dumps({"status": "ready", "message": f"Server listening on {self.host}:{self.port}"}))
            sys.stdout.flush()
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                    client_thread.daemon = True
                    client_thread.start()
                    self.clients.append((client_socket, addr, client_thread))
                except Exception as e:
                    if self.running:
                        print(json.dumps({"status": "error", "message": f"Error accepting connection: {str(e)}"}))
                        sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"Server error: {str(e)}"}))
            sys.stdout.flush()
        finally:
            self.stop()
    
    def stop(self):
        """Stop the remote control server."""
        self.running = False
        
        # Close all client connections
        for client_socket, _, _ in self.clients:
            try:
                client_socket.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
    
    def handle_client(self, client_socket, addr):
        """Handle a client connection."""
        try:
            # Receive data from client
            data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(data) > MAX_BUFFER_SIZE:
                    raise ValueError("Data exceeds maximum buffer size")
                
                # Check if we have a complete JSON message
                try:
                    # Try to decode as JSON to see if it's complete
                    json.loads(data.decode('utf-8'))
                    break
                except:
                    # Not complete yet, continue receiving
                    continue
            
            if not data:
                return
            
            # Parse the request
            request = json.loads(data.decode('utf-8'))
            tool_name = request.get("tool")
            params = request.get("params", {})
            
            # Process the request
            response = self.process_request(tool_name, params)
            
            # Send the response
            client_socket.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            error_response = {
                "status": "error",
                "message": f"Error handling client request: {str(e)}"
            }
            try:
                client_socket.sendall(json.dumps(error_response).encode('utf-8'))
            except:
                pass
        finally:
            client_socket.close()
    
    def process_request(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a client request."""
        try:
            if tool_name == "remote_execute":
                return self.remote_execute(params)
            elif tool_name == "remote_transfer":
                return self.remote_transfer(params)
            elif tool_name == "remote_status":
                return self.remote_status(params)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown tool: {tool_name}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }
    
    def remote_execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command on the remote machine."""
        command = params.get("command")
        cwd = params.get("cwd", os.getcwd())
        
        if not command:
            return {
                "status": "error",
                "message": "Missing required parameter: command"
            }
        
        try:
            # Execute the command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd
            )
            stdout, stderr = process.communicate()
            
            return {
                "status": "success",
                "data": {
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": process.returncode
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error executing command: {str(e)}"
            }
    
    def remote_transfer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transfer a file to or from the remote machine."""
        source = params.get("source")
        destination = params.get("destination")
        direction = params.get("direction", "receive")  # "send" or "receive"
        content = params.get("content")  # Base64 encoded content for send operations
        
        if not source or not destination:
            return {
                "status": "error",
                "message": "Missing required parameters: source and destination"
            }
        
        try:
            if direction == "send":
                # Client is sending a file to us
                if not content:
                    return {
                        "status": "error",
                        "message": "Missing required parameter: content"
                    }
                
                # Decode the base64 content
                file_content = base64.b64decode(content)
                
                # Ensure the destination directory exists
                os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
                
                # Write the file
                with open(destination, 'wb') as f:
                    f.write(file_content)
                
                return {
                    "status": "success",
                    "data": {
                        "message": f"File received and saved to {destination}",
                        "size": len(file_content)
                    }
                }
            else:
                # Client is requesting a file from us
                if not os.path.exists(source):
                    return {
                        "status": "error",
                        "message": f"Source file not found: {source}"
                    }
                
                # Read the file
                with open(source, 'rb') as f:
                    file_content = f.read()
                
                # Encode the content as base64
                encoded_content = base64.b64encode(file_content).decode('utf-8')
                
                return {
                    "status": "success",
                    "data": {
                        "content": encoded_content,
                        "size": len(file_content)
                    }
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error transferring file: {str(e)}"
            }
    
    def remote_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get status information from the remote machine."""
        status_type = params.get("type", "system")
        
        try:
            if status_type == "system":
                # Get system information
                uptime_process = subprocess.Popen(["uptime"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                uptime_output, _ = uptime_process.communicate()
                
                df_process = subprocess.Popen(["df", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                df_output, _ = df_process.communicate()
                
                ps_process = subprocess.Popen(["ps", "aux", "|", "head", "-10"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
                ps_output, _ = ps_process.communicate()
                
                return {
                    "status": "success",
                    "data": {
                        "uptime": uptime_output.strip(),
                        "disk_usage": df_output.strip(),
                        "processes": ps_output.strip(),
                        "hostname": socket.gethostname(),
                        "ip_address": socket.gethostbyname(socket.gethostname())
                    }
                }
            elif status_type == "network":
                # Get network information
                netstat_process = subprocess.Popen(["netstat", "-an"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                netstat_output, _ = netstat_process.communicate()
                
                return {
                    "status": "success",
                    "data": {
                        "netstat": netstat_output.strip()
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown status type: {status_type}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting status: {str(e)}"
            }

def main():
    """Main entry point for the MCP server."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Remote Control MCP Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to listen on")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on")
    args = parser.parse_args()
    
    # Start the server
    server = RemoteControlServer(args.host, args.port)
    server.start()

if __name__ == "__main__":
    main()