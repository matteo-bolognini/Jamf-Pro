#!/bin/bash

########################################################################
#   This script is designed to create a LaunchDaemon that will run a   #
#   script to collect Jamf Protect privilege elevation logs            #
########################################################################

#Replace the below with choice values

# Set variables
SCRIPT_PATH="/Library/com.my_org.com/my_script.sh"
PLIST_PATH="/Library/LaunchDaemons/com.my_org.plist"
LABEL="com.my_org.myscript"

# Check if the script exists
if [ ! -f "$SCRIPT_PATH" ]; then
	echo "Error: Script not found at $SCRIPT_PATH"
	exit 1
fi

#######################
# DO NOT MODIFY BELOW #
#######################
# Create the plist file
cat << EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>$LABEL</string>
	<key>ProgramArguments</key>
	<array>
		<string>/bin/bash</string>
		<string>-c</string>
		<string>$SCRIPT_PATH</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
	<key>StartInterval</key>
	<integer>3600</integer>
	<key>StandardOutPath</key>
	<string>/tmp/$LABEL.out</string>
	<key>StandardErrorPath</key>
	<string>/tmp/$LABEL.err</string>
</dict>
</plist>
EOF

# Set correct ownership and permissions
chown root:wheel "$PLIST_PATH"
chmod 644 "$PLIST_PATH"

# Load the LaunchDaemon
launchctl bootstrap system "$PLIST_PATH"

echo "LaunchDaemon created and loaded successfully."