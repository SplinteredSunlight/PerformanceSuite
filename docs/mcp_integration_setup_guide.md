# MCP Integration Setup Guide

This guide provides instructions for setting up the MCP integration for the Performance Suite project.

## Prerequisites

Before beginning the MCP integration, ensure you have the following:

1. Access to the Blender MCP Server (blender-dynamic-mcp-vxai)
2. Access to the Ableton MCP Server (ableton-copilot-mcp)
3. Access to the Google ADK (Agent Development Kit)
4. Python 3.9+ installed
5. Git installed
6. Performance Suite repository cloned

## Directory Structure Setup

Create the following directory structure for the MCP integration:

```
src/
├── mcp_integration/
│   ├── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── interfaces.py
│   │   ├── connection_manager.py
│   │   └── error_handling.py
│   ├── blender/
│   │   ├── __init__.py
│   │   ├── blender_mcp_adapter.py
│   │   ├── animation_mapping.py
│   │   └── fallback_renderer.py
│   ├── ableton/
│   │   ├── __init__.py
│   │   ├── ableton_mcp_adapter.py
│   │   ├── midi_mapping.py
│   │   └── fallback_midi.py
│   └── google_adk/
│       ├── __init__.py
│       ├── adk_manager.py
│       ├── agent_factory.py
│       └── communication.py
```

You can create this structure manually or use the following commands:

```bash
# Create main directories
mkdir -p src/mcp_integration/common
mkdir -p src/mcp_integration/blender
mkdir -p src/mcp_integration/ableton
mkdir -p src/mcp_integration/google_adk

# Create __init__.py files
touch src/mcp_integration/__init__.py
touch src/mcp_integration/common/__init__.py
touch src/mcp_integration/blender/__init__.py
touch src/mcp_integration/ableton/__init__.py
touch src/mcp_integration/google_adk/__init__.py

# Create common module files
touch src/mcp_integration/common/interfaces.py
touch src/mcp_integration/common/connection_manager.py
touch src/mcp_integration/common/error_handling.py

# Create Blender module files
touch src/mcp_integration/blender/blender_mcp_adapter.py
touch src/mcp_integration/blender/animation_mapping.py
touch src/mcp_integration/blender/fallback_renderer.py

# Create Ableton module files
touch src/mcp_integration/ableton/ableton_mcp_adapter.py
touch src/mcp_integration/ableton/midi_mapping.py
touch src/mcp_integration/ableton/fallback_midi.py

# Create Google ADK module files
touch src/mcp_integration/google_adk/adk_manager.py
touch src/mcp_integration/google_adk/agent_factory.py
touch src/mcp_integration/google_adk/communication.py
```

## Dependencies Setup

Update the `requirements.txt` file to include the necessary dependencies for the MCP integration:

```
# Existing dependencies
# ...

# MCP Integration dependencies
mcp-client>=1.0.0
blender-mcp-client>=0.5.0
ableton-mcp-client>=0.5.0
google-adk>=1.0.0
```

Update the `setup.py` file to include the new dependencies:

```python
# Add to install_requires list
install_requires=[
    # Existing dependencies...
    'mcp-client>=1.0.0',
    'blender-mcp-client>=0.5.0',
    'ableton-mcp-client>=0.5.0',
    'google-adk>=1.0.0',
],
```

## MCP Server Configuration

### Blender MCP Server

Create a configuration file for the Blender MCP server at `config/blender_mcp_config.yaml`:

```yaml
blender_mcp:
  server_url: "http://localhost:8000"
  api_key: "${BLENDER_MCP_API_KEY}"
  connection_timeout: 5.0
  request_timeout: 10.0
  max_retries: 3
  retry_delay: 1.0
  health_check_interval: 30.0
  fallback_enabled: true
```

### Ableton MCP Server

Create a configuration file for the Ableton MCP server at `config/ableton_mcp_config.yaml`:

```yaml
ableton_mcp:
  server_url: "http://localhost:8001"
  api_key: "${ABLETON_MCP_API_KEY}"
  connection_timeout: 5.0
  request_timeout: 10.0
  max_retries: 3
  retry_delay: 1.0
  health_check_interval: 30.0
  fallback_enabled: true
```

### Google ADK

Create a configuration file for the Google ADK at `config/google_adk_config.yaml`:

```yaml
google_adk:
  api_key: "${GOOGLE_ADK_API_KEY}"
  project_id: "performance-suite"
  agent_model: "bandmate-agent-1"
  max_concurrent_agents: 5
  request_timeout: 10.0
  fallback_enabled: true
```

## Environment Variables

Create a `.env` file with the necessary environment variables:

```
# MCP Server API Keys
BLENDER_MCP_API_KEY=your_blender_mcp_api_key
ABLETON_MCP_API_KEY=your_ableton_mcp_api_key
GOOGLE_ADK_API_KEY=your_google_adk_api_key
```

Make sure to add `.env` to your `.gitignore` file to avoid committing sensitive information.

## Testing Setup

Create a directory for MCP integration tests:

```bash
mkdir -p tests/mcp_integration
touch tests/mcp_integration/__init__.py
touch tests/mcp_integration/test_blender_mcp.py
touch tests/mcp_integration/test_ableton_mcp.py
touch tests/mcp_integration/test_google_adk.py
```

## Next Steps

After setting up the directory structure and configuration files, proceed with the implementation of the MCP integration as outlined in the [MCP Integration Plan](./mcp_integration_plan.md).

The GitHub issues for the implementation tasks are available in the [MCP Integration Issues](./mcp_integration_issues.md) document.