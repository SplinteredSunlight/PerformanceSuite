#!/usr/bin/env python3
"""
Mac Studio Discovery Script

This script helps discover the Mac Studio on the network and find available usernames.
It uses SSH to attempt to connect to the Mac Studio and list available users.

Usage:
    python scripts/discover_mac_studio.py
"""

import os
import sys
import subprocess
import socket
import time
from pathlib import Path

# Default settings
MAC_STUDIO_IP = "192.168.1.20"
MAC_STUDIO_SSH_PORT = 22

def check_ping(ip):
    """Check if the Mac Studio is reachable via ping."""
    print(f"Pinging {ip}...")
    
    try:
        # Use ping with a timeout of 2 seconds and 3 packets
        result = subprocess.run(
            ["ping", "-c", "3", "-W", "2", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ {ip} is reachable!")
            return True
        else:
            print(f"❌ {ip} is not reachable.")
            return False
    except Exception as e:
        print(f"❌ Error pinging {ip}: {str(e)}")
        return False

def check_ssh_port(ip, port=MAC_STUDIO_SSH_PORT):
    """Check if SSH port is open on the Mac Studio."""
    print(f"Checking if SSH port {port} is open on {ip}...")
    
    try:
        # Create a socket connection to check if the port is open
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex((ip, port))
        s.close()
        
        if result == 0:
            print(f"✅ SSH port {port} is open on {ip}!")
            return True
        else:
            print(f"❌ SSH port {port} is not open on {ip}.")
            return False
    except Exception as e:
        print(f"❌ Error checking SSH port on {ip}: {str(e)}")
        return False

def get_ssh_banner(ip, port=MAC_STUDIO_SSH_PORT):
    """Get the SSH banner to extract information about the server."""
    print(f"Getting SSH banner from {ip}...")
    
    try:
        # Use netcat to get the SSH banner
        result = subprocess.run(
            ["nc", "-v", "-w", "5", ip, str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            input="\n"
        )
        
        # Extract the banner from stderr (netcat outputs connection info to stderr)
        banner = result.stderr
        if "SSH" in banner:
            print(f"✅ SSH banner received: {banner.strip()}")
            return banner
        else:
            print(f"❌ No SSH banner received from {ip}.")
            return None
    except Exception as e:
        print(f"❌ Error getting SSH banner from {ip}: {str(e)}")
        return None

def try_common_usernames(ip, port=MAC_STUDIO_SSH_PORT):
    """Try to find valid usernames on the Mac Studio."""
    print(f"Trying to find valid usernames on {ip}...")
    
    # Common macOS usernames to try
    common_usernames = [
        "admin", "administrator", "root", "user", "macuser", "macadmin", 
        "studio", "macstudio", "mac", "apple", "macos", "owner"
    ]
    
    valid_usernames = []
    
    for username in common_usernames:
        print(f"Checking username: {username}")
        
        try:
            # Use SSH with a timeout to check if the username exists
            # The -o BatchMode=yes option prevents password prompt
            result = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", 
                 "-o", "ConnectTimeout=5", f"{username}@{ip}", "echo", "Connection successful"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            # Check the error message to determine if the username exists
            if "Connection successful" in result.stdout:
                print(f"✅ Username '{username}' exists and login succeeded (unlikely without password).")
                valid_usernames.append(username)
            elif "Permission denied" in result.stderr:
                print(f"✅ Username '{username}' likely exists (permission denied).")
                valid_usernames.append(username)
            else:
                print(f"❌ Username '{username}' might not exist.")
        except Exception as e:
            print(f"❌ Error checking username '{username}': {str(e)}")
    
    return valid_usernames

def get_hostname(ip):
    """Try to get the hostname of the Mac Studio."""
    print(f"Trying to get hostname of {ip}...")
    
    try:
        # Use the host command to perform a reverse DNS lookup
        result = subprocess.run(
            ["host", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if "domain name pointer" in result.stdout:
            hostname = result.stdout.split("domain name pointer")[1].strip().rstrip(".")
            print(f"✅ Hostname: {hostname}")
            return hostname
        else:
            print(f"❌ Could not determine hostname for {ip}.")
            return None
    except Exception as e:
        print(f"❌ Error getting hostname for {ip}: {str(e)}")
        return None

def main():
    """Main entry point for the script."""
    print("=== Mac Studio Discovery ===\n")
    
    # Check if the Mac Studio is reachable
    if not check_ping(MAC_STUDIO_IP):
        print("\nPlease make sure:")
        print("1. The Mac Studio is powered on")
        print("2. The Mac Studio is connected via Ethernet")
        print("3. The Mac Studio has the correct IP address (192.168.1.20)")
        return 1
    
    # Check if SSH port is open
    if not check_ssh_port(MAC_STUDIO_IP):
        print("\nPlease make sure:")
        print("1. Remote Login is enabled on the Mac Studio (System Settings > Sharing > Remote Login)")
        return 1
    
    # Get the SSH banner
    banner = get_ssh_banner(MAC_STUDIO_IP)
    
    # Get the hostname
    hostname = get_hostname(MAC_STUDIO_IP)
    
    # Try to find valid usernames
    valid_usernames = try_common_usernames(MAC_STUDIO_IP)
    
    # Print summary
    print("\n=== Discovery Summary ===")
    print(f"Mac Studio IP: {MAC_STUDIO_IP}")
    if hostname:
        print(f"Hostname: {hostname}")
    if banner:
        print(f"SSH Banner: {banner.strip()}")
    
    if valid_usernames:
        print("\nPossible usernames:")
        for username in valid_usernames:
            print(f"- {username}")
        
        print("\nTo set up the Mac Studio remotely, run:")
        print(f"python scripts/setup_mac_studio_remote.py --username <username>")
        print("\nReplace <username> with one of the usernames listed above.")
    else:
        print("\nNo valid usernames found. You'll need to provide the correct username.")
        print("\nTo set up the Mac Studio remotely, run:")
        print(f"python scripts/setup_mac_studio_remote.py --username <username>")
        print("\nReplace <username> with the correct username for your Mac Studio.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())