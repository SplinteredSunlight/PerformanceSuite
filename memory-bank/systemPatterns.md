# System Patterns: Performance Suite

## System Architecture

The Performance Suite follows a distributed architecture split across two machines with optional MCP server integration:

```mermaid
graph TD
    subgraph Machine 1 [Processing & Audio - e.g., Mac Mini M4/Pro]
        direction LR
        PerformerIn[Performer Input (Audio Interface: Quantum 2626, Control Surface)]
        Ableton[Ableton Live (Sound Generation Engine)]
        subgraph Python Agents
            AA[Audio Analysis Agent]
            SM[Session Manager Agent]
            CA[Control Interface Agent]
            BA_Group{Bandmate Agents (Drums, Bass...)}
            MIDI_Gen[MIDI Generation Agent (controls Ableton)]
            Anim_Ctrl[Animation Control Agent]
            Stage_Vis[Stage Visuals Agent (Optional)]
        end
        PerformerIn -- Audio Stream --> AA;
        PerformerIn -- MIDI/OSC Control --> CA;
        AA -- Analysis Results (Chord, Tempo, Dynamics) --> SM;
        CA -- Performer Commands --> SM;
        SM -- Unified Musical Context --> BA_Group;
        BA_Group -- Musical Plans --> MIDI_Gen;
        BA_Group -- Animation Plans --> Anim_Ctrl;
        SM -- High-Level Cues --> Stage_Vis;
        MIDI_Gen -- AbletonOSC Commands --> Ableton;
        Ableton -- Master Audio Out --> PA_System;
        Anim_Ctrl -- OSC/WebSocket Commands --> Network;
        Stage_Vis -- DMX/OSC Commands --> Network;
    end

    subgraph Machine 2 [Rendering - e.g., High-End Mac/Nvidia PC]
        direction LR
        subgraph Game Engine [Godot/Unity/Unreal]
            Listener[OSC/WebSocket Listener Script]
            SceneMgr[Scene Manager Script (Engine Logic)]
            AvatarLoader[Avatar Loader (.glb)]
            AnimPlayer[Animation State Machine/Player]
            ShapeKeyCtrl[Shape Key Controller Script]
            Renderer[Real-time Renderer]
        end
        Network -- OSC/WebSocket Commands --> Listener;
        Listener -- Parsed Commands --> SceneMgr;
        SceneMgr -- Controls --> AvatarLoader;
        SceneMgr -- Controls --> AnimPlayer;
        SceneMgr -- Controls --> ShapeKeyCtrl;
        Renderer -- Rendered Video --> Display;
    end

    subgraph Outputs
      PA_System[PA System / Monitors]
      Display[Projector / Screens]
      Lights[DMX Lighting Rig (Optional)]
    end

    Network -- DMX/OSC Commands --> Lights;
    
    subgraph MCP Servers [Optional]
        Animation_MCP[Animation Control Server]
        Musical_AI_MCP[Musical AI Server]
    end
    
    Anim_Ctrl -- Animation Parameters --> Animation_MCP
    Animation_MCP -- Enhanced Animation Data --> Listener
    SM -- Musical Context --> Musical_AI_MCP
    Musical_AI_MCP -- Enhanced Musical Decisions --> BA_Group
```

### Machine 1: Processing & Audio
- Handles all real-time audio processing and analysis
- Runs the AI agent system for musical decision-making
- Generates MIDI data to control Ableton Live
- Sends animation control data to Machine 2
- Manages performer input (audio and control surfaces)

### Machine 2: Rendering
- Dedicated to visual rendering tasks
- Receives animation control data from Machine 1
- Manages 3D avatars and their animations
- Renders the visual output for display
- Handles visual effects and scene management

### MCP Servers (Optional)
- Provide enhanced AI capabilities while maintaining low latency
- Animation Control Server: Generates sophisticated animation data
- Musical AI Server: Enhances musical decision-making

## Key Technical Decisions

1. **Agent-Based Architecture**:
   - Multiple specialized agents with distinct responsibilities
   - Centralized Session Manager for coordination
   - Event-driven communication between agents

2. **OSC/WebSocket Communication**:
   - Open Sound Control (OSC) for low-latency musical control
   - WebSockets for more complex data structures when latency is less critical
   - Standardized message formats for interoperability

