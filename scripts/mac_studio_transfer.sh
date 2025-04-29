#!/bin/bash
# Mac Studio File Transfer Script
#
# This script makes it easy to transfer files and directories between the Mac Mini and Mac Studio.
#
# Usage:
#   ./scripts/mac_studio_transfer.sh send <local_path> <remote_path>
#   ./scripts/mac_studio_transfer.sh get <remote_path> <local_path>
#
# Examples:
#   ./scripts/mac_studio_transfer.sh send ./myfile.txt ~/
#   ./scripts/mac_studio_transfer.sh send ./mydir/ ~/projects/
#   ./scripts/mac_studio_transfer.sh get ~/myfile.txt ./
#   ./scripts/mac_studio_transfer.sh get ~/mydir/ ./

# Check if the correct number of arguments is provided
if [ $# -lt 3 ]; then
    echo "Error: Insufficient arguments"
    echo "Usage:"
    echo "  $0 send <local_path> <remote_path>"
    echo "  $0 get <remote_path> <local_path>"
    exit 1
fi

# Parse arguments
ACTION=$1
SOURCE=$2
DESTINATION=$3

# Function to expand tilde in path for Mac Studio
expand_remote_path() {
    local path=$1
    # Replace ~/ with /Users/danielconnolly/
    echo "$path" | sed "s|^~/|/Users/danielconnolly/|"
}

# Function to send files/directories to Mac Studio
send_to_mac_studio() {
    local_path=$1
    remote_path=$2
    
    # Check if the source exists
    if [ ! -e "$local_path" ]; then
        echo "Error: Source path '$local_path' does not exist"
        exit 1
    fi
    
    # Expand the remote path
    remote_path_expanded=$(expand_remote_path "$remote_path")
    
    # Create the remote directory if it doesn't exist
    remote_dir=$(dirname "$remote_path_expanded")
    ssh mac-studio "mkdir -p '$remote_dir'"
    
    # If the source is a directory, use recursive copy
    if [ -d "$local_path" ]; then
        echo "Sending directory '$local_path' to Mac Studio at '$remote_path'..."
        scp -r "$local_path" mac-studio:"$remote_path_expanded"
    else
        echo "Sending file '$local_path' to Mac Studio at '$remote_path'..."
        scp "$local_path" mac-studio:"$remote_path_expanded"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Transfer successful!"
    else
        echo "❌ Transfer failed!"
    fi
}

# Function to get files/directories from Mac Studio
get_from_mac_studio() {
    remote_path=$1
    local_path=$2
    
    # Check if the destination exists
    if [ ! -e "$(dirname "$local_path")" ]; then
        echo "Error: Destination directory '$(dirname "$local_path")' does not exist"
        exit 1
    fi
    
    # Expand the remote path
    remote_path_expanded=$(expand_remote_path "$remote_path")
    
    # Check if the source exists on the remote machine
    ssh mac-studio "test -e '$remote_path_expanded'"
    if [ $? -ne 0 ]; then
        echo "Error: Source path '$remote_path' does not exist on Mac Studio"
        exit 1
    fi
    
    # Check if the source is a directory on the remote machine
    ssh mac-studio "test -d '$remote_path_expanded'"
    is_dir=$?
    
    if [ $is_dir -eq 0 ]; then
        echo "Getting directory '$remote_path' from Mac Studio to '$local_path'..."
        scp -r mac-studio:"$remote_path_expanded" "$local_path"
    else
        echo "Getting file '$remote_path' from Mac Studio to '$local_path'..."
        scp mac-studio:"$remote_path_expanded" "$local_path"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Transfer successful!"
    else
        echo "❌ Transfer failed!"
    fi
}

# Execute the appropriate action
case $ACTION in
    send)
        send_to_mac_studio "$SOURCE" "$DESTINATION"
        ;;
    get)
        get_from_mac_studio "$SOURCE" "$DESTINATION"
        ;;
    *)
        echo "Error: Invalid action '$ACTION'"
        echo "Usage:"
        echo "  $0 send <local_path> <remote_path>"
        echo "  $0 get <remote_path> <local_path>"
        exit 1
        ;;
esac

exit 0