#!/bin/bash
# Mac Studio Connection Script
#
# This script provides easy commands to connect to the Mac Studio and transfer files.
#
# Usage:
#   ./scripts/mac_studio_connect.sh ssh                    # SSH into Mac Studio
#   ./scripts/mac_studio_connect.sh send <local> <remote>  # Send file/dir to Mac Studio
#   ./scripts/mac_studio_connect.sh get <remote> <local>   # Get file/dir from Mac Studio
#   ./scripts/mac_studio_connect.sh mkdir <remote_dir>     # Create directory on Mac Studio

# Mac Studio connection details
MAC_STUDIO_USER="danielconnolly"
MAC_STUDIO_HOST="192.168.1.20"
MAC_STUDIO_HOME="/Users/$MAC_STUDIO_USER"

# Function to expand tilde in path
expand_path() {
    echo "$1" | sed "s|^~/|$MAC_STUDIO_HOME/|"
}

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    echo "Error: No command specified"
    echo "Usage:"
    echo "  $0 ssh                    # SSH into Mac Studio"
    echo "  $0 send <local> <remote>  # Send file/dir to Mac Studio"
    echo "  $0 get <remote> <local>   # Get file/dir from Mac Studio"
    echo "  $0 mkdir <remote_dir>     # Create directory on Mac Studio"
    exit 1
fi

# Parse command
COMMAND=$1
shift

case $COMMAND in
    ssh)
        # SSH into Mac Studio
        echo "Connecting to Mac Studio..."
        ssh mac-studio
        ;;
        
    send)
        # Check arguments
        if [ $# -lt 2 ]; then
            echo "Error: Missing arguments for send command"
            echo "Usage: $0 send <local_path> <remote_path>"
            exit 1
        fi
        
        LOCAL_PATH="$1"
        REMOTE_PATH=$(expand_path "$2")
        
        # Check if local path exists
        if [ ! -e "$LOCAL_PATH" ]; then
            echo "Error: Local path '$LOCAL_PATH' does not exist"
            exit 1
        fi
        
        # Create remote directory
        REMOTE_DIR=$(dirname "$REMOTE_PATH")
        echo "Creating directory $REMOTE_DIR on Mac Studio..."
        ssh mac-studio "mkdir -p \"$REMOTE_DIR\""
        
        # Transfer file or directory
        if [ -d "$LOCAL_PATH" ]; then
            echo "Sending directory '$LOCAL_PATH' to Mac Studio at '$REMOTE_PATH'..."
            scp -r "$LOCAL_PATH" mac-studio:"$REMOTE_PATH"
        else
            echo "Sending file '$LOCAL_PATH' to Mac Studio at '$REMOTE_PATH'..."
            scp "$LOCAL_PATH" mac-studio:"$REMOTE_PATH"
        fi
        
        if [ $? -eq 0 ]; then
            echo "✅ Transfer successful!"
        else
            echo "❌ Transfer failed!"
        fi
        ;;
        
    get)
        # Check arguments
        if [ $# -lt 2 ]; then
            echo "Error: Missing arguments for get command"
            echo "Usage: $0 get <remote_path> <local_path>"
            exit 1
        fi
        
        REMOTE_PATH=$(expand_path "$1")
        LOCAL_PATH="$2"
        
        # Check if remote path exists
        ssh mac-studio "test -e \"$REMOTE_PATH\""
        if [ $? -ne 0 ]; then
            echo "Error: Remote path '$REMOTE_PATH' does not exist on Mac Studio"
            exit 1
        fi
        
        # Create local directory if needed
        LOCAL_DIR=$(dirname "$LOCAL_PATH")
        mkdir -p "$LOCAL_DIR"
        
        # Check if remote path is a directory
        ssh mac-studio "test -d \"$REMOTE_PATH\""
        IS_DIR=$?
        
        # Transfer file or directory
        if [ $IS_DIR -eq 0 ]; then
            echo "Getting directory '$REMOTE_PATH' from Mac Studio to '$LOCAL_PATH'..."
            scp -r mac-studio:"$REMOTE_PATH" "$LOCAL_PATH"
        else
            echo "Getting file '$REMOTE_PATH' from Mac Studio to '$LOCAL_PATH'..."
            scp mac-studio:"$REMOTE_PATH" "$LOCAL_PATH"
        fi
        
        if [ $? -eq 0 ]; then
            echo "✅ Transfer successful!"
        else
            echo "❌ Transfer failed!"
        fi
        ;;
        
    mkdir)
        # Check arguments
        if [ $# -lt 1 ]; then
            echo "Error: Missing directory path"
            echo "Usage: $0 mkdir <remote_dir>"
            exit 1
        fi
        
        REMOTE_DIR=$(expand_path "$1")
        
        # Create directory on Mac Studio
        echo "Creating directory '$REMOTE_DIR' on Mac Studio..."
        ssh mac-studio "mkdir -p \"$REMOTE_DIR\""
        
        if [ $? -eq 0 ]; then
            echo "✅ Directory created successfully!"
        else
            echo "❌ Failed to create directory!"
        fi
        ;;
        
    *)
        echo "Error: Unknown command '$COMMAND'"
        echo "Usage:"
        echo "  $0 ssh                    # SSH into Mac Studio"
        echo "  $0 send <local> <remote>  # Send file/dir to Mac Studio"
        echo "  $0 get <remote> <local>   # Get file/dir from Mac Studio"
        echo "  $0 mkdir <remote_dir>     # Create directory on Mac Studio"
        exit 1
        ;;
esac

exit 0