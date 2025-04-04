# Technical Context: Performance Suite

## Technologies Used

### Programming Languages
- **Python**: Primary language for agent system and audio processing
- **C++**: Performance-critical components and audio analysis
- **C#/GDScript/Blueprint**: Game engine scripting (depending on chosen engine)
- **JavaScript/TypeScript**: Web-based control interfaces (if applicable)

### Frameworks & Libraries
- **NumPy/SciPy**: Scientific computing and signal processing
- **librosa**: Audio analysis and feature extraction
- **pytorch/tensorflow**: Machine learning for musical analysis and generation
- **python-osc**: OSC communication protocol implementation
- **mido**: MIDI message handling
- **AbletonOSC**: Interface with Ableton Live
- **websockets**: WebSocket communication

### Software Integrations
- **Ableton Live**: Sound generation engine and audio workstation
- **Game Engine**: Godot/Unity/Unreal for visual rendering
- **Max/MSP**: Optional for custom audio processing modules

### Hardware
- **Audio Interface**: Quantum 2626 or similar professional audio interface
- **Control Surface**: MIDI controllers, OSC-compatible devices
- **Processing Machine**: Mac Mini M4/Pro or equivalent
- **Rendering Machine**: High-end Mac or Nvidia PC
- **Display System**: Projectors, screens for visual output

## Development Setup

### Environment Configuration
- **Python Environment**: venv or conda for dependency management
- **Build System**: CMake for C++ components
- **Version Control**: Git with GitHub/GitLab
- **CI/CD**: GitHub Actions or similar for automated testing
- **Documentation**: Sphinx for Python, Doxygen for C++

### Development Workflow
1. Local development with simulated inputs
2. Integration testing with recorded audio samples
3. Hardware-in-the-loop testing with actual audio interface
4. Full system testing with both machines

### Testing Framework
- **Unit Tests**: pytest for Python, Google Test for C++
- **Integration Tests**: Custom test harness for agent interaction
- **Performance Tests**: Benchmarking suite for latency measurement
- **Audio Quality Tests**: Objective and subjective evaluation metrics

## Technical Constraints

### Latency Requirements
- **Audio Analysis Path**: < 50ms from input to analysis results
- **Agent Decision Making**: < 100ms from analysis to decision
- **MIDI Generation**: < 20ms from decision to MIDI output
- **Animation Control**: < 50ms from musical event to animation command
- **Visual Rendering**: Consistent 60fps minimum

### Resource Limitations
- **CPU Usage**: Must leave headroom for Ableton Live on Machine 1
- **Memory Usage**: < 8GB on Machine 1, < 16GB on Machine 2
- **Network Bandwidth**: < 10Mbps between machines
- **Storage Requirements**: < 100GB for full system installation

### Compatibility Requirements
- **OS Support**: macOS (Machine 1), macOS/Windows (Machine 2)
- **Ableton Version**: Live 11+ with Max for Live
- **Audio Interface**: Class-compliant or with appropriate drivers
- **Display Output**: Standard HDMI/DisplayPort connections

## Dependencies

### External Dependencies
- **Ableton Live**: Commercial software, requires license
- **Game Engine**: Depends on chosen engine (Godot is open-source, Unity/Unreal have licensing requirements)
- **Audio Interface Drivers**: Vendor-specific, required for low-latency operation
- **Python Packages**: Available via pip/conda
- **C++ Libraries**: Managed via CMake

### Internal Dependencies
- **Agent Communication Protocol**: Custom protocol for inter-agent communication
- **Animation Control Protocol**: Standardized message format for animation commands
- **Musical Context Model**: Shared data structure for musical state representation
- **Configuration System**: Central configuration management for all components

## Tool Usage Patterns

### Development Tools
- **IDE**: VSCode with Python and C++ extensions
- **Debugging**: pdb for Python, gdb/lldb for C++
- **Profiling**: cProfile for Python, Instruments (macOS) for system profiling
- **Audio Analysis**: Sonic Visualiser for audio feature inspection
- **MIDI Monitoring**: MIDI Monitor for debugging MIDI messages

### Deployment Tools
- **Packaging**: PyInstaller for Python applications
- **Configuration Management**: YAML/JSON for system configuration
- **Logging**: Structured logging with rotation and remote aggregation
- **Monitoring**: Real-time performance metrics dashboard

### Performance Optimization
- **Hotspot Analysis**: Identifying performance bottlenecks
- **Parallelization**: Multi-threading for CPU-intensive tasks
- **Memory Profiling**: Tracking memory usage patterns
- **Latency Measurement**: Custom tools for end-to-end latency analysis
