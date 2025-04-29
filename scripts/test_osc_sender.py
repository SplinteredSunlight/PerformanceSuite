#!/usr/bin/env python3
"""
OSC Sender Test Script for Performance Suite

This script sends test OSC messages to verify network connectivity between machines.
It's used to test the network setup for the Performance Suite two-machine architecture.

Usage:
    python test_osc_sender.py --ip 192.168.1.20 --port 8000
"""

import argparse
import time
from pythonosc import udp_client
import random

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Send test OSC messages")
    parser.add_argument("--ip", default="192.168.1.20", help="The IP address to send to")
    parser.add_argument("--port", type=int, default=8000, help="The port to send to")
    parser.add_argument("--interval", type=float, default=0.1, help="Interval between messages (seconds)")
    parser.add_argument("--count", type=int, default=100, help="Number of messages to send")
    return parser.parse_args()

def main():
    """Main function to send test OSC messages."""
    args = parse_args()
    
    # Create OSC client
    client = udp_client.SimpleUDPClient(args.ip, args.port)
    
    print(f"Sending {args.count} OSC messages to {args.ip}:{args.port} at {args.interval}s intervals")
    print("Press Ctrl+C to stop")
    
    try:
        for i in range(args.count):
            # Send a test message with timestamp and random values
            timestamp = time.time()
            value = random.random()
            
            # Send different types of test messages
            client.send_message("/test/timestamp", timestamp)
            client.send_message("/test/random", value)
            client.send_message("/test/counter", i)
            
            # Send a simulated animation control message
            if i % 10 == 0:
                client.send_message("/animation/trigger", "drum_hit")
            elif i % 10 == 5:
                client.send_message("/animation/trigger", "bass_note")
            
            # Print status
            print(f"Sent message {i+1}/{args.count}: timestamp={timestamp:.6f}, value={value:.6f}")
            
            # Wait for the specified interval
            time.sleep(args.interval)
            
        print("All messages sent successfully")
        
    except KeyboardInterrupt:
        print("\nSending stopped by user")
    except Exception as e:
        print(f"Error sending messages: {e}")

if __name__ == "__main__":
    main()