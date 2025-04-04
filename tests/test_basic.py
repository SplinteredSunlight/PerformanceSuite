"""
Basic tests for the Performance Suite components.

This module contains basic tests to verify that the core components
of the Performance Suite are working correctly.
"""

import unittest
import numpy as np
from src.config import config
from src.audio_analysis.analyzer import AudioAnalyzer
from src.agent_system.session_manager import SessionManager, MusicalContext
from src.agent_system.bandmate_agent import DrumsAgent, BassAgent


class TestAudioAnalyzer(unittest.TestCase):
    """Tests for the AudioAnalyzer class."""
    
    def setUp(self):
        """Set up the test case."""
        self.analyzer = AudioAnalyzer()
        
    def test_analyze_frame(self):
        """Test that analyze_frame returns the expected features."""
        # Create a simple sine wave as test audio
        sample_rate = 44100
        duration = 0.1  # seconds
        frequency = 440.0  # Hz (A4)
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio_frame = np.sin(2 * np.pi * frequency * t)
        
        # Analyze the frame
        features = self.analyzer.analyze_frame(audio_frame)
        
        # Check that the expected features are present
        self.assertIn("tempo", features)
        self.assertIn("pitch", features)
        self.assertIn("chords", features)
        self.assertIn("dynamics", features)
        self.assertIn("timbre", features)
        
        # Check that dynamics is a float between 0 and 1
        self.assertIsInstance(features["dynamics"], float)
        self.assertGreaterEqual(features["dynamics"], 0.0)
        self.assertLessEqual(features["dynamics"], 1.0)


class TestSessionManager(unittest.TestCase):
    """Tests for the SessionManager class."""
    
    def setUp(self):
        """Set up the test case."""
        self.session_manager = SessionManager()
        
    def test_update_audio_features(self):
        """Test that update_audio_features updates the musical context."""
        # Create some test audio features
        features = {
            "tempo": 130.0,
            "pitch": 440.0,
            "chords": ["D"],
            "dynamics": 0.8,
        }
        
        # Update the session manager with the features
        self.session_manager.update_audio_features(features)
        
        # Check that the context was updated
        self.assertEqual(self.session_manager.context.tempo, 130.0)
        self.assertEqual(self.session_manager.context.chord, "D")
        self.assertEqual(self.session_manager.context.dynamics, 0.8)
        
    def test_update_cycle(self):
        """Test that update_cycle updates the beat position."""
        # Set up the context
        self.session_manager.context.is_playing = True
        self.session_manager.context.tempo = 120.0  # 2 beats per second
        self.session_manager.context.beat_position = 0.0
        self.session_manager.context.bar_position = 1
        self.session_manager.context.time_signature = (4, 4)
        
        # Run an update cycle
        self.session_manager.update_rate = 10  # 10 updates per second
        self.session_manager.update_cycle()
        
        # Check that the beat position was updated
        # At 120 BPM, each beat is 0.5 seconds
        # At 10 updates per second, each update is 0.1 seconds
        # So each update should advance the beat position by 0.2 beats
        self.assertAlmostEqual(self.session_manager.context.beat_position, 0.2, places=2)


class TestBandmateAgents(unittest.TestCase):
    """Tests for the BandmateAgent classes."""
    
    def setUp(self):
        """Set up the test case."""
        self.drums_agent = DrumsAgent()
        self.bass_agent = BassAgent()
        self.context = MusicalContext()
        
    def test_drums_agent_generate_notes(self):
        """Test that the drums agent generates notes."""
        # Set up the context
        self.context.is_playing = True
        self.context.tempo = 120.0
        self.context.beat_position = 0.0  # On the beat
        self.context.section = "verse"
        
        # Update the agent with the context
        self.drums_agent.context = self.context
        
        # Generate notes
        notes = self.drums_agent.generate_notes()
        
        # Check that notes were generated
        self.assertGreater(len(notes), 0)
        
        # Check that the notes have the expected properties
        for note in notes:
            self.assertIn("pitch", note)
            self.assertIn("velocity", note)
            self.assertIn("duration", note)
            self.assertIn("channel", note)
            
    def test_bass_agent_generate_notes(self):
        """Test that the bass agent generates notes."""
        # Set up the context
        self.context.is_playing = True
        self.context.tempo = 120.0
        self.context.beat_position = 0.0  # On the beat
        self.context.section = "verse"
        self.context.key = "C"
        self.context.chord = "C"
        
        # Update the agent with the context
        self.bass_agent.context = self.context
        
        # Generate notes
        notes = self.bass_agent.generate_notes()
        
        # Check that notes were generated
        self.assertGreater(len(notes), 0)
        
        # Check that the notes have the expected properties
        for note in notes:
            self.assertIn("pitch", note)
            self.assertIn("velocity", note)
            self.assertIn("duration", note)
            self.assertIn("channel", note)


if __name__ == "__main__":
    unittest.main()
