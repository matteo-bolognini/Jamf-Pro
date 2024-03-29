#!/bin/bash

#This script is designed to connect to Jamf Pro via API, pull a list of scripts uploaded there and check for the use of #!/bin/zsh in those.
#If running in terminal, please use /bin/bash /path/to/CVE-2024-27301_Checker.sh 
#API Client Permissions: Read Scripts
#Script uses jq, make sure that's installed

URL="https://my_instance.jamfcloud.com"

clientID="11-22-33-44"
clientSecret="aa-22-bb-44"

# generate an auth token
token_data=$(/usr/bin/curl --location \
--silent \
--request POST "$URL/api/oauth/token" \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode "client_id=$clientID" \
--data-urlencode 'grant_type=client_credentials' \
--data-urlencode "client_secret=$clientSecret")
access_token=$(echo "$token_data" | jq -r '.access_token')

#curl Jamf Pro to pull a list of all the IDs of Scripts
payload=$(/usr/bin/curl --silent --request GET --url $URL/JSSResource/scripts --header "Authorization: Bearer $access_token" --header 'Accept: application/json')

ID=($(echo "$payload" | jq -r '.scripts[] | .id'))

#Loop throuh each singe script to check shebang
for i in "${ID[@]}"; do
	payload=$(/usr/bin/curl --silent --request GET --url "$URL/api/v1/scripts/$i" --header "Authorization: Bearer $access_token" --header 'Accept: application/json')
	
	script_name=$(echo "$payload" | jq -r '.name')
	script_id=$(echo "$payload" | jq -r '.id')
	script_contents=$(echo "$payload" | jq -r '.scriptContents')
	
	echo "Checking script: $script_name..."
	
	if echo "$script_contents" | /usr/bin/grep -qE '^#!/bin/zsh'; then
		echo "WARNING!  This script uses: #!/bin/zsh"
		echo "Script Name: $script_name"
		echo "Script ID: $script_id"
		echo "Jamf Pro URL: $URL/view/settings/computer-management/scripts/$script_id?tab=general"
	else
		continue
	fi
done
