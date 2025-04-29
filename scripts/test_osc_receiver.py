#!/usr/bin/env python3
"""
OSC Receiver Test Script for Performance Suite

This script receives and displays OSC messages to verify network connectivity between machines.
It's used to test the network setup for the Performance Suite two-machine architecture.

Usage:
    python test_osc_receiver.py --port 8000
"""

import argparse
import time
from pythonosc import dispatcher
from pythonosc import osc_server
import threading

# Global variables to track statistics
message_count = 0
start_time = None
last_timestamp = None
latencies = []

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Receive test OSC messages")
    parser.add_argument("--ip", default="0.0.0.0", help="The IP to listen on (0.0.0.0 for all interfaces)")
    parser.add_argument("--port", type=int, default=8000, help="The port to listen on")
    return parser.parse_args()

def generic_handler(address, *args):
    """Generic handler for all OSC messages."""
    global message_count, start_time, last_timestamp, latencies
    
    # Initialize start time if this is the first message
    if start_time is None:
        start_time = time.time()
    
    # Calculate time since last message
    current_time = time.time()
    if last_timestamp is not None:
        interval = current_time - last_timestamp
        latencies.append(interval)
    last_timestamp = current_time
    
    # Increment message count
    message_count += 1
    
    # Print message details
    print(f"Received message #{message_count}: {address} {args}")
    
    # Print statistics every 10 messages
    if message_count % 10 == 0:
        print_statistics()

def animation_trigger_handler(address, *args):
    """Special handler for animation trigger messages."""
    print(f"\n>>> ANIMATION TRIGGER: {args[0]} <<<\n")
    # Call the generic handler to maintain statistics
    generic_handler(address, *args)

def print_statistics():
    """Print statistics about received messages."""
    global message_count, start_time, latencies
    
    if start_time is None or message_count == 0:
        return
    
    elapsed_time = time.time() - start_time
    messages_per_second = message_count / elapsed_time
    
    print("\n--- Statistics ---")
    print(f"Messages received: {message_count}")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Messages per second: {messages_per_second:.2f}")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        print(f"Average interval between messages: {avg_latency*1000:.2f} ms")
        print(f"Min interval: {min_latency*1000:.2f} ms")
        print(f"Max interval: {max_latency*1000:.2f} ms")
    
    print("------------------\n")

def main():
    """Main function to receive OSC messages."""
    args = parse_args()
    
    # Create dispatcher
    disp = dispatcher.Dispatcher()
    
    # Register special handlers for specific addresses
    disp.map("/animation/trigger", animation_trigger_handler)
    
    # Register a generic handler for all other addresses
    disp.set_default_handler(generic_handler)
    
    # Create server
    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), disp)
    
    print(f"Listening for OSC messages on {args.ip}:{args.port}")
    print("Press Ctrl+C to stop")
    
    # Start a thread to periodically print statistics
    def stats_thread():
        while True:
            time.sleep(5)
            print_statistics()
    
    threading.Thread(target=stats_thread, daemon=True).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        print_statistics()
    except Exception as e:
        print(f"Error in server: {e}")

if __name__ == "__main__":
    main()