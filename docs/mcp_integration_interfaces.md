# MCP Integration Interfaces

This document outlines the key interfaces for the MCP integration in the Performance Suite project.

## Common Interfaces

### `MCPAdapter` Interface

The base interface for all MCP adapters:

```python
class MCPAdapter:
    """Base interface for MCP adapters."""
    
    def connect(self) -> bool:
        """
        Establish connection to the MCP server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
        
    def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        pass
        
    def is_connected(self) -> bool:
        """
        Check if connected to the MCP server.
        
        Returns:
            bool: True if connected, False otherwise
        """
        pass
        
    def health_check(self) -> bool:
        """
        Perform a health check on the MCP server.
        
        Returns:
            bool: True if server is healthy, False otherwise
        """
        pass
        
    def use_fallback(self) -> bool:
        """
        Switch to fallback mode.
        
        Returns:
            bool: True if fallback mode activated, False otherwise
        """
        pass
```

### `ConnectionManager` Interface

Manages connections to MCP servers:

```python
class ConnectionManager:
    """Manages connections to MCP servers."""
    
    def register_adapter(self, adapter_name: str, adapter: MCPAdapter) -> None:
        """
        Register an MCP adapter.
        
        Args:
            adapter_name: Name of the adapter
            adapter: The adapter instance
        """
        pass
        
    def get_adapter(self, adapter_name: str) -> Optional[MCPAdapter]:
        """
        Get an MCP adapter by name.
        
        Args:
            adapter_name: Name of the adapter
            
        Returns:
            Optional[MCPAdapter]: The adapter instance if found, None otherwise
        """
        pass
        
    def connect_all(self) -> Dict[str, bool]:
        """
        Connect to all registered MCP servers.
        
        Returns:
            Dict[str, bool]: Dictionary of adapter names and connection status
        """
        pass
        
    def disconnect_all(self) -> None:
        """Disconnect from all MCP servers."""
        pass
        
    def health_check_all(self) -> Dict[str, bool]:
        """
        Perform health checks on all MCP servers.
        
        Returns:
            Dict[str, bool]: Dictionary of adapter names and health status
        """
        pass
```

## Blender MCP Interfaces

### `BlenderMCPAdapter` Interface

Adapter for the Blender MCP server:

```python
class BlenderMCPAdapter(MCPAdapter):
    """Adapter for the Blender MCP server."""
    
    def set_avatar_animation(self, avatar_id: str, animation_name: str, 
                            intensity: float = 1.0, speed: float = 1.0) -> bool:
        """
        Set an animation for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            animation_name: Name of the animation
            intensity: Animation intensity (0.0 to 1.0)
            speed: Animation speed multiplier
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def trigger_animation_event(self, avatar_id: str, event_name: str, 
                               params: Dict[str, Any] = None) -> bool:
        """
        Trigger an animation event.
        
        Args:
            avatar_id: ID of the avatar
            event_name: Name of the event
            params: Additional parameters for the event
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def set_avatar_parameter(self, avatar_id: str, param_name: str, 
                            value: Any) -> bool:
        """
        Set a parameter for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            param_name: Name of the parameter
            value: Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def get_avatar_parameter(self, avatar_id: str, param_name: str) -> Any:
        """
        Get a parameter value for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            param_name: Name of the parameter
            
        Returns:
            Any: The parameter value
        """
        pass
        
    def get_available_avatars(self) -> List[Dict[str, Any]]:
        """
        Get a list of available avatars.
        
        Returns:
            List[Dict[str, Any]]: List of avatar information dictionaries
        """
        pass
        
    def get_available_animations(self, avatar_id: str) -> List[str]:
        """
        Get a list of available animations for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            List[str]: List of animation names
        """
        pass
```

### `AnimationMapping` Interface

Maps musical events to animation commands:

```python
class AnimationMapping:
    """Maps musical events to animation commands."""
    
    def map_note_event(self, agent_type: str, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Map a note event to animation commands.
        
        Args:
            agent_type: Type of agent (e.g., "drums", "bass")
            notes: List of note dictionaries
            
        Returns:
            Dict[str, Any]: Animation command dictionary
        """
        pass
        
    def map_section_change(self, section: str) -> Dict[str, Any]:
        """
        Map a section change to animation commands.
        
        Args:
            section: New section name
            
        Returns:
            Dict[str, Any]: Animation command dictionary
        """
        pass
        
    def map_intensity_change(self, intensity: float) -> Dict[str, Any]:
        """
        Map an intensity change to animation commands.
        
        Args:
            intensity: New intensity value (0.0 to 1.0)
            
        Returns:
            Dict[str, Any]: Animation command dictionary
        """
        pass
        
    def map_tempo_change(self, tempo: float) -> Dict[str, Any]:
        """
        Map a tempo change to animation commands.
        
        Args:
            tempo: New tempo value in BPM
            
        Returns:
            Dict[str, Any]: Animation command dictionary
        """
        pass
```

