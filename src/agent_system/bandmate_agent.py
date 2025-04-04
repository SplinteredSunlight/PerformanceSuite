"""
Bandmate Agent module for the Performance Suite.

This module provides the base class for AI bandmate agents that respond to
the musical context and generate musical output.
"""

from typing import Dict, Any, List, Optional, Callable
import abc
import random
from .session_manager import MusicalContext


class BandmateAgent(abc.ABC):
    """
    Base class for AI bandmate agents.
    
    This abstract class defines the interface for bandmate agents that
    respond to the musical context and generate musical output.
    """
    
    def __init__(self, agent_type: str, responsiveness: float = 0.7):
        """
        Initialize the bandmate agent.
        
        Args:
            agent_type: Type of agent (e.g., "drums", "bass", "keys")
            responsiveness: How responsive the agent is to changes (0.0 to 1.0)
        """
        self.agent_type = agent_type
        self.responsiveness = responsiveness
        self.context: Optional[MusicalContext] = None
        self.is_active = True
        
        # Output callbacks
        self.on_notes_generated: List[Callable[[List[Dict[str, Any]]], None]] = []
        
    def on_context_update(self, context: MusicalContext) -> None:
        """
        Handle updates to the musical context.
        
        Args:
            context: The updated musical context
        """
        self.context = context
        
        if self.is_active and context.is_playing:
            # Check if we should generate notes on this update
            if self._should_generate_notes():
                notes = self.generate_notes()
                
                # Notify listeners
                for callback in self.on_notes_generated:
                    callback(notes)
    
    def _should_generate_notes(self) -> bool:
        """
        Determine if the agent should generate notes on this update.
        
        This method can be overridden by subclasses to implement more
        sophisticated decision-making about when to generate notes.
        
        Returns:
            True if notes should be generated, False otherwise
        """
        if not self.context:
            return False
            
        # Simple implementation: generate notes on beat boundaries
        # This is a placeholder and would be more sophisticated in a real implementation
        beat_position = self.context.beat_position
        beat_boundary = abs(round(beat_position) - beat_position) < 0.05
        
        return beat_boundary
    
    @abc.abstractmethod
    def generate_notes(self) -> List[Dict[str, Any]]:
        """
        Generate musical notes based on the current context.
        
        This method must be implemented by subclasses to generate
        notes appropriate for the specific instrument/role.
        
        Returns:
            List of note dictionaries with pitch, velocity, duration, etc.
        """
        pass


