#!/bin/bash

# Set the directory and file path
SCRIPT_DIR="/Library/com.my_org.com"
SCRIPT_PATH="$SCRIPT_DIR/my_script.sh"

# Create the directory if it doesn't exist
if [ ! -d "$SCRIPT_DIR" ]; then
    echo "Creating directory $SCRIPT_DIR"
    sudo mkdir -p "$SCRIPT_DIR"
fi

# Create the script file
cat << 'EOF' | sudo tee "$SCRIPT_PATH" > /dev/null
#!/bin/bash

# Set the path where the log files will be saved
path="/Library/com.my_org.com/logs"

# Check if the directory exists
if [ ! -d "$path" ]; then
    echo "Directory $path does not exist. Creating it now..."
    mkdir -p "$path"
    if [ $? -eq 0 ]; then
        echo "Directory created successfully."
    else
        echo "Failed to create directory. Please check permissions and path."
        exit 1
    fi
else
    echo "Directory $path already exists."
fi

# Collect Jamf Connect Daemon Elevation Logs
echo "Collecting Jamf Connect Daemon Elevation Logs..."
log show --debug --info --style compact --predicate '(subsystem == "com.jamf.connect.daemon") && (category == "PrivilegeElevation")' >> "$path/Connect_Daemon_Elevation_Logs.txt"

# Collect Jamf Connect Menubar Elevation Logs
echo "Collecting Jamf Connect Menubar Elevation Logs..."
log show --debug --info --style compact --predicate '(subsystem == "com.jamf.connect") && (category == "PrivilegeElevation")' >> "$path/Connect_Menubar_Elevation_Logs.txt"

echo "Log collection complete. Files saved in $path"
EOF

# Set the correct permissions
chmod 755 "$SCRIPT_PATH"

# Make the script executable
chmod +x "$SCRIPT_PATH"

echo "Script has been created at $SCRIPT_PATH and made executable"
