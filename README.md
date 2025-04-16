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

### Technical Documentation

- [Technical Specification](docs/technical_specification.md): Comprehensive technical details including system architecture, performance requirements, hardware specifications, and more.
- [GitHub Project Setup](docs/github_project_setup.md): Instructions for setting up and configuring the GitHub Project for development tracking.
- [Manual GitHub Project Setup](docs/github_project_setup_manual.md): Manual setup instructions for GitHub Projects.
- [GitHub Project Setup Success](docs/github_project_setup_success.md): Details of the successfully configured GitHub Project.

### Memory Bank

Project context and development information is maintained in the [memory-bank](memory-bank/) directory:

- [Project Brief](memory-bank/projectbrief.md): Core requirements and goals
- [Product Context](memory-bank/productContext.md): Purpose and user experience goals
- [System Patterns](memory-bank/systemPatterns.md): Architecture and design patterns
- [Technical Context](memory-bank/techContext.md): Technologies and development setup
- [Progress](memory-bank/progress.md): Current status and implementation timeline
- [Testing Strategy](memory-bank/testingStrategy.md): Testing approach and quality assurance

### Development Resources

- **Scripts**: The [scripts](scripts/) directory contains utility scripts for testing and development
- **Schemas**: JSON schemas for data structures are located in [src/schemas](src/schemas/)

## Development

### GitHub Project

The project uses GitHub Projects for task management and tracking. The configuration includes:

- **Custom Fields**: Priority, Component, Effort, and Milestone
- **Views**: Board, Roadmap, Component, Priority, and All Items
- **Automation**: Workflows for issue and PR management

To set up the GitHub Project:

1. Follow the instructions in the [Manual GitHub Project Setup Guide](docs/github_project_setup_manual.md)
2. GitHub has deprecated the classic Projects API, but you can still automate with GraphQL:
   - Use `scripts/setup_github_project_graphql.py` to create a project with GraphQL
   - Use `.github/workflows/project-automation-graphql.yml` for automated project management
   - See the [GitHub Project Setup Success](docs/github_project_setup_success.md) document for details on the configured project

### Contributing

Please see the [Contributing Guidelines](CONTRIBUTING.md) for information on how to contribute to the project.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
