# Performance Suite

A comprehensive system for live musical performances, integrating audio processing, MIDI generation, and visual components. The system enables real-time interaction between a human performer and AI-driven virtual bandmates, creating an immersive audio-visual performance experience.

## Overview

The Performance Suite is designed to bridge the gap between solo performers and full band experiences, enabling musicians to create rich, multi-instrumental performances without requiring additional human bandmates. By leveraging AI-driven virtual musicians, the system allows for dynamic, responsive musical collaboration that adapts to the performer's style and direction in real-time.

## System Architecture

The Performance Suite follows a distributed architecture split across two machines:

- **Machine 1: Processing & Audio** (e.g., Mac Mini M4/Pro)
  - Handles all real-time audio processing and analysis
  - Runs the AI agent system for musical decision-making
  - Generates MIDI data to control Ableton Live
  - Sends animation control data to Machine 2
  - Manages performer input (audio and control surfaces)

- **Machine 2: Rendering** (e.g., High-End Mac/Nvidia PC)
  - Dedicated to visual rendering tasks
  - Receives animation control data from Machine 1
  - Manages 3D avatars and their animations
  - Renders the visual output for display
  - Handles visual effects and scene management

## Key Features

- Real-time audio analysis and musical context recognition
- AI-driven virtual bandmates with distinct musical personalities
- MIDI generation for controlling Ableton Live instruments
- Visual representation of virtual bandmates through animated avatars
- Low-latency communication between audio and visual components
- Intuitive control interface for performer direction

## Project Status

The Performance Suite project is currently in the initial planning and architecture phase. See the [memory-bank](memory-bank/) directory for detailed documentation on the project's current status, architecture, and plans.

## Documentation

Comprehensive documentation is maintained in the [memory-bank](memory-bank/) directory:

- [Project Brief](memory-bank/projectbrief.md): Core requirements and goals
- [Product Context](memory-bank/productContext.md): Purpose and user experience goals
- [System Patterns](memory-bank/systemPatterns.md): Architecture and design patterns
- [Technical Context](memory-bank/techContext.md): Technologies and development setup
- [Progress](memory-bank/progress.md): Current status and implementation timeline
- [Testing Strategy](memory-bank/testingStrategy.md): Testing approach and quality assurance
