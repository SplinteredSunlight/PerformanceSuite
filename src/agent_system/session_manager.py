"""
Session Manager module for the Performance Suite.

This module provides the central coordination for the agent system,
managing the musical context and coordinating the bandmate agents.
"""

from typing import Dict, Any, List, Optional, Callable
import time
import threading


class MusicalContext:
    """
    Container for the current musical context.
    
    This class holds the current musical state, including tempo, key, chord progression,
    dynamics, and other musical parameters that agents need to make decisions.
    """
    
    def __init__(self):
        """Initialize the musical context with default values."""
        self.tempo: float = 120.0
        self.key: str = "C"
        self.chord: str = "C"
        self.chord_progression: List[str] = ["C"]
        self.dynamics: float = 0.5  # 0.0 to 1.0
        self.section: str = "verse"
        self.beat_position: float = 0.0
        self.bar_position: int = 1
        self.time_signature: tuple = (4, 4)  # (beats per bar, beat unit)
        self.is_playing: bool = False
        
    def update(self, **kwargs) -> None:
        """
        Update the musical context with new values.
        
        Args:
            **kwargs: Key-value pairs of attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the musical context to a dictionary.
        
        Returns:
            Dictionary representation of the musical context
        """
        return {
            "tempo": self.tempo,
            "key": self.key,
            "chord": self.chord,
            "chord_progression": self.chord_progression,
            "dynamics": self.dynamics,
            "section": self.section,
            "beat_position": self.beat_position,
            "bar_position": self.bar_position,
            "time_signature": self.time_signature,
            "is_playing": self.is_playing,
        }


class SessionManager:
    """
    Central coordinator for the agent system.
    
    The Session Manager maintains the musical context and coordinates
    the bandmate agents, ensuring they have the information they need
    to make musical decisions.
    """
    
    def __init__(self, update_rate: float = 30.0):
        """
        Initialize the Session Manager.
        
        Args:
            update_rate: Update rate in Hz
        """
        self.update_rate = update_rate
        self.update_interval = 1.0 / update_rate
        
        self.context = MusicalContext()
        self.agents: List[Any] = []  # Will hold BandmateAgent instances
        
        self.audio_features: Dict[str, Any] = {}
        self.control_commands: List[Dict[str, Any]] = []
        
        self._running = False
        self._update_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_context_updated: List[Callable[[MusicalContext], None]] = []
        
    def register_agent(self, agent: Any) -> None:
        """
        Register a bandmate agent with the session manager.
        
        Args:
            agent: The bandmate agent to register
        """
        self.agents.append(agent)
        
    def update_audio_features(self, features: Dict[str, Any]) -> None:
        """
        Update the current audio features from the audio analysis.
        
        Args:
            features: Dictionary of audio features
        """
        self.audio_features = features
        
        # Update musical context based on audio features
        context_updates = {}
        
        if "tempo" in features and features["tempo"] is not None:
            context_updates["tempo"] = features["tempo"]
            
        if "dynamics" in features:
            context_updates["dynamics"] = features["dynamics"]
            
        if "chords" in features and features["chords"]:
            context_updates["chord"] = features["chords"][0]
            
        self.context.update(**context_updates)
        
    def add_control_command(self, command: Dict[str, Any]) -> None:
        """
        Add a control command from the performer.
        
        Args:
            command: Dictionary containing the command details
        """
        self.control_commands.append(command)
        
    def process_control_commands(self) -> None:
        """Process any pending control commands."""
        if not self.control_commands:
            return
            
        for command in self.control_commands:
            command_type = command.get("type")
            
            if command_type == "section_change":
                self.context.update(section=command.get("section", "verse"))
            elif command_type == "tempo_change":
                self.context.update(tempo=command.get("tempo", self.context.tempo))
            elif command_type == "key_change":
                self.context.update(key=command.get("key", self.context.key))
            elif command_type == "start":
                self.context.update(is_playing=True)
            elif command_type == "stop":
                self.context.update(is_playing=False)
                
        # Clear processed commands
        self.control_commands = []
        
    def update_cycle(self) -> None:
        """Run a single update cycle."""
        # Process control commands
        self.process_control_commands()
        
        # Update beat position
        if self.context.is_playing:
            beats_per_second = self.context.tempo / 60.0
            beat_increment = beats_per_second / self.update_rate
            
            self.context.beat_position += beat_increment
            
            # Update bar position
            beats_per_bar = self.context.time_signature[0]
            if self.context.beat_position >= beats_per_bar:
                self.context.beat_position -= beats_per_bar
                self.context.bar_position += 1
        
        # Notify agents of context update
        for agent in self.agents:
            agent.on_context_update(self.context)
            
        # Call context update callbacks
        for callback in self.on_context_updated:
            callback(self.context)
            
    def _update_loop(self) -> None:
        """Main update loop that runs in a separate thread."""
        while self._running:
            start_time = time.time()
            
            self.update_cycle()
            
            # Sleep to maintain update rate
            elapsed = time.time() - start_time
            sleep_time = max(0, self.update_interval - elapsed)
            time.sleep(sleep_time)
            
    def start(self) -> None:
        """Start the session manager update loop."""
        if self._running:
            return
            
        self._running = True
        self._update_thread = threading.Thread(target=self._update_loop)
        self._update_thread.daemon = True
        self._update_thread.start()
        
    def stop(self) -> None:
        """Stop the session manager update loop."""
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=1.0)
            self._update_thread = None