class DrumsAgent(BandmateAgent):
    """
    Bandmate agent for drum parts.
    
    This agent generates drum patterns based on the musical context.
    """
    
    def __init__(self, responsiveness: float = 0.7):
        """
        Initialize the drums agent.
        
        Args:
            responsiveness: How responsive the agent is to changes (0.0 to 1.0)
        """
        super().__init__("drums", responsiveness)
        
        # Drum kit mapping (MIDI note numbers)
        self.drum_mapping = {
            "kick": 36,
            "snare": 38,
            "hi_hat_closed": 42,
            "hi_hat_open": 46,
            "tom_low": 43,
            "tom_mid": 47,
            "tom_high": 50,
            "crash": 49,
            "ride": 51,
        }
        
        # Pattern templates for different sections and time signatures
        self.patterns = {
            "4/4": {
                "verse": self._create_basic_rock_pattern(),
                "chorus": self._create_basic_rock_pattern(intensity=1.2),
                "bridge": self._create_basic_rock_pattern(variation=True),
                "intro": self._create_basic_rock_pattern(sparse=True),
                "outro": self._create_basic_rock_pattern(sparse=True),
            }
        }
        
    def _create_basic_rock_pattern(self, intensity: float = 1.0, variation: bool = False, sparse: bool = False) -> List[Dict[str, Any]]:
        """
        Create a basic rock drum pattern.
        
        Args:
            intensity: Intensity multiplier for velocities
            variation: Whether to add variations to the pattern
            sparse: Whether to create a sparser version of the pattern
            
        Returns:
            List of drum hit dictionaries
        """
        # This is a placeholder implementation
        # In a real implementation, this would create actual drum patterns
        
        pattern = []
        
        # Add a kick on beats 1 and 3
        if not sparse or random.random() > 0.5:
            pattern.append({
                "drum": "kick",
                "beat_position": 0.0,
                "velocity": min(127, int(100 * intensity)),
            })
            
        if not sparse or random.random() > 0.7:
            pattern.append({
                "drum": "kick",
                "beat_position": 2.0,
                "velocity": min(127, int(90 * intensity)),
            })
            
        # Add a snare on beats 2 and 4
        pattern.append({
            "drum": "snare",
            "beat_position": 1.0,
            "velocity": min(127, int(100 * intensity)),
        })
        
        pattern.append({
            "drum": "snare",
            "beat_position": 3.0,
            "velocity": min(127, int(100 * intensity)),
        })
        
        # Add hi-hats on eighth notes
        for i in range(8):
            if sparse and i % 2 == 1 and random.random() > 0.7:
                continue  # Skip some hi-hats in sparse mode
                
            pattern.append({
                "drum": "hi_hat_closed",
                "beat_position": i * 0.5,
                "velocity": min(127, int((70 + random.randint(-10, 10)) * intensity)),
            })
            
        # Add variations
        if variation:
            if random.random() > 0.7:
                # Add a crash on beat 1
                pattern.append({
                    "drum": "crash",
                    "beat_position": 0.0,
                    "velocity": min(127, int(110 * intensity)),
                })
                
            if random.random() > 0.8:
                # Add a tom fill
                for i in range(random.randint(2, 4)):
                    beat_pos = 3.0 + (i * 0.25)
                    if beat_pos < 4.0:
                        tom_type = random.choice(["tom_low", "tom_mid", "tom_high"])
                        pattern.append({
                            "drum": tom_type,
                            "beat_position": beat_pos,
                            "velocity": min(127, int((90 + random.randint(-10, 10)) * intensity)),
                        })
        
        return pattern
        
    def generate_notes(self) -> List[Dict[str, Any]]:
        """
        Generate drum notes based on the current context.
        
        Returns:
            List of note dictionaries with pitch, velocity, duration, etc.
        """
        if not self.context:
            return []
            
        # Get the appropriate pattern based on time signature and section
        time_sig_str = f"{self.context.time_signature[0]}/{self.context.time_signature[1]}"
        section = self.context.section
        
        if time_sig_str not in self.patterns:
            time_sig_str = "4/4"  # Default to 4/4 if time signature not supported
            
        if section not in self.patterns[time_sig_str]:
            section = "verse"  # Default to verse if section not supported
            
        pattern = self.patterns[time_sig_str][section]
        
        # Find drum hits that occur on the current beat position
        current_beat = self.context.beat_position
        notes = []
        
        for hit in pattern:
            if abs(hit["beat_position"] - current_beat) < 0.05:
                # Convert drum hit to MIDI note
                drum_name = hit["drum"]
                if drum_name in self.drum_mapping:
                    note = {
                        "pitch": self.drum_mapping[drum_name],
                        "velocity": hit["velocity"],
                        "duration": 0.1,  # Short duration for drums
                        "channel": 9,  # MIDI channel 10 (0-indexed as 9) for drums
                    }
                    notes.append(note)
        
        # Adjust notes based on dynamics
        if self.context.dynamics < 0.3:
            # Reduce velocities for quiet sections
            for note in notes:
                note["velocity"] = int(note["velocity"] * 0.7)
        elif self.context.dynamics > 0.7:
            # Increase velocities for loud sections
            for note in notes:
                note["velocity"] = min(127, int(note["velocity"] * 1.2))
        
        return notes