## Ableton MCP Interfaces

### `AbletonMCPAdapter` Interface

Adapter for the Ableton MCP server:

```python
class AbletonMCPAdapter(MCPAdapter):
    """Adapter for the Ableton MCP server."""
    
    def send_midi_note(self, note: int, velocity: int, channel: int = 0, 
                      duration: float = 0.5) -> bool:
        """
        Send a MIDI note.
        
        Args:
            note: MIDI note number (0-127)
            velocity: Note velocity (0-127)
            channel: MIDI channel (0-15)
            duration: Note duration in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def send_midi_cc(self, cc: int, value: int, channel: int = 0) -> bool:
        """
        Send a MIDI control change message.
        
        Args:
            cc: Control change number (0-127)
            value: Control value (0-127)
            channel: MIDI channel (0-15)
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def send_midi_program_change(self, program: int, channel: int = 0) -> bool:
        """
        Send a MIDI program change message.
        
        Args:
            program: Program number (0-127)
            channel: MIDI channel (0-15)
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def trigger_clip(self, track: int, scene: int) -> bool:
        """
        Trigger a clip in Ableton Live.
        
        Args:
            track: Track number
            scene: Scene number
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def stop_clip(self, track: int, scene: int = None) -> bool:
        """
        Stop a clip in Ableton Live.
        
        Args:
            track: Track number
            scene: Scene number (if None, stops all clips in the track)
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def set_tempo(self, tempo: float) -> bool:
        """
        Set the tempo in Ableton Live.
        
        Args:
            tempo: Tempo in BPM
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def get_tempo(self) -> float:
        """
        Get the current tempo from Ableton Live.
        
        Returns:
            float: Current tempo in BPM
        """
        pass
        
    def get_track_info(self, track: int) -> Dict[str, Any]:
        """
        Get information about a track in Ableton Live.
        
        Args:
            track: Track number
            
        Returns:
            Dict[str, Any]: Track information dictionary
        """
        pass
```

### `MIDIMapping` Interface

Maps note data to MIDI messages:

```python
class MIDIMapping:
    """Maps note data to MIDI messages."""
    
    def map_notes(self, notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map note data to MIDI messages.
        
        Args:
            notes: List of note dictionaries
            
        Returns:
            List[Dict[str, Any]]: List of MIDI message dictionaries
        """
        pass
        
    def map_drum_hit(self, drum_type: str, velocity: int) -> Dict[str, Any]:
        """
        Map a drum hit to a MIDI message.
        
        Args:
            drum_type: Type of drum (e.g., "kick", "snare")
            velocity: Hit velocity (0-127)
            
        Returns:
            Dict[str, Any]: MIDI message dictionary
        """
        pass
        
    def map_chord(self, chord: str, velocity: int, duration: float) -> List[Dict[str, Any]]:
        """
        Map a chord to MIDI messages.
        
        Args:
            chord: Chord name (e.g., "C", "Dm7")
            velocity: Note velocity (0-127)
            duration: Note duration in seconds
            
        Returns:
            List[Dict[str, Any]]: List of MIDI message dictionaries
        """
        pass
```

## Google ADK Interfaces

### `GoogleADKManager` Interface

Manages the Google ADK integration:

```python
class GoogleADKManager:
    """Manages the Google ADK integration."""
    
    def initialize(self) -> bool:
        """
        Initialize the Google ADK.
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def create_agent(self, agent_type: str, config: Dict[str, Any] = None) -> str:
        """
        Create a new agent.
        
        Args:
            agent_type: Type of agent to create
            config: Agent configuration
            
        Returns:
            str: Agent ID
        """
        pass
        
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: ID of the agent to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
        
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get information about an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dict[str, Any]: Agent information dictionary
        """
        pass
        
    def send_message(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to an agent.
        
        Args:
            agent_id: ID of the agent
            message: Message to send
            
        Returns:
            Dict[str, Any]: Response from the agent
        """
        pass
        
    def get_agent_state(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the current state of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dict[str, Any]: Agent state dictionary
        """
        pass
```

### `AgentFactory` Interface

Creates and configures bandmate agents:

