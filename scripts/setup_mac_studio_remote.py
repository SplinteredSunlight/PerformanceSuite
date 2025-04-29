#!/usr/bin/env python3
"""
Mac Studio Remote Setup Script

This script helps set up the Mac Studio remotely from the Mac Mini using SSH.
It handles the initial environment setup, including installing Homebrew, Python,
and cloning the repository.

Prerequisites:
- SSH must be enabled on the Mac Studio (System Settings > Sharing > Remote Login)
- The Mac Studio must be connected via Ethernet with IP 192.168.1.20
- You must know the username and password for the Mac Studio

Usage:
    python scripts/setup_mac_studio_remote.py --username <username>
"""

import os
import sys
import argparse
import getpass
import subprocess
import time
from pathlib import Path

# Default settings
MAC_STUDIO_IP = "192.168.1.20"
MAC_STUDIO_SSH_PORT = 22
REPO_URL = "https://github.com/SplinteredSunlight/PerformanceSuite.git"

def run_ssh_command(username, password, command, ip=MAC_STUDIO_IP, port=MAC_STUDIO_SSH_PORT):
    """Run a command on the remote machine via SSH."""
    # Use sshpass to provide the password non-interactively
    full_command = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -p {port} {username}@{ip} '{command}'"
    
    try:
        result = subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_ssh_connection(username, password, ip=MAC_STUDIO_IP, port=MAC_STUDIO_SSH_PORT):
    """Check if SSH connection to the Mac Studio is working."""
    print(f"Checking SSH connection to {ip}...")
    
    try:
        result = run_ssh_command(username, password, "echo 'SSH connection successful'")
        if result and "SSH connection successful" in result:
            print("✅ SSH connection successful!")
            return True
        else:
            print("❌ SSH connection failed.")
            return False
    except Exception as e:
        print(f"❌ SSH connection failed: {str(e)}")
        return False

def install_sshpass():
    """Install sshpass on the Mac Mini if not already installed."""
    print("Checking if sshpass is installed...")
    
    try:
        subprocess.run(["which", "sshpass"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ sshpass is already installed.")
        return True
    except subprocess.CalledProcessError:
        print("sshpass not found. Installing...")
        
        try:
            # Check if Homebrew is installed
            subprocess.run(["which", "brew"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Install sshpass using Homebrew
            subprocess.run(["brew", "install", "hudochenkov/sshpass/sshpass"], check=True)
            print("✅ sshpass installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install sshpass: {str(e)}")
            print("Please install Homebrew and sshpass manually:")
            print("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("  brew install hudochenkov/sshpass/sshpass")
            return False

def setup_mac_studio(username, password):
    """Set up the Mac Studio environment."""
    print("\n=== Setting up Mac Studio environment ===\n")
    
    # Check if Homebrew is installed
    print("Checking if Homebrew is installed on Mac Studio...")
    brew_check = run_ssh_command(username, password, "which brew || echo 'not installed'")
    
    if brew_check and "not installed" in brew_check:
        print("Installing Homebrew on Mac Studio...")
        install_cmd = 'bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        run_ssh_command(username, password, install_cmd)
        
        # Add Homebrew to PATH
        print("Adding Homebrew to PATH...")
        if "arm64" in run_ssh_command(username, password, "uname -m"):
            # For Apple Silicon Macs
            run_ssh_command(username, password, 'echo \'eval "$(/opt/homebrew/bin/brew shellenv)"\' >> ~/.zprofile')
            run_ssh_command(username, password, 'eval "$(/opt/homebrew/bin/brew shellenv)"')
        else:
            # For Intel Macs
            run_ssh_command(username, password, 'echo \'eval "$(/usr/local/bin/brew shellenv)"\' >> ~/.zprofile')
            run_ssh_command(username, password, 'eval "$(/usr/local/bin/brew shellenv)"')
    else:
        print("✅ Homebrew is already installed on Mac Studio.")
    
    # Install Python 3.11
    print("\nInstalling Python 3.11 on Mac Studio...")
    run_ssh_command(username, password, "brew install python@3.11")
    
    # Install Miniconda
    print("\nInstalling Miniconda on Mac Studio...")
    run_ssh_command(username, password, "brew install --cask miniconda")
    
    # Initialize conda
    print("\nInitializing conda on Mac Studio...")
    run_ssh_command(username, password, "conda init zsh")
    
    # Create conda environment
    print("\nCreating conda environment on Mac Studio...")
    run_ssh_command(username, password, "conda create -y -n performance-suite python=3.11")
    
    # Clone repository
    print("\nCloning repository on Mac Studio...")
    run_ssh_command(username, password, f"git clone {REPO_URL} ~/PerformanceSuite")
    
    # Install dependencies
    print("\nInstalling dependencies on Mac Studio...")
    run_ssh_command(username, password, "cd ~/PerformanceSuite && pip install python-osc paramiko")
    
    # Copy remote control server script to a standalone location
    print("\nSetting up remote control server...")
    run_ssh_command(username, password, "mkdir -p ~/bin")
    run_ssh_command(username, password, "cp ~/PerformanceSuite/scripts/remote_control_mcp.py ~/bin/")
    run_ssh_command(username, password, "chmod +x ~/bin/remote_control_mcp.py")
    
    # Create a startup script for the remote control server
    print("\nCreating startup script for remote control server...")
    startup_script = """#!/bin/bash
cd ~/PerformanceSuite
python scripts/remote_control_mcp.py --port 5000
"""
    run_ssh_command(username, password, f"echo '{startup_script}' > ~/bin/start_remote_control.sh")
    run_ssh_command(username, password, "chmod +x ~/bin/start_remote_control.sh")
    
    # Start the remote control server
    print("\nStarting remote control server on Mac Studio...")
    run_ssh_command(username, password, "nohup ~/bin/start_remote_control.sh > ~/remote_control.log 2>&1 &")
    
    print("\n✅ Mac Studio environment setup complete!")
    print("\nThe remote control server is now running on the Mac Studio.")
    print("You can now use the remote control client on the Mac Mini to control the Mac Studio.")
    print("\nTo test the connection, run:")
    print("  python scripts/test_remote_control.py")
    
    return True

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Set up the Mac Studio environment remotely")
    parser.add_argument("--username", required=True, help="Username for the Mac Studio")
    parser.add_argument("--ip", default=MAC_STUDIO_IP, help=f"IP address of the Mac Studio (default: {MAC_STUDIO_IP})")
    args = parser.parse_args()
    
    # Get the password securely
    password = getpass.getpass(f"Enter password for {args.username}@{args.ip}: ")
    
    # Install sshpass on the Mac Mini
    if not install_sshpass():
        return 1
    
    # Check SSH connection
    if not check_ssh_connection(args.username, password, args.ip):
        print("\nPlease make sure:")
        print("1. Remote Login is enabled on the Mac Studio (System Settings > Sharing > Remote Login)")
        print("2. The Mac Studio is connected via Ethernet with IP 192.168.1.20")
        print("3. The username and password are correct")
        return 1
    
    # Set up the Mac Studio environment
    setup_mac_studio(args.username, password)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())