class BassAgent(BandmateAgent):
    """
    Bandmate agent for bass parts.
    
    This agent generates bass lines based on the musical context.
    """
    
    def __init__(self, responsiveness: float = 0.8):
        """
        Initialize the bass agent.
        
        Args:
            responsiveness: How responsive the agent is to changes (0.0 to 1.0)
        """
        super().__init__("bass", responsiveness)
        
        # Note mapping for different keys
        self.note_mapping = {
            "C": {"root": 36, "scale": [36, 38, 40, 41, 43, 45, 47, 48]},
            "C#": {"root": 37, "scale": [37, 39, 41, 42, 44, 46, 48, 49]},
            "D": {"root": 38, "scale": [38, 40, 42, 43, 45, 47, 49, 50]},
            "D#": {"root": 39, "scale": [39, 41, 43, 44, 46, 48, 50, 51]},
            "E": {"root": 40, "scale": [40, 42, 44, 45, 47, 49, 51, 52]},
            "F": {"root": 41, "scale": [41, 43, 45, 46, 48, 50, 52, 53]},
            "F#": {"root": 42, "scale": [42, 44, 46, 47, 49, 51, 53, 54]},
            "G": {"root": 43, "scale": [43, 45, 47, 48, 50, 52, 54, 55]},
            "G#": {"root": 44, "scale": [44, 46, 48, 49, 51, 53, 55, 56]},
            "A": {"root": 45, "scale": [45, 47, 49, 50, 52, 54, 56, 57]},
            "A#": {"root": 46, "scale": [46, 48, 50, 51, 53, 55, 57, 58]},
            "B": {"root": 47, "scale": [47, 49, 51, 52, 54, 56, 58, 59]},
        }
        
        # Pattern templates for different sections
        self.patterns = {
            "verse": self._create_simple_bass_pattern(),
            "chorus": self._create_simple_bass_pattern(intensity=1.2),
            "bridge": self._create_simple_bass_pattern(variation=True),
            "intro": self._create_simple_bass_pattern(sparse=True),
            "outro": self._create_simple_bass_pattern(sparse=True),
        }
        
    def _create_simple_bass_pattern(self, intensity: float = 1.0, variation: bool = False, sparse: bool = False) -> List[Dict[str, Any]]:
        """
        Create a simple bass pattern.
        
        Args:
            intensity: Intensity multiplier for velocities
            variation: Whether to add variations to the pattern
            sparse: Whether to create a sparser version of the pattern
            
        Returns:
            List of bass note dictionaries
        """
        # This is a placeholder implementation
        # In a real implementation, this would create actual bass patterns
        
        pattern = []
        
        # Add root note on beat 1
        pattern.append({
            "scale_degree": 0,  # Root note
            "beat_position": 0.0,
            "duration": 0.9,
            "velocity": min(127, int(100 * intensity)),
        })
        
        # Add fifth on beat 2
        if not sparse or random.random() > 0.3:
            pattern.append({
                "scale_degree": 4,  # Fifth
                "beat_position": 1.0,
                "duration": 0.9,
                "velocity": min(127, int(90 * intensity)),
            })
        
        # Add root note on beat 3
        if not sparse or random.random() > 0.2:
            pattern.append({
                "scale_degree": 0,  # Root note
                "beat_position": 2.0,
                "duration": 0.9,
                "velocity": min(127, int(95 * intensity)),
            })
        
        # Add third or fifth on beat 4
        if not sparse or random.random() > 0.4:
            pattern.append({
                "scale_degree": 2 if random.random() > 0.5 else 4,  # Third or fifth
                "beat_position": 3.0,
                "duration": 0.9,
                "velocity": min(127, int(85 * intensity)),
            })
        
        # Add variations
        if variation:
            if random.random() > 0.7:
                # Add a walking bass line
                for i in range(4):
                    if i == 0:
                        continue  # Skip beat 1 as it's already covered
                    
                    scale_degree = random.choice([0, 2, 4, 6])  # Root, third, fifth, seventh
                    pattern.append({
                        "scale_degree": scale_degree,
                        "beat_position": i * 1.0,
                        "duration": 0.9,
                        "velocity": min(127, int((85 + random.randint(-10, 10)) * intensity)),
                    })
        
        return pattern
        
    def generate_notes(self) -> List[Dict[str, Any]]:
        """
        Generate bass notes based on the current context.
        
        Returns:
            List of note dictionaries with pitch, velocity, duration, etc.
        """
        if not self.context:
            return []
            
        # Get the appropriate pattern based on section
        section = self.context.section
        
        if section not in self.patterns:
            section = "verse"  # Default to verse if section not supported
            
        pattern = self.patterns[section]
        
        # Find bass notes that occur on the current beat position
        current_beat = self.context.beat_position
        notes = []
        
        for note_info in pattern:
            if abs(note_info["beat_position"] - current_beat) < 0.05:
                # Convert scale degree to MIDI note based on current key and chord
                key = self.context.key
                chord = self.context.chord
                
                if key not in self.note_mapping:
                    key = "C"  # Default to C if key not supported
                
                # Adjust for chord (simplified implementation)
                root_offset = 0
                if chord and len(chord) > 0:
                    chord_root = chord[0]
                    if chord_root in self.note_mapping:
                        root_offset = self.note_mapping[chord_root]["root"] - self.note_mapping[key]["root"]
                
                scale_degree = note_info["scale_degree"]
                if 0 <= scale_degree < len(self.note_mapping[key]["scale"]):
                    pitch = self.note_mapping[key]["scale"][scale_degree] + root_offset
                    
                    note = {
                        "pitch": pitch,
                        "velocity": note_info["velocity"],
                        "duration": note_info["duration"],
                        "channel": 0,  # MIDI channel 1 (0-indexed)
                    }
                    notes.append(note)
        
        # Adjust notes based on dynamics
        if self.context.dynamics < 0.3:
            # Reduce velocities for quiet sections
            for note in notes:
                note["velocity"] = int(note["velocity"] * 0.7)
        elif self.context.dynamics > 0.7:
            # Increase velocities for loud sections
            for note in notes:
                note["velocity"] = min(127, int(note["velocity"] * 1.2))
        
        return notes