```python
class AgentFactory:
    """Creates and configures bandmate agents."""
    
    def create_drummer_agent(self, responsiveness: float = 0.7) -> str:
        """
        Create a drummer agent.
        
        Args:
            responsiveness: How responsive the agent is to changes (0.0 to 1.0)
            
        Returns:
            str: Agent ID
        """
        pass
        
    def create_bassist_agent(self, responsiveness: float = 0.8) -> str:
        """
        Create a bassist agent.
        
        Args:
            responsiveness: How responsive the agent is to changes (0.0 to 1.0)
            
        Returns:
            str: Agent ID
        """
        pass
        
    def create_keyboardist_agent(self, responsiveness: float = 0.6) -> str:
        """
        Create a keyboardist agent.
        
        Args:
            responsiveness: How responsive the agent is to changes (0.0 to 1.0)
            
        Returns:
            str: Agent ID
        """
        pass
        
    def create_custom_agent(self, agent_type: str, personality: Dict[str, Any], 
                           responsiveness: float = 0.7) -> str:
        """
        Create a custom agent.
        
        Args:
            agent_type: Type of agent
            personality: Personality configuration
            responsiveness: How responsive the agent is to changes (0.0 to 1.0)
            
        Returns:
            str: Agent ID
        """
        pass
```

### `AgentCommunication` Interface

Handles communication between bandmate agents:

```python
class AgentCommunication:
    """Handles communication between bandmate agents."""
    
    def register_agent(self, agent_id: str, agent_type: str) -> None:
        """
        Register an agent for communication.
        
        Args:
            agent_id: ID of the agent
            agent_type: Type of agent
        """
        pass
        
    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from communication.
        
        Args:
            agent_id: ID of the agent
        """
        pass
        
    def broadcast_message(self, sender_id: str, message_type: str, 
                         message_data: Dict[str, Any]) -> None:
        """
        Broadcast a message to all agents.
        
        Args:
            sender_id: ID of the sending agent
            message_type: Type of message
            message_data: Message data
        """
        pass
        
    def send_direct_message(self, sender_id: str, receiver_id: str, 
                           message_type: str, message_data: Dict[str, Any]) -> None:
        """
        Send a direct message to a specific agent.
        
        Args:
            sender_id: ID of the sending agent
            receiver_id: ID of the receiving agent
            message_type: Type of message
            message_data: Message data
        """
        pass
        
    def register_message_handler(self, agent_id: str, message_type: str, 
                                handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            agent_id: ID of the agent
            message_type: Type of message to handle
            handler: Handler function
        """
        pass
```

## Integration with Existing Components

### Updated `AnimationController` Interface

```python
class AnimationController:
    """Animation Controller for sending animation commands to the rendering machine."""
    
    def __init__(self, blender_mcp_adapter: BlenderMCPAdapter = None, 
                host: str = "127.0.0.1", port: int = 12000, protocol: str = "osc"):
        """
        Initialize the animation controller.
        
        Args:
            blender_mcp_adapter: Blender MCP adapter instance
            host: IP address of the rendering machine (fallback)
            port: Port number for communication (fallback)
            protocol: Communication protocol (fallback)
        """
        pass
        
    # Existing methods...
    
    def use_mcp(self, use: bool = True) -> None:
        """
        Enable or disable MCP usage.
        
        Args:
            use: Whether to use MCP (True) or fallback (False)
        """
        pass
```

### Updated `MidiGenerator` Interface

```python
class MidiGenerator:
    """MIDI Generator for converting note data to MIDI messages."""
    
    def __init__(self, ableton_mcp_adapter: AbletonMCPAdapter = None, 
                port_name: Optional[str] = None):
        """
        Initialize the MIDI generator.
        
        Args:
            ableton_mcp_adapter: Ableton MCP adapter instance
            port_name: Name of the MIDI output port to use (fallback)
        """
        pass
        
    # Existing methods...
    
    def use_mcp(self, use: bool = True) -> None:
        """
        Enable or disable MCP usage.
        
        Args:
            use: Whether to use MCP (True) or fallback (False)
        """
        pass
```

### Updated `BandmateAgent` Interface

```python
class BandmateAgent(abc.ABC):
    """Base class for AI bandmate agents."""
    
    def __init__(self, agent_type: str, responsiveness: float = 0.7, 
                adk_agent_id: Optional[str] = None):
        """
        Initialize the bandmate agent.
        
        Args:
            agent_type: Type of agent (e.g., "drums", "bass", "keys")
            responsiveness: How responsive the agent is to changes (0.0 to 1.0)
            adk_agent_id: ID of the associated ADK agent (if any)
        """
        pass
        
    # Existing methods...
    
    def use_adk(self, use: bool = True) -> None:
        """
        Enable or disable ADK usage.
        
        Args:
            use: Whether to use ADK (True) or local implementation (False)
        """
        pass
```

### Updated `SessionManager` Interface

```python
class SessionManager:
    """Central coordinator for the agent system."""
    
    def __init__(self, update_rate: float = 30.0, 
                adk_manager: Optional[GoogleADKManager] = None):
        """
        Initialize the Session Manager.
        
        Args:
            update_rate: Update rate in Hz
            adk_manager: Google ADK manager instance
        """
        pass
        
    # Existing methods...
    
    def use_adk(self, use: bool = True) -> None:
        """
        Enable or disable ADK usage.
        
        Args:
            use: Whether to use ADK (True) or local implementation (False)
        """
        pass