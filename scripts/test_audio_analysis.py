#!/usr/bin/env python3
"""
Audio Analysis Test Script for Performance Suite

This script tests the audio interface and basic audio analysis functionality.
It captures audio from the Quantum 2626 interface and performs simple analysis.

Usage:
    python test_audio_analysis.py --device "Quantum" --duration 10
"""

import argparse
import time
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import queue

# Global variables
audio_queue = queue.Queue()
plot_data = np.zeros(1000)
fft_data = np.zeros(512)
rms_history = np.zeros(100)
detected_pitch = 0
detected_volume = 0

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test audio analysis functionality")
    parser.add_argument("--device", default="", help="Audio device name (partial match)")
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds (0 for continuous)")
    parser.add_argument("--sample-rate", type=int, default=48000, help="Sample rate")
    parser.add_argument("--block-size", type=int, default=1024, help="Block size")
    parser.add_argument("--channels", type=int, default=1, help="Number of channels to record")
    parser.add_argument("--no-plot", action="store_true", help="Disable plotting")
    return parser.parse_args()

def list_audio_devices():
    """List available audio devices."""
    print("\nAvailable audio devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']} (Inputs: {device['max_input_channels']}, Outputs: {device['max_output_channels']})")
    print()

def find_device_by_name(name):
    """Find device index by partial name match."""
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if name.lower() in device['name'].lower() and device['max_input_channels'] > 0:
            return i
    return None

def audio_callback(indata, frames, time, status):
    """Callback function for audio input."""
    if status:
        print(f"Status: {status}")
    
    # Put the audio data in the queue
    audio_queue.put(indata.copy())

def analyze_audio():
    """Analyze audio data from the queue."""
    global plot_data, fft_data, rms_history, detected_pitch, detected_volume
    
    while True:
        try:
            # Get audio data from the queue
            data = audio_queue.get(timeout=1.0)
            
            # Convert to mono if needed
            if data.shape[1] > 1:
                data = np.mean(data, axis=1)
            else:
                data = data.flatten()
            
            # Update waveform data
            plot_data = np.roll(plot_data, -len(data))
            plot_data[-len(data):] = data
            
            # Calculate FFT
            fft = np.abs(np.fft.rfft(data * np.hanning(len(data))))
            fft = fft / np.max(fft) if np.max(fft) > 0 else fft
            fft_data = np.roll(fft_data, -len(fft))
            fft_data[-len(fft):] = fft[:len(fft_data)]
            
            # Calculate RMS (volume)
            rms = np.sqrt(np.mean(np.square(data)))
            rms_history = np.roll(rms_history, -1)
            rms_history[-1] = rms
            detected_volume = rms
            
            # Simple pitch detection (find max frequency)
            if np.max(fft) > 0.1:  # Only if there's significant energy
                max_idx = np.argmax(fft)
                detected_pitch = max_idx * (args.sample_rate / 2) / len(fft)
            else:
                detected_pitch = 0
            
            # Print analysis results
            print(f"\rVolume: {rms:.4f} | Pitch: {detected_pitch:.1f} Hz", end="")
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"\nError in audio analysis: {e}")
            break

def update_plot(frame):
    """Update function for the animation."""
    global plot_data, fft_data, rms_history
    
    # Update waveform plot
    waveform_line.set_ydata(plot_data)
    
    # Update FFT plot
    fft_line.set_ydata(fft_data)
    
    # Update volume history plot
    volume_line.set_ydata(rms_history)
    
    # Update pitch and volume text
    info_text.set_text(f"Volume: {detected_volume:.4f}\nPitch: {detected_pitch:.1f} Hz")
    
    return waveform_line, fft_line, volume_line, info_text

def main():
    """Main function."""
    global args, waveform_line, fft_line, volume_line, info_text
    
    args = parse_args()
    
    # List available audio devices
    list_audio_devices()
    
    # Find device
    device_idx = None
    if args.device:
        device_idx = find_device_by_name(args.device)
        if device_idx is not None:
            print(f"Using device {device_idx}: {sd.query_devices(device_idx)['name']}")
        else:
            print(f"No device found matching '{args.device}'")
            return
    
    # Set up plotting if enabled
    if not args.no_plot:
        plt.ion()
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
        
        # Waveform plot
        ax1.set_ylim(-1, 1)
        ax1.set_xlim(0, len(plot_data))
        ax1.set_title("Waveform")
        ax1.set_ylabel("Amplitude")
        waveform_line, = ax1.plot(np.arange(len(plot_data)), plot_data)
        
        # FFT plot
        ax2.set_ylim(0, 1)
        ax2.set_xlim(0, len(fft_data))
        ax2.set_title("Frequency Spectrum")
        ax2.set_ylabel("Magnitude")
        fft_line, = ax2.plot(np.arange(len(fft_data)), fft_data)
        
        # Volume history plot
        ax3.set_ylim(0, 0.5)
        ax3.set_xlim(0, len(rms_history))
        ax3.set_title("Volume History")
        ax3.set_ylabel("RMS")
        volume_line, = ax3.plot(np.arange(len(rms_history)), rms_history)
        
        # Add text for pitch and volume
        info_text = ax1.text(0.02, 0.9, "", transform=ax1.transAxes)
        
        # Create animation
        ani = FuncAnimation(fig, update_plot, interval=50, blit=True)
        plt.tight_layout()
    
    # Start analysis thread
    analysis_thread = threading.Thread(target=analyze_audio, daemon=True)
    analysis_thread.start()
    
    try:
        # Start audio stream
        with sd.InputStream(device=device_idx, channels=args.channels, 
                           callback=audio_callback, 
                           blocksize=args.block_size,
                           samplerate=args.sample_rate):
            
            print(f"Recording from {'default device' if device_idx is None else f'device {device_idx}'}")
            print("Press Ctrl+C to stop")
            
            if args.duration > 0:
                time.sleep(args.duration)
            else:
                # Keep the main thread alive
                while True:
                    if not args.no_plot:
                        plt.pause(0.1)
                    else:
                        time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nRecording stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if not args.no_plot:
            plt.close()

if __name__ == "__main__":
    main()
