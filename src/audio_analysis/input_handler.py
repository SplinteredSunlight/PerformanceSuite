"""
Audio input handler module for the Performance Suite.

This module provides functionality to capture real-time audio from input devices
and make it available for analysis.
"""

import collections
import threading
import numpy as np
import sounddevice as sd
from typing import Optional, List, Callable, Deque, Dict, Any


class AudioInputHandler:
    """
    Handler for capturing real-time audio from input devices.
    
    This class manages the audio input stream, buffers the incoming audio data,
    and provides access to the latest audio frames for analysis.
    """
    
    def __init__(
        self,
        device: Optional[int] = None,
        sample_rate: int = 44100,
        buffer_size: int = 1024,
        channels: int = 1,
        dtype: str = 'float32'
    ):
        """
        Initialize the audio input handler.
        
        Args:
            device: Audio input device index (None = system default)
            sample_rate: Audio sample rate in Hz
            buffer_size: Size of the audio buffer for processing
            channels: Number of audio channels (1 = mono, 2 = stereo)
            dtype: Data type for audio samples
        """
        self.device = device
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        self.dtype = dtype
        
        # Audio buffer (4x buffer_size to allow for analysis windows)
        self.audio_buffer: Deque[np.ndarray] = collections.deque(maxlen=buffer_size * 4)
        
        # Pre-fill buffer with zeros
        for _ in range(self.audio_buffer.maxlen):
            self.audio_buffer.append(np.zeros(channels, dtype=dtype))
        
        # Stream and state
        self.stream: Optional[sd.InputStream] = None
        self._running = False
        self._lock = threading.RLock()
        
        # Callbacks for new audio data
        self.callbacks: List[Callable[[np.ndarray], None]] = []
        
        # Audio statistics
        self.stats = {
            'peak_level': 0.0,
            'rms_level': 0.0,
            'clipping': False,
            'dropout': False
        }
    
    def audio_callback(self, indata: np.ndarray, frames: int, time: Any, status: Any) -> None:
        """
        Callback function for the audio stream.
        
        This is called by sounddevice for each audio block.
        
        Args:
            indata: Input audio data as numpy array
            frames: Number of frames in the audio block
            time: Stream time information
            status: Stream status information
        """
        if status:
            # Handle status flags (e.g., overflow, underflow)
            self.stats['dropout'] = True
            print(f"Audio stream status: {status}")
        else:
            self.stats['dropout'] = False
        
        # Make a copy of the data to avoid reference issues
        data = indata.copy()
        
        # Calculate audio statistics
        with self._lock:
            # Peak level
            peak = np.max(np.abs(data))
            self.stats['peak_level'] = peak
            
            # RMS level
            rms = np.sqrt(np.mean(np.square(data)))
            self.stats['rms_level'] = rms
            
            # Clipping detection
            self.stats['clipping'] = peak >= 0.99
            
            # Add data to buffer frame by frame
            for frame_idx in range(frames):
                self.audio_buffer.append(data[frame_idx])
        
        # Call registered callbacks with the new data
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Error in audio callback: {e}")
    
    def start(self) -> None:
        """Start the audio input stream."""
        if self._running:
            print("Audio input stream is already running")
            return
        
        try:
            self.stream = sd.InputStream(
                device=self.device,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                dtype=self.dtype,
                callback=self.audio_callback
            )
            self.stream.start()
            self._running = True
            print(f"Audio input stream started (device={self.device}, "
                  f"sample_rate={self.sample_rate}, buffer_size={self.buffer_size})")
        except Exception as e:
            print(f"Error starting audio input stream: {e}")
            self._running = False
    
    def stop(self) -> None:
        """Stop the audio input stream."""
        if not self._running:
            print("Audio input stream is not running")
            return
        
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            self._running = False
            print("Audio input stream stopped")
        except Exception as e:
            print(f"Error stopping audio input stream: {e}")
    
    def get_audio_data(self, frames: Optional[int] = None) -> np.ndarray:
        """
        Get the latest audio data from the buffer.
        
        Args:
            frames: Number of frames to retrieve (None = all available)
            
        Returns:
            Numpy array containing the requested audio data
        """
        with self._lock:
            if frames is None:
                frames = len(self.audio_buffer)
            
            # Limit frames to available data
            frames = min(frames, len(self.audio_buffer))
            
            # Get the latest 'frames' frames from the buffer
            data = list(self.audio_buffer)[-frames:]
            
            # Convert to numpy array
            return np.array(data)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current audio statistics.
        
        Returns:
            Dictionary containing audio statistics
        """
        with self._lock:
            return self.stats.copy()
    
    def register_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """
        Register a callback function to be called with new audio data.
        
        Args:
            callback: Function to call with new audio data
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """
        Unregister a previously registered callback function.
        
        Args:
            callback: Function to remove from callbacks
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def is_running(self) -> bool:
        """
        Check if the audio input stream is running.
        
        Returns:
            True if the stream is running, False otherwise
        """
        return self._running
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Get a list of available audio input devices.
        
        Returns:
            List of dictionaries containing device information
        """
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        return input_devices
