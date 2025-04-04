"""
Main application module for the Performance Suite.

This module provides the main application class that ties together all the
components of the Performance Suite.
"""

import time
import threading
import argparse
import logging
import os
import numpy as np
from typing import Dict, Any, List, Optional, Callable

from .config import config
from .audio_analysis.analyzer import AudioAnalyzer
from .audio_analysis.input_handler import AudioInputHandler
from .agent_system.session_manager import SessionManager, MusicalContext
from .agent_system.bandmate_agent import BandmateAgent, DrumsAgent, BassAgent
from .midi_generation.midi_generator import MidiGenerator
from .animation_control.animation_controller import AnimationController


class PerformanceSuite:
    """
    Main application class for the Performance Suite.
    
    This class ties together all the components of the Performance Suite and
    manages the overall application lifecycle.
    """
    
    def __init__(self):
        """Initialize the Performance Suite application."""
        # Configure logging
        log_level = getattr(logging, config.get("system", "log_level", "INFO"))
        log_file = config.get("system", "log_file", "logs/performance_suite.log")
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ]
        )
        
        self.logger = logging.getLogger("PerformanceSuite")
        self.logger.info("Initializing Performance Suite")
        
        # Initialize components
        self._init_components()
        
        # Application state
        self._running = False
        self._main_thread: Optional[threading.Thread] = None
        self._audio_processing_thread: Optional[threading.Thread] = None
        self._audio_buffer_lock = threading.RLock()
        self._audio_buffer: List[np.ndarray] = []
        self._last_audio_features: Dict[str, Any] = {}
        
    def _init_components(self) -> None:
        """Initialize all system components."""
        # Audio Configuration
        sample_rate = config.get("audio", "sample_rate", 44100)
        buffer_size = config.get("audio", "buffer_size", 1024)
        hop_length = buffer_size // 2  # 50% overlap for analysis
        channels = config.get("audio", "channels", 1)
        input_device = config.get("audio", "input_device", None)
        analysis_mode = config.get("audio", "analysis_mode", "balanced")
        
        # Audio Input Handler
        self.logger.info("Initializing Audio Input Handler")
        self.audio_input = AudioInputHandler(
            device=input_device,
            sample_rate=sample_rate,
            buffer_size=buffer_size,
            channels=channels
        )
        
        # Register callback for new audio data
        self.audio_input.register_callback(self._audio_callback)
        
        # Audio Analyzer
        self.logger.info("Initializing Audio Analyzer")
        self.audio_analyzer = AudioAnalyzer(
            sample_rate=sample_rate,
            buffer_size=buffer_size,
            hop_length=hop_length,
            analysis_mode=analysis_mode
        )
        
        # Session Manager
        self.logger.info("Initializing Session Manager")
        update_rate = config.get("agent_system", "session_manager", {}).get("update_rate", 30)
        self.session_manager = SessionManager(update_rate=update_rate)
        
        # Bandmate Agents
        self.logger.info("Initializing Bandmate Agents")
        self.agents: List[BandmateAgent] = []
        
        # Create agents based on configuration
        bandmate_configs = config.get("agent_system", "bandmate_agents", [])
        for agent_config in bandmate_configs:
            agent_type = agent_config.get("type", "")
            enabled = agent_config.get("enabled", True)
            responsiveness = agent_config.get("responsiveness", 0.7)
            
            if not enabled:
                continue
                
            if agent_type == "drums":
                agent = DrumsAgent(responsiveness=responsiveness)
                self.agents.append(agent)
                self.logger.info(f"Created Drums Agent (responsiveness={responsiveness})")
            elif agent_type == "bass":
                agent = BassAgent(responsiveness=responsiveness)
                self.agents.append(agent)
                self.logger.info(f"Created Bass Agent (responsiveness={responsiveness})")
            else:
                self.logger.warning(f"Unknown agent type: {agent_type}")
                
        # Register agents with session manager
        for agent in self.agents:
            self.session_manager.register_agent(agent)
            
        # MIDI Generator
        self.logger.info("Initializing MIDI Generator")
        midi_port = config.get("midi", "output_port", None)
        self.midi_generator = MidiGenerator(port_name=midi_port)
        
        # Connect agent outputs to MIDI generator
        for agent in self.agents:
            agent.on_notes_generated.append(self.midi_generator.process_notes)
            
        # Animation Controller
        self.logger.info("Initializing Animation Controller")
        animation_host = config.get("animation", "osc_host", "127.0.0.1")
        animation_port = config.get("animation", "osc_port", 12000)
        self.animation_controller = AnimationController(
            host=animation_host,
            port=animation_port
        )
        
        # Connect session manager to animation controller
        self.session_manager.on_context_updated.append(
            lambda context: self.animation_controller.update_from_musical_context(context.to_dict())
        )
        
        # Connect agent outputs to animation controller
        for agent in self.agents:
            agent.on_notes_generated.append(
                lambda notes, agent_type=agent.agent_type: self.animation_controller.agent_note_event(agent_type, notes)
            )
    
    def _audio_callback(self, audio_data: np.ndarray) -> None:
        """
        Callback function for new audio data.
        
        Args:
            audio_data: New audio data as numpy array
        """
        with self._audio_buffer_lock:
            self._audio_buffer.append(audio_data.copy())
    
    def _audio_processing_loop(self) -> None:
        """Audio processing loop that runs in a separate thread."""
        self.logger.info("Starting audio processing loop")
        
        analysis_interval = 1.0 / 30.0  # 30 Hz analysis rate
        last_analysis_time = time.time()
        
        while self._running:
            current_time = time.time()
            elapsed = current_time - last_analysis_time
            
            # Process audio at regular intervals
            if elapsed >= analysis_interval:
                last_analysis_time = current_time
                
                # Get audio data from buffer
                audio_data = None
                with self._audio_buffer_lock:
                    if self._audio_buffer:
                        # Concatenate all buffered audio data
                        audio_data = np.concatenate(self._audio_buffer)
                        self._audio_buffer = []
                
                if audio_data is not None and len(audio_data) > 0:
                    try:
                        # Analyze audio data
                        features = self.audio_analyzer.analyze_frame(audio_data)
                        
                        # Convert to format expected by session manager
                        audio_features = self._convert_features_for_session_manager(features)
                        
                        # Update session manager
                        self.session_manager.update_audio_features(audio_features)
                        
                        # Store last features
                        self._last_audio_features = audio_features
                        
                        # Log audio statistics periodically
                        if self.logger.isEnabledFor(logging.DEBUG):
                            stats = self.audio_input.get_stats()
                            self.logger.debug(f"Audio stats: peak={stats['peak_level']:.2f}, "
                                             f"rms={stats['rms_level']:.2f}, "
                                             f"clipping={stats['clipping']}, "
                                             f"dropout={stats['dropout']}")
                    except Exception as e:
                        self.logger.error(f"Error processing audio: {e}")
            
            # Sleep to avoid busy-waiting
            time.sleep(0.001)
        
        self.logger.info("Exiting audio processing loop")
    
    def _convert_features_for_session_manager(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert analyzer features to the format expected by the session manager.
        
        Args:
            features: Features from the audio analyzer
            
        Returns:
            Features in session manager format
        """
        # Extract values from nested feature structure
        tempo = features["tempo"]["value"] if features["tempo"]["value"] is not None else 120.0
        
        pitch = None
        if features["pitch"]["value"] is not None:
            pitch = features["pitch"]["value"]
        
        chords = []
        if features["chords"]["value"]:
            chords = features["chords"]["value"]
        
        dynamics = features["dynamics"]["value"]
        
        # MFCC features for timbre
        timbre = features["timbre"]["mfcc"]
        
        # Create simplified feature dictionary for session manager
        return {
            "tempo": tempo,
            "pitch": pitch,
            "chords": chords,
            "dynamics": dynamics,
            "timbre": timbre,
        }
            
    def start(self) -> None:
        """Start the Performance Suite application."""
        if self._running:
            self.logger.warning("Performance Suite is already running")
            return
            
        self.logger.info("Starting Performance Suite")
        self._running = True
        
        # Start audio input
        self.audio_input.start()
        
        # Start components
        self.midi_generator.start()
        self.session_manager.start()
        
        # Start audio processing thread
        self._audio_processing_thread = threading.Thread(target=self._audio_processing_loop)
        self._audio_processing_thread.daemon = True
        self._audio_processing_thread.start()
        
        # Start main thread
        self._main_thread = threading.Thread(target=self._main_loop)
        self._main_thread.daemon = True
        self._main_thread.start()
        
        self.logger.info("Performance Suite started")
        
    def stop(self) -> None:
        """Stop the Performance Suite application."""
        if not self._running:
            self.logger.warning("Performance Suite is not running")
            return
            
        self.logger.info("Stopping Performance Suite")
        self._running = False
        
        # Stop audio input
        self.audio_input.stop()
        
        # Stop components
        self.session_manager.stop()
        self.midi_generator.stop()
        self.animation_controller.close()
        
        # Wait for threads to finish
        if self._audio_processing_thread:
            self._audio_processing_thread.join(timeout=1.0)
            self._audio_processing_thread = None
            
        if self._main_thread:
            self._main_thread.join(timeout=1.0)
            self._main_thread = None
            
        self.logger.info("Performance Suite stopped")
        
    def _main_loop(self) -> None:
        """Main application loop."""
        self.logger.info("Entering main loop")
        
        while self._running:
            # This loop is now primarily for system monitoring and control
            # Audio processing happens in the audio processing thread
            
            # Check audio input status
            if not self.audio_input.is_running():
                self.logger.warning("Audio input stopped unexpectedly, attempting to restart")
                try:
                    self.audio_input.start()
                except Exception as e:
                    self.logger.error(f"Failed to restart audio input: {e}")
            
            # Sleep to avoid busy-waiting
            time.sleep(0.1)
            
        self.logger.info("Exiting main loop")
    
    def get_audio_devices(self) -> List[Dict[str, Any]]:
        """
        Get a list of available audio input devices.
        
        Returns:
            List of dictionaries containing device information
        """
        return self.audio_input.get_devices()


def main():
    """Main entry point for the Performance Suite application."""
    parser = argparse.ArgumentParser(description="Performance Suite")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--list-devices", action="store_true", help="List available audio devices and exit")
    args = parser.parse_args()
    
    # Load configuration if specified
    if args.config:
        config.config_path = args.config
        config.load_config()
        
    # Create the application
    app = PerformanceSuite()
    
    # List audio devices if requested
    if args.list_devices:
        devices = app.get_audio_devices()
        print("\nAvailable Audio Input Devices:")
        print("-----------------------------")
        for i, device in enumerate(devices):
            print(f"{i}: {device['name']}")
        return
    
    try:
        app.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        app.stop()


if __name__ == "__main__":
    main()
