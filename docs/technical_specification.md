# Performance Suite: Comprehensive Technical Specification

## Table of Contents
1. [System Overview](#system-overview)
2. [Performance Requirements](#performance-requirements)
3. [Hardware Architecture](#hardware-architecture)
4. [Software Architecture](#software-architecture)
5. [MCP Servers Integration](#mcp-servers-integration)
6. [Network Configuration](#network-configuration)
7. [Data Flow and Signal Processing](#data-flow-and-signal-processing)
8. [Initialization and Synchronization Protocols](#initialization-and-synchronization-protocols)
9. [Error Handling and Recovery](#error-handling-and-recovery)
10. [Monitoring and Diagnostics](#monitoring-and-diagnostics)
11. [Testing Procedures](#testing-procedures)
12. [Appendix: Component Configuration](#appendix-component-configuration)

## System Architecture Diagram

```mermaid
graph TD
    subgraph Machine 1 (Processing & Audio - e.g., Mac Mini M4/Pro)
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

    subgraph Machine 2 (Rendering - e.g., High-End Mac/Nvidia PC)
        direction LR
        subgraph Game Engine (Godot/Unity/Unreal)
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
```

## System Overview

The Performance Suite combines real-time audio processing, AI-driven musical accompaniment, and synchronized visual rendering to create an integrated multimedia performance environment. The system is designed for professional live performance scenarios where ultra-low latency (under 10ms end-to-end) is critical.

### Design Philosophy
- **Performance First**: All system decisions prioritize real-time performance and low latency
- **Fault Tolerance**: Graceful degradation rather than catastrophic failure
- **Modularity**: Components can be upgraded or replaced individually
- **Scalability**: Architecture supports expansion from small to large-scale performances

## Performance Requirements

### Latency Requirements
- **End-to-End System Latency**: <10ms from performer input to audiovisual output
- **Audio Processing Latency**: <3ms from input to output
- **Network Transit Latency**: <1ms between machines
- **Visual Rendering Latency**: <6ms from receiving commands to display update

### Processing Requirements
- **Audio Sample Rate**: 96kHz minimum
- **Visual Frame Rate**: 60fps minimum
- **Control Message Rate**: 1000Hz minimum for critical performance parameters

## Hardware Architecture

### Two-Machine Deployment

#### Machine 1 (Processing & Audio)
- **Recommended Hardware**: Apple Mac Mini M4/Pro or equivalent
- **CPU**: 10+ CPU cores
- **Memory**: 32GB RAM minimum, 64GB recommended
- **Storage**: 1TB NVMe SSD minimum (3000MB/s+ read/write)
- **Audio Interface**: PreSonus Quantum 2626 Thunderbolt 3 audio interface
- **Network**: 10Gbps Ethernet preferred, 1Gbps minimum
- **Control Surface**: OSC/MIDI compatible control surface (specific models TBD)

#### Machine 2 (Rendering)
- **Recommended Hardware**: High-end Mac or Nvidia-based PC
- **CPU**: Latest generation Intel i9/AMD Ryzen 9 or Apple Silicon equivalent
- **GPU**: RTX 4080 or higher for PC, or highest-tier Apple Silicon GPU
- **Memory**: 32GB RAM minimum, 64GB recommended
- **Storage**: 2TB NVMe SSD minimum (5000MB/s+ read/write)
- **Network**: 10Gbps Ethernet preferred, 1Gbps minimum
- **Display Output**: HDMI 2.1 or DisplayPort 1.4 for high-resolution output

### Output Systems
- **PA System**: Professional audio amplification and speakers
- **Display**: Projector(s) or LED screens with minimum 1080p resolution, 4K preferred
- **Lighting**: Optional DMX lighting rig for synchronized light effects

## Software Architecture

### Machine 1 Components

#### Core Audio System
- **DAW**: Ableton Live (with optimized configuration for low latency)
- **Plugins**: Minimalist setup with native or low-latency plugins only
- **Audio Routing**: Internal routing via Ableton or external via audio interface

#### Python Agent System
1. **Audio Analysis Agent**
   - Real-time analysis of incoming audio (chord detection, tempo, dynamics)
   - Implements FFT and other DSP algorithms optimized for minimal latency
   - Outputs structured analysis data to Session Manager

2. **Session Manager Agent**
   - Central coordination system for all agents
   - Maintains global musical context and performance state
   - Routes commands and data between agents
   - Handles synchronization between audio and visual components

3. **Control Interface Agent**
   - Processes input from performer's control surface
   - Translates physical controls to internal command structure
   - Provides feedback to performer through control surface

4. **Bandmate Agents**
   - Individual agents for different virtual instruments (drums, bass, etc.)
   - AI-driven musical decision making based on performer input
   - Generates musical parts appropriate to current performance context

5. **MIDI Generation Agent**
   - Translates musical decisions from Bandmate Agents to MIDI
   - Communicates with Ableton Live via AbletonOSC
   - Handles timing and synchronization of generated parts

6. **Animation Control Agent**
   - Translates musical activity to animation parameters
   - Generates OSC messages for visual system
   - Synchronizes animation timing with audio events

7. **Stage Visuals Agent (Optional)**
   - Controls additional stage elements (lighting, video)
   - Generates DMX, OSC, or other control signals
   - Synchronizes environmental effects with performance

### Machine 2 Components

#### Game Engine System (Godot/Unity/Unreal)
1. **OSC/WebSocket Listener Script**
   - Receives network commands from Machine 1 and MCP servers
   - Maintains real-time communication channels
   - Buffers and prioritizes incoming commands
   - Routes MCP animation data to appropriate subsystems

2. **Scene Manager Script**
   - Core logic for visual rendering decisions
   - Manages resources and rendering priorities
   - Controls loading and unloading of visual assets
   - Coordinates between traditional and MCP-driven animations

3. **Avatar Loader**
   - Handles 3D character models (.glb format)
   - Manages model LOD (Level of Detail) based on performance needs
   - Pre-loads and caches avatar resources
   - Ensures rigging compatibility with MCP-generated animations

4. **Animation State Machine/Player**
   - Controls character animations based on musical input
   - Handles blending between animation states
   - Synchronizes animation timing with audio events
   - Integrates with MCP-generated animation data

5. **Shape Key Controller Script**
   - Manages facial animations and microexpressions
   - Controls morph targets for expressive character features
   - Synchronizes lip syncing or other precise animations
   - Applies MCP-generated facial expressions

6. **Real-time Renderer**
   - Handles final output rendering
   - Manages shaders and visual effects
   - Optimizes for frame rate and visual quality

## MCP Servers Integration

### Overview
Model Context Protocol (MCP) servers provide a powerful framework for real-time AI-driven content generation and state management. For the Performance Suite, MCP servers can enhance several key components while maintaining the sub-10ms latency requirement.

### Primary MCP Server Applications

#### Animation and Rigging System
- **Dedicated MCP Server**: Animation Control Server
- **Purpose**: Bridge between Animation Control Agent and Game Engine animation systems
- **Key Functions**:
  - Real-time skeletal animation generation based on musical parameters
  - Procedural character motion that responds organically to performance
  - Advanced blending between animation states with context awareness
  - Facial animation and expression generation synchronized with music
- **Latency Budget**: 1ms within the existing Animation Processing budget
- **Hardware Requirements**: 
  - Dedicated CPU cores (2-4 cores minimum)
  - 8GB RAM allocation
  - Can be hosted on Machine 2 if resources permit

#### Bandmate Intelligence System
- **Dedicated MCP Server**: Musical AI Server
- **Purpose**: Enhance the musical decision-making of Bandmate Agents
- **Key Functions**:
  - Contextual understanding of musical structure and progression
  - Stylistic adaptation based on performer's playing
  - Dynamic response to changing performance parameters
  - Memory of motifs and themes for musical callback and development
- **Latency Budget**: 1ms within the existing Agent Processing budget
- **Hardware Requirements**:
  - Dedicated CPU cores (4-6 cores minimum)
  - 16GB RAM allocation
  - Preferably hosted on separate hardware for optimal performance

### MCP Server Architecture

#### Server Configuration
- **Server Framework**: Node.js or Python-based
- **Communication Protocol**: Binary WebSocket for low-latency messaging
- **State Management**: In-memory with periodic persistence to disk
- **Scaling Strategy**: Vertical scaling for latency-sensitive operations

#### Integration Points
1. **Animation MCP Server**:
   - **Input**: OSC messages from Animation Control Agent (Machine 1)
   - **Output**: Enhanced animation parameters to OSC/WebSocket Listener (Machine 2)
   - **Connection**: Direct network link with dedicated ports

2. **Musical AI MCP Server**:
   - **Input**: Musical context data from Session Manager (Machine 1)
   - **Output**: Enhanced musical decisions to Bandmate Agents (Machine 1)
   - **Connection**: Could be local to Machine 1 or networked if separate hardware

## Network Configuration

### Physical Configuration
- **Connection Type**: Wired Ethernet (CAT6a or better)
- **Network Switch**: Dedicated gigabit or 10G switch (no other devices)
- **IP Configuration**: Static IP addresses (192.168.1.x subnet)
- **MTU Size**: 9000 (Jumbo frames) if supported by all components

### Protocol Configuration
- **Primary Protocol**: OSC (Open Sound Control) over UDP
- **Message Format**: Binary with minimal overhead
- **Port Assignments**:
  - 8000: Primary control messages
  - 8001: Animation control
  - 8002: Synchronization messages
  - 8003: Monitoring and status
  - 8004-8010: Reserved for future expansion

### Quality of Service
- **Packet Prioritization**: Critical sync messages get highest priority
- **Traffic Shaping**: Bandwidth reservation for critical message types
- **Redundancy**: Critical messages sent twice with sequence numbers for deduplication

## Data Flow and Signal Processing

### Audio Signal Path
1. Performer input → Audio Interface → Audio Analysis Agent
2. Audio Analysis Agent → Session Manager → Bandmate Agents
3. Bandmate Agents → MIDI Generation Agent → Ableton Live
4. Ableton Live → Audio Interface → PA System

### Control Signal Path
1. Performer Control Surface → Control Interface Agent
2. Control Interface Agent → Session Manager
3. Session Manager → Appropriate Bandmate Agent
4. Bandmate Agent → MIDI Generation Agent and/or Animation Control Agent

### Animation Signal Path
1. Animation Control Agent → Network → Animation MCP Server
2. Animation MCP Server → Enhanced Animation Data → OSC Listener (Machine 2)
3. OSC Listener → MCP Animation Integration Module
4. MCP Animation Integration Module → Scene Manager
5. Scene Manager → Animation State Machine and/or Shape Key Controller
6. Animation State Machine → Real-time Renderer → Display Output

### MCP Musical Intelligence Path
1. Audio Analysis Agent → Session Manager → Musical Context → Musical AI MCP Server
2. Musical AI MCP Server → Enhanced Musical Decisions → Bandmate Agents
3. Bandmate Agents → MIDI Generation Agent → Ableton Live

### Latency Budgeting
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

## Initialization and Synchronization Protocols

### System Boot Sequence
1. Start MCP servers (if on separate hardware)
2. Wait for MCP servers to initialize and enter ready state
3. Start Machine 2 (rendering system)
4. Initialize game engine and load base assets
5. Start OSC listener and enter standby mode
6. Establish connection with MCP servers and perform handshake
7. Start Machine 1 (audio system)
8. Initialize Ableton Live with empty session
9. Start Python agent system
10. Establish network connections between all components
11. Perform handshake to confirm connectivity
12. Synchronize system clocks across machines and MCP servers
13. Load performance-specific content
14. Verify MCP server responsiveness with test messages
15. Enter performance-ready state

### Clock Synchronization
- Initial PTP (Precision Time Protocol) sync between machines
- Continuous heartbeat messages with timestamps for drift correction
- Resync trigger available to performer if timing drifts during performance

### Asset Preloading
- All visual assets preloaded during initialization
- Audio samples and instruments preloaded in Ableton
- Memory-mapped files used where appropriate for large assets

## Error Handling and Recovery

### Error Detection
- Heartbeat monitoring between all system components, including MCP servers
- Performance metric monitoring (CPU, memory, latency)
- Automated detection of audio dropouts or frame rate issues
- MCP server response time monitoring with alerts for degradation
- Threshold alerts for approaching resource limits
- Animation quality metrics to detect MCP server performance issues

### Graceful Degradation Levels
1. **Level 0**: Full system functionality, all features enabled, MCP servers fully operational
2. **Level 1**: MCP servers in degraded mode (simplified processing), maintain full audio functionality
3. **Level 2**: MCP servers bypassed, use pre-computed animations, maintain full audio functionality
4. **Level 3**: Reduce visual complexity, maintain full audio functionality
5. **Level 4**: Simplify both audio and visuals, maintain core performance
6. **Level 5**: Minimal backup mode (basic audio and static visuals)

### Recovery Procedures
- **Component Restart**: Ability to restart individual agents without full system reboot
- **MCP Server Failover**: Automatic switching to backup MCP servers if primary servers fail
- **Degraded MCP Mode**: Fallback to simplified animation and musical patterns if MCP servers are underperforming
- **MCP-less Operation**: Complete fallback path for operation without MCP servers if necessary
- **State Restoration**: Automatic return to last known good state
- **Safe Modes**: Predefined configurations for recovery scenarios
- **Manual Override**: Emergency controls for technical operator

## Monitoring and Diagnostics

### Real-time Monitoring
- **Performance Dashboard**: Real-time display of system metrics
- **Latency Measurement**: Continuous monitoring of end-to-end latency
- **Resource Usage**: CPU, memory, network, and disk utilization
- **Audio Levels**: Signal level monitoring at key points in audio chain

### Logging System
- **Performance Logs**: Timestamped record of all performance events
- **Error Logs**: Detailed information on any detected issues
- **Resource Logs**: Historical tracking of system resource usage
- **Latency Logs**: Measurements of system timing performance

### Diagnostic Tools
- **Network Analyzer**: Tool to measure actual network performance
- **Latency Tester**: End-to-end system latency measurement
- **Component Tester**: Individual testing of each system component
- **Stress Tester**: Controlled performance degradation to test boundaries

## Testing Procedures

### Pre-Performance Testing
1. **System Boot Test**: Verify correct startup sequence including MCP servers
2. **MCP Server Test**: Verify MCP server responsiveness and correct operation
3. **Audio Pathway Test**: Verify audio signal integrity
4. **Visual Rendering Test**: Verify visual output quality and frame rate
5. **Animation Quality Test**: Verify MCP-driven animation quality and responsiveness
6. **Network Test**: Verify connection speed and packet transit times including MCP communication
7. **End-to-End Latency Test**: Measure total system response time
8. **MCP Failover Test**: Verify graceful degradation when MCP servers are unavailable
9. **Resource Headroom Test**: Verify sufficient system resources

### Latency Measurement Methodology
- **Audio Testing**: Loopback test from output to input with waveform analysis
- **Visual Testing**: High-speed camera capture of visual reaction to audio event
- **End-to-End Testing**: Click-to-flash test with measurement of elapsed time

### Performance Benchmarks
- **Audio Processing**: <3ms for full audio chain
- **Visual Rendering**: Stable 60fps minimum
- **Network Transit**: <1ms packet transit time
- **MCP Server Processing**: <1ms for animation calculations
- **MCP Network Round-trip**: <2ms for complete request-response cycle
- **Overall Responsiveness**: <10ms from input to output

## Appendix: Component Configuration

### Quantum 2626 Configuration
- **Sample Rate**: 96kHz
- **Buffer Size**: 32 samples (0.33ms @ 96kHz)
- **Bit Depth**: 24-bit
- **Input Channels**: Configured based on performer requirements
- **Direct Monitoring**: Enabled for zero-latency monitoring
- **DSP Effects**: Disabled during performance
- **Connection**: Thunderbolt 3

### Ableton Live Configuration
- **Audio Engine**: On
- **Sample Rate**: 96kHz
- **Buffer Size**: 64 samples or lower
- **Multicore Support**: On
- **Reduce Latency When Monitoring**: On
- **Plug-in Delay Compensation**: On
- **Process Audio During CPU Overloads**: Off
- **Render Ahead Time**: 1-2ms

### Python Environment Setup
- **Python Version**: 3.11+
- **Dependency Management**: Anaconda/Miniconda
- **Key Libraries**:
  - NumPy (with BLAS optimizations)
  - librosa (with numba acceleration)
  - python-osc
  - rtmidi
  - sounddevice
  - multiprocessing
  - pyliblo
  - python-rtmidi
  - websockets (for MCP server communication)
  - protobuf (for efficient binary serialization)
  - asyncio (for asynchronous communication with MCP servers)