#!/usr/bin/env python3
"""
Script to test the audio analysis pipeline with real-time audio input.

This script initializes the audio input handler and analyzer, captures audio
from the default input device, and displays the extracted features in real-time.
"""

import os
import sys
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_analysis.input_handler import AudioInputHandler
from src.audio_analysis.analyzer import AudioAnalyzer


class AudioAnalysisVisualizer:
    """Visualizer for audio analysis features."""
    
    def __init__(self, device=None, sample_rate=44100, buffer_size=1024, analysis_mode="balanced"):
        """
        Initialize the audio analysis visualizer.
        
        Args:
            device: Audio input device index (None = system default)
            sample_rate: Audio sample rate in Hz
            buffer_size: Size of the audio buffer for processing
            analysis_mode: Analysis mode ("low_latency", "balanced", or "high_accuracy")
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.hop_length = buffer_size // 2
        
        # Initialize audio input handler
        self.audio_input = AudioInputHandler(
            device=device,
            sample_rate=sample_rate,
            buffer_size=buffer_size,
            channels=1
        )
        
        # Initialize audio analyzer
        self.analyzer = AudioAnalyzer(
            sample_rate=sample_rate,
            buffer_size=buffer_size,
            hop_length=self.hop_length,
            analysis_mode=analysis_mode
        )
        
        # Audio buffer for visualization
        self.audio_buffer = []
        self.features = None
        
        # Register callback for new audio data
        self.audio_input.register_callback(self._audio_callback)
        
        # Set up the plot
        self._setup_plot()
        
    def _audio_callback(self, audio_data):
        """
        Callback function for new audio data.
        
        Args:
            audio_data: New audio data as numpy array
        """
        # Add audio data to buffer
        self.audio_buffer.append(audio_data.copy())
        
        # Keep buffer at a reasonable size
        if len(self.audio_buffer) > 10:
            self.audio_buffer.pop(0)
            
        # Analyze audio data
        if len(self.audio_buffer) > 0:
            # Concatenate all buffered audio data
            data = np.concatenate(self.audio_buffer)
            
            # Analyze the data
            self.features = self.analyzer.analyze_frame(data)
            
    def _setup_plot(self):
        """Set up the matplotlib plot for visualization."""
        self.fig, self.axes = plt.subplots(3, 2, figsize=(12, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Audio waveform plot
        self.axes[0, 0].set_title("Audio Waveform")
        self.axes[0, 0].set_xlabel("Time (samples)")
        self.axes[0, 0].set_ylabel("Amplitude")
        self.waveform_line, = self.axes[0, 0].plot([], [], 'b-')
        
        # Pitch plot
        self.axes[0, 1].set_title("Pitch")
        self.axes[0, 1].set_xlabel("Time (frames)")
        self.axes[0, 1].set_ylabel("Frequency (Hz)")
        self.pitch_line, = self.axes[0, 1].plot([], [], 'r-')
        self.pitch_history = []
        
        # Chroma plot
        self.axes[1, 0].set_title("Chroma")
        self.axes[1, 0].set_xlabel("Pitch Class")
        self.axes[1, 0].set_ylabel("Magnitude")
        self.chroma_bars = self.axes[1, 0].bar(range(12), np.zeros(12))
        self.axes[1, 0].set_xticks(range(12))
        self.axes[1, 0].set_xticklabels(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])
        
        # Dynamics plot
        self.axes[1, 1].set_title("Dynamics")
        self.axes[1, 1].set_xlabel("Time (frames)")
        self.axes[1, 1].set_ylabel("Level")
        self.dynamics_line, = self.axes[1, 1].plot([], [], 'g-')
        self.dynamics_history = []
        
        # MFCC plot
        self.axes[2, 0].set_title("MFCC")
        self.axes[2, 0].set_xlabel("Coefficient")
        self.axes[2, 0].set_ylabel("Value")
        self.mfcc_bars = self.axes[2, 0].bar(range(13), np.zeros(13))
        
        # Tempo plot
        self.axes[2, 1].set_title("Tempo")
        self.axes[2, 1].set_xlabel("Time (frames)")
        self.axes[2, 1].set_ylabel("BPM")
        self.tempo_line, = self.axes[2, 1].plot([], [], 'm-')
        self.tempo_history = []
        
        # Set y-axis limits
        self.axes[0, 0].set_ylim(-1, 1)
        self.axes[0, 1].set_ylim(0, 1000)
        self.axes[1, 0].set_ylim(0, 1)
        self.axes[1, 1].set_ylim(0, 1)
        self.axes[2, 0].set_ylim(-10, 10)
        self.axes[2, 1].set_ylim(60, 180)
        
        # Initialize x-axis data
        self.frame_count = 0
        self.x_data = np.arange(100)
        
        # Add text annotations for current values
        self.pitch_text = self.axes[0, 1].text(0.02, 0.95, "", transform=self.axes[0, 1].transAxes)
        self.chord_text = self.axes[1, 0].text(0.02, 0.95, "", transform=self.axes[1, 0].transAxes)
        self.dynamics_text = self.axes[1, 1].text(0.02, 0.95, "", transform=self.axes[1, 1].transAxes)
        self.tempo_text = self.axes[2, 1].text(0.02, 0.95, "", transform=self.axes[2, 1].transAxes)
        
    def _update_plot(self, frame):
        """
        Update the plot with new data.
        
        Args:
            frame: Animation frame number
        """
        # Update frame count
        self.frame_count += 1
        
        # Get the latest audio data
        if len(self.audio_buffer) > 0:
            audio_data = self.audio_buffer[-1]
            
            # Update waveform plot
            self.waveform_line.set_data(range(len(audio_data)), audio_data)
            self.axes[0, 0].set_xlim(0, len(audio_data))
            
        # Update feature plots if features are available
        if self.features is not None:
            # Update pitch plot
            pitch = self.features["pitch"]["value"]
            if pitch is not None:
                self.pitch_history.append(pitch)
                if len(self.pitch_history) > 100:
                    self.pitch_history.pop(0)
                self.pitch_line.set_data(range(len(self.pitch_history)), self.pitch_history)
                self.axes[0, 1].set_xlim(0, len(self.pitch_history))
                
                # Update pitch text
                note = self.features["pitch"]["note"]
                confidence = self.features["pitch"]["confidence"]
                self.pitch_text.set_text(f"Note: {note}\nFreq: {pitch:.1f} Hz\nConf: {confidence:.2f}")
            
            # Update chroma plot
            if hasattr(self.analyzer, 'chroma_history') and len(self.analyzer.chroma_history) > 0:
                chroma = np.mean(self.analyzer.chroma_history[-1], axis=1)
                for i, bar in enumerate(self.chroma_bars):
                    bar.set_height(chroma[i])
                    
                # Update chord text
                chords = self.features["chords"]["value"]
                confidence = self.features["chords"]["confidence"]
                chord_text = f"Chords: {', '.join(chords) if chords else 'None'}\nConf: {confidence:.2f}"
                self.chord_text.set_text(chord_text)
            
            # Update dynamics plot
            dynamics = self.features["dynamics"]["value"]
            self.dynamics_history.append(dynamics)
            if len(self.dynamics_history) > 100:
                self.dynamics_history.pop(0)
            self.dynamics_line.set_data(range(len(self.dynamics_history)), self.dynamics_history)
            self.axes[1, 1].set_xlim(0, len(self.dynamics_history))
            
            # Update dynamics text
            peak = self.features["dynamics"]["peak"]
            rms = self.features["dynamics"]["rms"]
            self.dynamics_text.set_text(f"Level: {dynamics:.2f}\nPeak: {peak:.2f}\nRMS: {rms:.2f}")
            
            # Update MFCC plot
            mfcc = self.features["timbre"]["mfcc"]
            for i, bar in enumerate(self.mfcc_bars):
                bar.set_height(mfcc[i])
            
            # Update tempo plot
            tempo = self.features["tempo"]["value"]
            self.tempo_history.append(tempo)
            if len(self.tempo_history) > 100:
                self.tempo_history.pop(0)
            self.tempo_line.set_data(range(len(self.tempo_history)), self.tempo_history)
            self.axes[2, 1].set_xlim(0, len(self.tempo_history))
            
            # Update tempo text
            confidence = self.features["tempo"]["confidence"]
            self.tempo_text.set_text(f"Tempo: {tempo:.1f} BPM\nConf: {confidence:.2f}")
        
        # Return all artists that were updated
        return (self.waveform_line, self.pitch_line, self.dynamics_line, 
                self.tempo_line, *self.chroma_bars, *self.mfcc_bars,
                self.pitch_text, self.chord_text, self.dynamics_text, self.tempo_text)
    
    def start(self):
        """Start the audio analysis and visualization."""
        # Start audio input
        self.audio_input.start()
        
        # Start animation
        self.animation = FuncAnimation(
            self.fig, self._update_plot, interval=33, blit=True
        )
        
        # Show the plot
        plt.show()
        
    def stop(self):
        """Stop the audio analysis and visualization."""
        # Stop audio input
        self.audio_input.stop()
        
        # Stop animation
        if hasattr(self, 'animation'):
            self.animation.event_source.stop()


def list_audio_devices():
    """List available audio input devices."""
    handler = AudioInputHandler()
    devices = handler.get_devices()
    
    print("\nAvailable Audio Input Devices:")
    print("-----------------------------")
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Test the audio analysis pipeline")
    parser.add_argument("--device", type=int, help="Audio input device index")
    parser.add_argument("--sample-rate", type=int, default=44100, help="Audio sample rate in Hz")
    parser.add_argument("--buffer-size", type=int, default=1024, help="Audio buffer size")
    parser.add_argument("--mode", choices=["low_latency", "balanced", "high_accuracy"], 
                        default="balanced", help="Analysis mode")
    parser.add_argument("--list-devices", action="store_true", help="List available audio devices and exit")
    args = parser.parse_args()
    
    # List audio devices if requested
    if args.list_devices:
        list_audio_devices()
        return
    
    # Create and start the visualizer
    visualizer = AudioAnalysisVisualizer(
        device=args.device,
        sample_rate=args.sample_rate,
        buffer_size=args.buffer_size,
        analysis_mode=args.mode
    )
    
    try:
        visualizer.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        visualizer.stop()


if __name__ == "__main__":
    main()
