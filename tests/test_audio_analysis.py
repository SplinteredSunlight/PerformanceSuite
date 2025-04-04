"""
Tests for the audio analysis components of the Performance Suite.
"""

import os
import sys
import unittest
import numpy as np
import tempfile
import soundfile as sf
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_analysis.analyzer import AudioAnalyzer
from src.audio_analysis.input_handler import AudioInputHandler


class TestAudioAnalyzer(unittest.TestCase):
    """Test cases for the AudioAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.hop_length = 512
        self.analyzer = AudioAnalyzer(
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size,
            hop_length=self.hop_length,
            analysis_mode="balanced"
        )
        
        # Create a simple sine wave for testing
        self.duration = 1.0  # seconds
        self.frequency = 440.0  # Hz (A4)
        self.t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), endpoint=False)
        self.sine_wave = 0.5 * np.sin(2 * np.pi * self.frequency * self.t)
        
    def test_initialization(self):
        """Test that the analyzer initializes correctly."""
        self.assertEqual(self.analyzer.sample_rate, self.sample_rate)
        self.assertEqual(self.analyzer.buffer_size, self.buffer_size)
        self.assertEqual(self.analyzer.hop_length, self.hop_length)
        self.assertEqual(self.analyzer.analysis_mode, "balanced")
        self.assertEqual(self.analyzer.n_fft, 2048)  # Default for balanced mode
        
    def test_analysis_modes(self):
        """Test that different analysis modes set the correct FFT size."""
        analyzer_low = AudioAnalyzer(analysis_mode="low_latency")
        analyzer_high = AudioAnalyzer(analysis_mode="high_accuracy")
        
        self.assertEqual(analyzer_low.n_fft, 1024)
        self.assertEqual(analyzer_high.n_fft, 4096)
        
    def test_pre_emphasis(self):
        """Test the pre-emphasis filter."""
        filtered = self.analyzer._apply_pre_emphasis(self.sine_wave)
        
        # Check that the filtered signal has the same length
        self.assertEqual(len(filtered), len(self.sine_wave))
        
        # Check that the filter has changed the signal
        self.assertFalse(np.array_equal(filtered, self.sine_wave))
        
    def test_analyze_frame(self):
        """Test analyzing an audio frame."""
        # Use a segment of the sine wave
        frame = self.sine_wave[:self.buffer_size]
        
        # Analyze the frame
        features = self.analyzer.analyze_frame(frame)
        
        # Check that all expected features are present
        self.assertIn("tempo", features)
        self.assertIn("pitch", features)
        self.assertIn("chords", features)
        self.assertIn("dynamics", features)
        self.assertIn("timbre", features)
        
        # Check that tempo has value and confidence
        self.assertIn("value", features["tempo"])
        self.assertIn("confidence", features["tempo"])
        
        # Check that pitch has value, confidence, and note
        self.assertIn("value", features["pitch"])
        self.assertIn("confidence", features["pitch"])
        self.assertIn("note", features["pitch"])
        
        # Check that dynamics has expected fields
        self.assertIn("value", features["dynamics"])
        self.assertIn("peak", features["dynamics"])
        self.assertIn("rms", features["dynamics"])
        
        # Check that timbre has expected fields
        self.assertIn("mfcc", features["timbre"])
        self.assertIn("spectral_centroid", features["timbre"])
        self.assertIn("spectral_contrast", features["timbre"])
        
    def test_pitch_detection(self):
        """Test pitch detection on a sine wave."""
        # Use a longer segment for better pitch detection
        frame = self.sine_wave[:self.buffer_size * 4]
        
        # Extract pitch
        pitch_data = self.analyzer._extract_pitch(frame)
        
        # Check that pitch is detected
        self.assertIsNotNone(pitch_data["pitch"])
        
        # Check that the detected pitch is close to the expected frequency
        # Allow for some error in the pitch detection
        if pitch_data["pitch"] is not None:
            self.assertAlmostEqual(pitch_data["pitch"], self.frequency, delta=self.frequency * 0.1)
        
    def test_dynamics_extraction(self):
        """Test dynamics extraction."""
        # Use a segment of the sine wave
        frame = self.sine_wave[:self.buffer_size]
        
        # Extract dynamics
        dynamics_data = self.analyzer._extract_dynamics(frame)
        
        # Check that dynamics values are in the expected range
        self.assertGreaterEqual(dynamics_data["value"], 0.0)
        self.assertLessEqual(dynamics_data["value"], 1.0)
        self.assertGreaterEqual(dynamics_data["peak"], 0.0)
        self.assertLessEqual(dynamics_data["peak"], 1.0)
        self.assertGreaterEqual(dynamics_data["rms"], 0.0)
        
        # For a sine wave with amplitude 0.5, peak should be close to 0.5
        self.assertAlmostEqual(dynamics_data["peak"], 0.5, delta=0.1)


class TestAudioInputHandler(unittest.TestCase):
    """Test cases for the AudioInputHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.channels = 1
        
        # Create a mock for sounddevice.InputStream
        self.mock_stream = MagicMock()
        self.mock_stream.start = MagicMock()
        self.mock_stream.stop = MagicMock()
        self.mock_stream.close = MagicMock()
        
        # Create a temporary audio file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        self.temp_file.close()
        
        # Create a simple sine wave and save it to the temporary file
        duration = 1.0  # seconds
        frequency = 440.0  # Hz (A4)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        sine_wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        sf.write(self.temp_file.name, sine_wave, self.sample_rate)
        
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
        
    @patch('sounddevice.InputStream')
    def test_initialization(self, mock_input_stream):
        """Test that the input handler initializes correctly."""
        mock_input_stream.return_value = self.mock_stream
        
        handler = AudioInputHandler(
            device=None,
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size,
            channels=self.channels
        )
        
        self.assertEqual(handler.sample_rate, self.sample_rate)
        self.assertEqual(handler.buffer_size, self.buffer_size)
        self.assertEqual(handler.channels, self.channels)
        self.assertFalse(handler.is_running())
        
    @patch('sounddevice.InputStream')
    def test_start_stop(self, mock_input_stream):
        """Test starting and stopping the input handler."""
        mock_input_stream.return_value = self.mock_stream
        
        handler = AudioInputHandler(
            device=None,
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size,
            channels=self.channels
        )
        
        # Start the handler
        handler.start()
        self.assertTrue(handler.is_running())
        mock_input_stream.assert_called_once()
        self.mock_stream.start.assert_called_once()
        
        # Stop the handler
        handler.stop()
        self.assertFalse(handler.is_running())
        self.mock_stream.stop.assert_called_once()
        self.mock_stream.close.assert_called_once()
        
    @patch('sounddevice.InputStream')
    def test_callbacks(self, mock_input_stream):
        """Test registering and unregistering callbacks."""
        mock_input_stream.return_value = self.mock_stream
        
        handler = AudioInputHandler(
            device=None,
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size,
            channels=self.channels
        )
        
        # Create a mock callback
        callback = MagicMock()
        
        # Register the callback
        handler.register_callback(callback)
        self.assertIn(callback, handler.callbacks)
        
        # Unregister the callback
        handler.unregister_callback(callback)
        self.assertNotIn(callback, handler.callbacks)
        
    @patch('sounddevice.InputStream')
    def test_audio_callback(self, mock_input_stream):
        """Test the audio callback function."""
        mock_input_stream.return_value = self.mock_stream
        
        handler = AudioInputHandler(
            device=None,
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size,
            channels=self.channels
        )
        
        # Create a mock callback
        callback = MagicMock()
        handler.register_callback(callback)
        
        # Create test audio data
        test_data = np.random.rand(self.buffer_size, self.channels).astype(np.float32)
        
        # Call the audio callback
        handler.audio_callback(test_data, self.buffer_size, None, None)
        
        # Check that the callback was called with the test data
        callback.assert_called_once()
        np.testing.assert_array_equal(callback.call_args[0][0], test_data)
        
        # Check that stats were updated
        stats = handler.get_stats()
        self.assertGreaterEqual(stats["peak_level"], 0.0)
        self.assertGreaterEqual(stats["rms_level"], 0.0)
        self.assertIn("clipping", stats)
        self.assertIn("dropout", stats)


if __name__ == '__main__':
    unittest.main()
