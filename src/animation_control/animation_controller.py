"""
Animation Control module for the Performance Suite.

This module provides functionality to send animation control commands to the
rendering machine based on musical events and agent activity.
"""

import threading
import time
import json
import socket
from typing import Dict, Any, List, Optional, Callable, Union
from pythonosc import udp_client


class AnimationController:
    """
    Animation Controller for sending animation commands to the rendering machine.
    
    This class handles the conversion of musical events and agent activity into
    animation control commands that are sent to the rendering machine.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 12000, protocol: str = "osc"):
        """
        Initialize the animation controller.
        
        Args:
            host: IP address of the rendering machine
            port: Port number for communication
            protocol: Communication protocol ("osc" or "websocket")
        """
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        
        # Communication clients
        self.osc_client: Optional[udp_client.SimpleUDPClient] = None
        self.websocket_client: Optional[socket.socket] = None
        
        # Initialize the appropriate client
        self._init_client()
        
        # Animation state
        self.animation_state: Dict[str, Any] = {
            "tempo": 120.0,
            "intensity": 0.5,
            "section": "verse",
            "agents": {},
        }
        
    def _init_client(self) -> None:
        """Initialize the appropriate communication client."""
        if self.protocol == "osc":
            try:
                self.osc_client = udp_client.SimpleUDPClient(self.host, self.port)
                print(f"Initialized OSC client to {self.host}:{self.port}")
            except Exception as e:
                print(f"Error initializing OSC client: {e}")
                self.osc_client = None
        elif self.protocol == "websocket":
            # Simple socket-based implementation for demonstration
            # In a real implementation, this would use a proper WebSocket library
            try:
                self.websocket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.websocket_client.connect((self.host, self.port))
                print(f"Initialized WebSocket client to {self.host}:{self.port}")
            except Exception as e:
                print(f"Error initializing WebSocket client: {e}")
                self.websocket_client = None
        else:
            print(f"Unsupported protocol: {self.protocol}")
            
    def close(self) -> None:
        """Close the communication client."""
        if self.osc_client:
            # OSC client doesn't need explicit closing
            self.osc_client = None
        
        if self.websocket_client:
            try:
                self.websocket_client.close()
            except Exception as e:
                print(f"Error closing WebSocket client: {e}")
            self.websocket_client = None
            
    def send_command(self, address: str, data: Any) -> None:
        """
        Send a command to the rendering machine.
        
        Args:
            address: Command address/path
            data: Command data
        """
        if self.protocol == "osc" and self.osc_client:
            try:
                self.osc_client.send_message(address, data)
            except Exception as e:
                print(f"Error sending OSC message: {e}")
        elif self.protocol == "websocket" and self.websocket_client:
            try:
                # Format as JSON message
                message = json.dumps({
                    "address": address,
                    "data": data,
                })
                self.websocket_client.sendall(message.encode() + b'\n')
            except Exception as e:
                print(f"Error sending WebSocket message: {e}")
                
    def update_tempo(self, tempo: float) -> None:
        """
        Update the tempo for animations.
        
        Args:
            tempo: Tempo in BPM
        """
        self.animation_state["tempo"] = tempo
        self.send_command("/tempo", tempo)
        
    def update_intensity(self, intensity: float) -> None:
        """
        Update the overall animation intensity.
        
        Args:
            intensity: Intensity value between 0.0 and 1.0
        """
        self.animation_state["intensity"] = intensity
        self.send_command("/intensity", intensity)
        
    def update_section(self, section: str) -> None:
        """
        Update the current musical section.
        
        Args:
            section: Section name (e.g., "verse", "chorus")
        """
        self.animation_state["section"] = section
        self.send_command("/section", section)
        
    def agent_note_event(self, agent_type: str, notes: List[Dict[str, Any]]) -> None:
        """
        Handle a note event from a bandmate agent.
        
        Args:
            agent_type: Type of agent (e.g., "drums", "bass")
            notes: List of note dictionaries
        """
        if not notes:
            return
            
        # Calculate average velocity as a measure of intensity
        avg_velocity = sum(note.get("velocity", 64) for note in notes) / len(notes)
        normalized_velocity = avg_velocity / 127.0
        
        # Update agent state
        if agent_type not in self.animation_state["agents"]:
            self.animation_state["agents"][agent_type] = {
                "active": True,
                "intensity": normalized_velocity,
                "last_note_time": time.time(),
            }
        else:
            self.animation_state["agents"][agent_type].update({
                "intensity": normalized_velocity,
                "last_note_time": time.time(),
            })
            
        # Send agent-specific animation command
        self.send_command(f"/agent/{agent_type}/note", {
            "intensity": normalized_velocity,
            "count": len(notes),
        })
        
        # For drums, send specific hit types
        if agent_type == "drums":
            for note in notes:
                pitch = note.get("pitch", 60)
                velocity = note.get("velocity", 64)
                
                # Map MIDI note numbers to drum types
                drum_type = "other"
                if pitch == 36:
                    drum_type = "kick"
                elif pitch == 38:
                    drum_type = "snare"
                elif pitch in (42, 44, 46):
                    drum_type = "hihat"
                elif pitch in (49, 51, 52, 53, 55, 57, 59):
                    drum_type = "cymbal"
                elif pitch in (41, 43, 45, 47, 48, 50):
                    drum_type = "tom"
                    
                self.send_command(f"/agent/drums/hit", {
                    "type": drum_type,
                    "intensity": velocity / 127.0,
                })
                
    def update_beat_position(self, beat_position: float, bar_position: int) -> None:
        """
        Update the current beat position for animations.
        
        Args:
            beat_position: Position within the current bar (0.0 to beats_per_bar)
            bar_position: Current bar number
        """
        self.send_command("/beat", {
            "beat": beat_position,
            "bar": bar_position,
        })
        
        # Send on-beat messages for strong beats (1 and 3 in 4/4)
        if abs(beat_position - 0.0) < 0.05 or abs(beat_position - 2.0) < 0.05:
            self.send_command("/beat/strong", {
                "beat": beat_position,
                "bar": bar_position,
            })
            
    def update_from_musical_context(self, context_dict: Dict[str, Any]) -> None:
        """
        Update animation state from a musical context dictionary.
        
        Args:
            context_dict: Dictionary representation of the musical context
        """
        # Update tempo if changed
        if "tempo" in context_dict and context_dict["tempo"] != self.animation_state["tempo"]:
            self.update_tempo(context_dict["tempo"])
            
        # Update section if changed
        if "section" in context_dict and context_dict["section"] != self.animation_state["section"]:
            self.update_section(context_dict["section"])
            
        # Update beat position
        if "beat_position" in context_dict and "bar_position" in context_dict:
            self.update_beat_position(context_dict["beat_position"], context_dict["bar_position"])
            
        # Update intensity based on dynamics
        if "dynamics" in context_dict:
            self.update_intensity(context_dict["dynamics"])
