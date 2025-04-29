# Mac Studio Connection Guide

This guide provides instructions for connecting to the Mac Studio from the Mac Mini.

## Prerequisites

- SSH must be enabled on the Mac Studio (System Settings > Sharing > Remote Login)
- The Mac Studio must be connected to the same network as the Mac Mini
- The Mac Studio IP address is 192.168.1.20

## SSH Connection

SSH connection has been set up with key-based authentication. You can connect to the Mac Studio using:

```bash
ssh mac-studio
```

This uses the configuration in `~/.ssh/config` which includes:
- Host: 192.168.1.20
- User: danielconnolly
- Identity file: ~/.ssh/mac_studio_key

## File Transfer

### Sending Files to Mac Studio

To send a file to the Mac Studio:

```bash
scp <local_file> mac-studio:/Users/danielconnolly/path/to/destination/
```

For example:
```bash
scp document.txt mac-studio:/Users/danielconnolly/Documents/
```

To send a directory recursively:

```bash
scp -r <local_directory> mac-studio:/Users/danielconnolly/path/to/destination/
```

For example:
```bash
scp -r project_folder mac-studio:/Users/danielconnolly/Projects/
```

### Retrieving Files from Mac Studio

To retrieve a file from the Mac Studio:

```bash
scp mac-studio:/Users/danielconnolly/path/to/file <local_destination>
```

For example:
```bash
scp mac-studio:/Users/danielconnolly/Documents/document.txt ./
```

To retrieve a directory recursively:

```bash
scp -r mac-studio:/Users/danielconnolly/path/to/directory <local_destination>
```

For example:
```bash
scp -r mac-studio:/Users/danielconnolly/Projects/project_folder ./
```

## Creating Directories on Mac Studio

To create a directory on the Mac Studio:

```bash
ssh mac-studio "mkdir -p /Users/danielconnolly/path/to/new/directory"
```

For example:
```bash
ssh mac-studio "mkdir -p /Users/danielconnolly/Projects/new_project"
```

## Running Commands on Mac Studio

To run a command on the Mac Studio:

```bash
ssh mac-studio "<command>"
```

For example:
```bash
ssh mac-studio "ls -la /Users/danielconnolly/Projects"
```

## Troubleshooting

If you encounter issues with the connection:

1. Verify that the Mac Studio is powered on and connected to the network
2. Check that Remote Login is enabled on the Mac Studio
3. Ensure that the IP address of the Mac Studio is still 192.168.1.20
4. If the IP address has changed, update the ~/.ssh/config file