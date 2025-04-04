"""
MIDI Generation module for the Performance Suite.

This module provides functionality to convert note data from bandmate agents
into MIDI messages that can be sent to Ableton Live or other MIDI devices.
"""

import mido
import threading
import time
from typing import Dict, Any, List, Optional, Callable, Union


class MidiGenerator:
    """
    MIDI Generator for converting note data to MIDI messages.
    
    This class handles the conversion of note data from bandmate agents
    into MIDI messages and sends them to the specified MIDI output port.
    """
    
    def __init__(self, port_name: Optional[str] = None):
        """
        Initialize the MIDI generator.
        
        Args:
            port_name: Name of the MIDI output port to use. If None, uses the default port.
        """
        self.port_name = port_name
        self.midi_out: Optional[mido.ports.BaseOutput] = None
        self.active_notes: Dict[int, Dict[int, int]] = {}  # {channel: {note: velocity}}
        
        # Note-off scheduling
        self._note_off_thread: Optional[threading.Thread] = None
        self._note_off_queue: List[Dict[str, Any]] = []
        self._running = False
        
        # Try to open the MIDI port
        self._open_port()
        
    def _open_port(self) -> None:
        """Open the MIDI output port."""
        try:
            if self.port_name:
                self.midi_out = mido.open_output(self.port_name)
            else:
                # Try to open the default port
                output_ports = mido.get_output_names()
                if output_ports:
                    self.midi_out = mido.open_output(output_ports[0])
                    self.port_name = output_ports[0]
                    print(f"Opened default MIDI output port: {self.port_name}")
                else:
                    print("No MIDI output ports available")
        except Exception as e:
            print(f"Error opening MIDI port: {e}")
            self.midi_out = None
            
    def start(self) -> None:
        """Start the MIDI generator and note-off scheduling thread."""
        if self._running:
            return
            
        self._running = True
        self._note_off_thread = threading.Thread(target=self._note_off_loop)
        self._note_off_thread.daemon = True
        self._note_off_thread.start()
        
    def stop(self) -> None:
        """Stop the MIDI generator and note-off scheduling thread."""
        self._running = False
        if self._note_off_thread:
            self._note_off_thread.join(timeout=1.0)
            self._note_off_thread = None
            
        # Send note-off messages for any active notes
        self.all_notes_off()
        
        # Close the MIDI port
        if self.midi_out:
            self.midi_out.close()
            self.midi_out = None
            
    def send_note_on(self, note: int, velocity: int, channel: int = 0) -> None:
        """
        Send a note-on MIDI message.
        
        Args:
            note: MIDI note number (0-127)
            velocity: Note velocity (0-127)
            channel: MIDI channel (0-15)
        """
        if not self.midi_out:
            return
            
        try:
            msg = mido.Message('note_on', note=note, velocity=velocity, channel=channel)
            self.midi_out.send(msg)
            
            # Track active notes
            if channel not in self.active_notes:
                self.active_notes[channel] = {}
            self.active_notes[channel][note] = velocity
        except Exception as e:
            print(f"Error sending note-on message: {e}")
            
    def send_note_off(self, note: int, channel: int = 0) -> None:
        """
        Send a note-off MIDI message.
        
        Args:
            note: MIDI note number (0-127)
            channel: MIDI channel (0-15)
        """
        if not self.midi_out:
            return
            
        try:
            msg = mido.Message('note_off', note=note, velocity=0, channel=channel)
            self.midi_out.send(msg)
            
            # Remove from active notes
            if channel in self.active_notes and note in self.active_notes[channel]:
                del self.active_notes[channel][note]
        except Exception as e:
            print(f"Error sending note-off message: {e}")
            
    def schedule_note_off(self, note: int, channel: int, delay: float) -> None:
        """
        Schedule a note-off message to be sent after a delay.
        
        Args:
            note: MIDI note number (0-127)
            channel: MIDI channel (0-15)
            delay: Delay in seconds before sending the note-off message
        """
        note_off_time = time.time() + delay
        self._note_off_queue.append({
            "time": note_off_time,
            "note": note,
            "channel": channel,
        })
        
    def _note_off_loop(self) -> None:
        """Main loop for the note-off scheduling thread."""
        while self._running:
            current_time = time.time()
            
            # Find note-off messages that are due
            due_notes = [note for note in self._note_off_queue if note["time"] <= current_time]
            
            # Send note-off messages for due notes
            for note_info in due_notes:
                self.send_note_off(note_info["note"], note_info["channel"])
                
            # Remove processed note-off messages from the queue
            self._note_off_queue = [note for note in self._note_off_queue if note["time"] > current_time]
            
            # Sleep a short time to avoid busy-waiting
            time.sleep(0.001)
            
    def all_notes_off(self) -> None:
        """Send note-off messages for all active notes."""
        if not self.midi_out:
            return
            
        for channel, notes in self.active_notes.items():
            for note in notes.keys():
                self.send_note_off(note, channel)
                
        self.active_notes = {}
        
    def send_control_change(self, control: int, value: int, channel: int = 0) -> None:
        """
        Send a control change MIDI message.
        
        Args:
            control: Control number (0-127)
            value: Control value (0-127)
            channel: MIDI channel (0-15)
        """
        if not self.midi_out:
            return
            
        try:
            msg = mido.Message('control_change', control=control, value=value, channel=channel)
            self.midi_out.send(msg)
        except Exception as e:
            print(f"Error sending control change message: {e}")
            
    def send_program_change(self, program: int, channel: int = 0) -> None:
        """
        Send a program change MIDI message.
        
        Args:
            program: Program number (0-127)
            channel: MIDI channel (0-15)
        """
        if not self.midi_out:
            return
            
        try:
            msg = mido.Message('program_change', program=program, channel=channel)
            self.midi_out.send(msg)
        except Exception as e:
            print(f"Error sending program change message: {e}")
            
    def process_notes(self, notes: List[Dict[str, Any]]) -> None:
        """
        Process a list of note dictionaries and send the corresponding MIDI messages.
        
        Args:
            notes: List of note dictionaries with pitch, velocity, duration, channel
        """
        for note in notes:
            pitch = note.get("pitch", 60)
            velocity = note.get("velocity", 64)
            duration = note.get("duration", 0.5)
            channel = note.get("channel", 0)
            
            # Send note-on message
            self.send_note_on(pitch, velocity, channel)
            
            # Schedule note-off message
            self.schedule_note_off(pitch, channel, duration)
