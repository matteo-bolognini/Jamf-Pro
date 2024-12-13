#!/usr/bin/env python3

import requests

# Define the URL and credentials
jamf_pro_url="https://instance.jamfcloud.com"

clientID="11-22-33-44"
clientSecret="abcdefgh"

token_endpoint = f'{jamf_pro_url}/api/oauth/token'


# Prepare the data payload
payload = {
	"client_id": clientID,
	"grant_type": "client_credentials",
	"client_secret": clientSecret
}

# Make the POST request
response = requests.post(
	token_endpoint,
	headers={
		"accept": "application/json",
		"Content-Type": "application/x-www-form-urlencoded"
	},
	data=payload
)

# Check for successful response
if response.status_code == 200:
	# Parse the access token from the response JSON
	access_token = response.json().get("access_token")
	print(f"Access Token: {access_token}")
else:
	print(f"Failed to retrieve token: {response.status_code}, {response.text}")
#	