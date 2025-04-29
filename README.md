# Performance Suite

A comprehensive system for live musical performances, integrating audio processing, MIDI generation, and visual components. The system enables real-time interaction between a human performer and AI-driven virtual bandmates, creating an immersive audio-visual performance experience.

## Overview

The Performance Suite is designed to bridge the gap between solo performers and full band experiences, enabling musicians to create rich, multi-instrumental performances without requiring additional human bandmates. By leveraging AI-driven virtual musicians, the system allows for dynamic, responsive musical collaboration that adapts to the performer's style and direction in real-time.

## System Architecture

The Performance Suite follows a distributed architecture split across two machines:

- **Machine 1: Processing & Audio** (Mac Mini M4)
  - Handles all real-time audio processing and analysis
  - Runs the AI agent system for musical decision-making
  - Generates MIDI data to control virtual instruments
  - Sends animation control data to Machine 2
  - Manages performer input (audio and control surfaces)
  - Connects to the Quantum 2626 audio interface

- **Machine 2: Rendering** (Mac Studio M4)
  - Dedicated to visual rendering tasks
  - Receives animation control data from Machine 1
  - Manages 3D avatars and their animations
  - Renders the visual output for display
  - Handles visual effects and scene management

## Key Features

- Real-time audio analysis and musical context recognition
- AI-driven virtual bandmates with distinct musical personalities
- MIDI generation for controlling virtual instruments
- Visual representation of virtual bandmates through animated avatars
- Low-latency communication between audio and visual components
- Intuitive control interface for performer direction

## Project Status

The Performance Suite project is currently in active development. See the [memory-bank](memory-bank/) directory for detailed documentation on the project's current status, architecture, and plans.

## Documentation

### Technical Documentation

- [Technical Specification](docs/technical_specification.md): Comprehensive technical details including system architecture, performance requirements, hardware specifications, and more.
- [Environment Setup Guide](docs/environment_setup_guide.md): Instructions for setting up the development environment.
- [Local Workflow](docs/local_only_workflow.md): Details on the local-only workflow for development.
- [Remote Control Setup](scripts/README_remote_control.md): Documentation for the two-machine remote control system.

### Memory Bank

Project context and development information is maintained in the [memory-bank](memory-bank/) directory:

- [Project Brief](memory-bank/projectbrief.md): Core requirements and goals
- [Product Context](memory-bank/productContext.md): Purpose and user experience goals
- [System Patterns](memory-bank/systemPatterns.md): Architecture and design patterns
- [Technical Context](memory-bank/techContext.md): Technologies and development setup
- [Progress](memory-bank/progress.md): Current status and implementation timeline
- [Active Context](memory-bank/activeContext.md): Current focus and recent changes
- [Testing Strategy](memory-bank/testingStrategy.md): Testing approach and quality assurance

### Development Resources

- **Scripts**: The [scripts](scripts/) directory contains utility scripts for testing and development
- **Schemas**: JSON schemas for data structures are located in [src/schemas](src/schemas/)

## Development

### Project Organization

The project is organized into several key components:

1. **Audio Analysis**: Processes real-time audio input and extracts musical features
   - Located in `src/audio_analysis/`
   - Key files: `analyzer.py`, `input_handler.py`

2. **Agent System**: Coordinates virtual musicians that respond to audio analysis
   - Located in `src/agent_system/`
   - Key files: `session_manager.py`, `bandmate_agent.py`

3. **MIDI Generation**: Creates MIDI output based on agent decisions
   - Located in `src/midi_generation/`
   - Key files: `midi_generator.py`

4. **Animation Control**: Manages the visual representation of virtual bandmates
   - Located in `src/animation_control/`
   - Key files: `animation_controller.py`

5. **Dashboard**: Provides a visual interface for monitoring the system
   - Located in `src/dashboard/`
   - Run with `scripts/restart_dashboard.sh`

### Two-Machine Setup

The project uses a two-machine architecture with the following setup:

1. **Mac Mini M4** (Audio Processing)
   - Runs the main PerformanceSuite application
   - Connects to the Quantum 2626 audio interface
   - Sends control messages to the Mac Studio

2. **Mac Studio M4** (Rendering)
   - Runs the rendering engine
   - Receives control messages from the Mac Mini
   - Generates visual output

Communication between machines is handled by:
- Remote control system (`scripts/remote_control_mcp.py` and `scripts/remote_control_client.py`)
- OSC communication for low-latency data transfer

### Task Management

The project uses a local task management system integrated with the Memory Bank:
- Tasks are tracked in the dashboard
- Task details are stored in the Memory Bank
- The task manager MCP server (`scripts/task_manager_mcp.py`) provides an interface for task management

### Contributing

Please see the [Contributing Guidelines](CONTRIBUTING.md) for information on how to contribute to the project.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
