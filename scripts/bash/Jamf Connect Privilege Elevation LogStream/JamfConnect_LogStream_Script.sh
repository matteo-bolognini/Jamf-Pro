#!/bin/bash

# Set the path where the log files will be saved
path="/tmp/logs"

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