3. **Ableton Live Integration**:
   - AbletonOSC for reliable communication with Ableton
   - MIDI mapping for direct control of instruments and effects
   - Audio routing through professional audio interface

4. **Game Engine Rendering**:
   - Godot/Unity/Unreal for high-quality real-time rendering
   - GLSL/HLSL shaders for custom visual effects
   - Optimized for performance on dedicated rendering hardware

5. **Modular Component Design**:
   - Loosely coupled components with well-defined interfaces
   - Plug-and-play architecture for different agent types
   - Configurable system to adapt to different performance needs

6. **MCP Server Integration**:
   - Model Context Protocol servers for enhanced AI capabilities
   - Separate servers for animation and musical intelligence
   - Designed for ultra-low latency (<1ms processing time)
   - Graceful degradation if servers become unavailable

## Design Patterns

1. **Observer Pattern**:
   - Used for event notification between agents
   - Session Manager observes all agent activities
   - Allows for reactive behavior based on system events

2. **Strategy Pattern**:
   - Different musical generation strategies based on context
   - Swappable animation strategies for different visual styles
   - Configurable processing strategies for different audio inputs

3. **Factory Pattern**:
   - Dynamic creation of agent instances
   - Runtime generation of musical patterns
   - Creation of visual elements based on performance context

4. **Command Pattern**:
   - Encapsulation of performer instructions
   - Queueable commands for timing-sensitive operations
   - Undoable operations for rehearsal scenarios

5. **State Machine**:
   - Management of performance states (intro, verse, chorus, etc.)
   - Animation state management for avatars
   - System mode transitions (setup, rehearsal, performance)

6. **Graceful Degradation Pattern**:
   - Defined degradation levels for system components
   - Automatic fallback to simpler processing when needed
   - Prioritization of audio functionality over visual complexity

## Component Relationships

### Audio Analysis Chain:
```
Audio Input → Signal Processing → Feature Extraction → Musical Context Analysis → Agent Decision Making
```

### Control Flow:
```
Performer Input → Control Interface Agent → Session Manager → Bandmate Agents → MIDI Generation → Ableton Live
```

### Animation Pipeline:
```
Musical Events → Animation Control Agent → Animation MCP Server → OSC/WebSocket → Rendering Machine → Avatar Animation System → Display
```

### MCP Musical Intelligence Path:
```
Audio Analysis Agent → Session Manager → Musical Context → Musical AI MCP Server → Enhanced Musical Decisions → Bandmate Agents
```

## Critical Implementation Paths

1. **Audio Analysis Path**:
   - Critical for responsive musical interaction
   - Must maintain sub-3ms latency from input to analysis results
   - Requires efficient signal processing algorithms

2. **MIDI Generation Path**:
   - Translates agent decisions into playable MIDI
   - Must synchronize precisely with tempo and musical structure
   - Requires robust error handling to prevent performance disruption

3. **Inter-Machine Communication**:
   - Must maintain reliable, low-latency connection between machines
   - Requires efficient serialization of complex animation data
   - Needs fault tolerance for network hiccups

4. **Rendering Pipeline**:
   - Must maintain consistent frame rate (60fps minimum) for smooth visual experience
   - Requires optimization for real-time performance
   - Needs synchronization with audio events for convincing performance

5. **MCP Server Communication**:
   - Must maintain sub-1ms round-trip time for MCP server requests
   - Requires efficient binary serialization for data exchange
   - Needs automatic failover mechanisms if servers become unresponsive

## Latency Budgeting

| Component | Maximum Latency Budget |
|-----------|------------------------|
| Audio Interface Input | 0.5ms |
| Audio Analysis | 2.0ms |
| Agent Processing | 1.0ms |
| Musical AI MCP Processing | 0.5ms |
| MIDI Generation | 1.0ms |
| Ableton Processing | 1.0ms |
| Audio Interface Output | 0.5ms |
| Network Transit (inter-machine) | 0.5ms |
| Network Transit (to/from MCP) | 0.5ms |
| OSC Processing | 0.5ms |
| Animation MCP Processing | 0.5ms |
| Animation Processing | 1.0ms |
| Rendering | 0.5ms |
| **Total End-to-End** | **10.0ms** |
