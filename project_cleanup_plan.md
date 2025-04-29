# Project Cleanup and Refocus Plan

This document outlines the steps to clean up the PerformanceSuite project and ensure we're on track with the core functionality.

## 1. Remove Unnecessary Test Files and Directories

```mermaid
graph TD
    A[Remove Unnecessary Files] --> B[Test Directories]
    A --> C[Test Files]
    A --> D[Error Logs]
    
    B --> B1[test_dir/]
    B --> B2[retrieved_test_dir/]
    
    C --> C1[retrieved_file1.txt]
    C --> C2[test_transfer.txt]
    
    D --> D1[server.log]
```

### Files to Remove:
- `test_dir/` directory and its contents
- `retrieved_test_dir/` directory and its contents
- `retrieved_file1.txt` (test file)
- `test_transfer.txt` (test file for SCP transfer)
- `server.log` (error log for a missing server.py file)

## 2. Consolidate Redundant Scripts

```mermaid
graph TD
    A[Consolidate Scripts] --> B[Remote Setup Scripts]
    A --> C[Remote Client Scripts]
    
    B --> B1[Keep remote_control_mcp.py]
    B --> B2[Merge simple_remote_setup.py]
    B --> B3[Merge minimal_remote_setup.py]
    
    C --> C1[Keep remote_control_client.py]
    C --> C2[Merge remote_client.py]
```

### Scripts to Consolidate:
1. **Remote Setup Scripts**:
   - Keep `setup_mac_studio_remote.py` as the main setup script
   - Merge functionality from `simple_remote_setup.py` and `minimal_remote_setup.py`
   - Document the consolidated script

2. **Remote Client Scripts**:
   - Keep `remote_control_client.py` as the main client (more feature-rich MCP client)
   - Remove `remote_client.py` (simpler version with less functionality)

## 3. Organize Scripts Directory

```mermaid
graph TD
    A[Organize Scripts] --> B[Core Scripts]
    A --> C[Test Scripts]
    A --> D[Utility Scripts]
    
    B --> B1[remote_control_mcp.py]
    B --> B2[setup_mac_studio_remote.py]
    B --> B3[remote_control_client.py]
    B --> B4[task_manager_mcp.py]
    B --> B5[github_desktop_mcp.py]
    B --> B6[restart_dashboard.sh]
    
    C --> C1[test_audio_analysis.py]
    C --> C2[test_osc_receiver.py]
    C --> C3[test_osc_sender.py]
    C --> C4[test_remote_control.py]
    
    D --> D1[discover_mac_studio.py]
    D --> D2[mac_studio_connect.sh]
    D --> D3[mac_studio_transfer.sh]
    D --> D4[simulate_midi.py]
```

### Script Organization:
- Create README.md in the scripts directory explaining the purpose of each script
- Group scripts by functionality in the README

## 4. Update Project Documentation

```mermaid
graph TD
    A[Update Documentation] --> B[Update Memory Bank]
    A --> C[Update README.md]
    
    B --> B1[Update activeContext.md]
    B --> B2[Update progress.md]
    
    C --> C1[Document Project Structure]
    C --> C2[Document Setup Process]
    C --> C3[Document Development Workflow]
```

### Documentation Updates:
1. **Memory Bank Updates**:
   - Update `activeContext.md` to reflect the cleanup and current focus
   - Update `progress.md` to mark completed tasks and add the cleanup task

2. **README.md Updates**:
   - Ensure the main README.md clearly explains the project structure
   - Document the two-machine setup process
   - Document the development workflow

## 5. Focus on Core Functionality

```mermaid
graph TD
    A[Core Functionality Focus] --> B[Audio Analysis]
    A --> C[Two-Machine Setup]
    A --> D[Agent System]
    
    B --> B1[Enhance AudioInputHandler]
    B --> B2[Create Testing Framework]
    
    C --> C1[Optimize Network Communication]
    C --> C2[Ensure Reliable Remote Control]
    
    D --> D1[Enhance SessionManager]
    D --> D2[Develop Bandmate Agents]
```

### Core Functionality Priorities:
1. **Audio Analysis**:
   - Enhance `AudioInputHandler` for Quantum 2626 (optimize buffer size for <10ms latency)
   - Create audio analysis testing framework

2. **Two-Machine Setup**:
   - Ensure reliable communication between Mac Mini and Mac Studio
   - Optimize network settings for low-latency OSC communication

3. **Agent System**:
   - Enhance `SessionManager` implementation
   - Develop basic bandmate agents

## 6. Implementation Steps

1. **Cleanup Phase**:
   ```bash
   # Remove test directories and files
   rm -rf test_dir/ retrieved_test_dir/
   rm retrieved_file1.txt test_transfer.txt server.log
   
   # Consolidate scripts
   # (This will be done in the Code mode)
   ```

2. **Documentation Phase**:
   ```bash
   # Update Memory Bank
   # (This will be done in the Code mode)
   ```

3. **Core Functionality Phase**:
   ```bash
   # Focus on enhancing AudioInputHandler
   # Create audio analysis testing framework
   # Enhance SessionManager
   # (This will be done in the Code mode)
   ```

## 7. Success Criteria

- Project directory is clean and well-organized
- Documentation is up-to-date and reflects the current state
- Core functionality is working reliably
- Two-machine setup is stable and performant
- Audio analysis pipeline is optimized for low latency