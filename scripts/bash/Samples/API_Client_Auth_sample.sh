#!/bin/bash


URL="https://instance.jamfcloud.com"

clientID="11-22-33-44"
clientSecret="abcdefgh"

# generate an auth token
token_data=$(/usr/bin/curl --location \
--silent \
--request POST "$URL/api/oauth/token" \
--header 'accept: application/json' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode "client_id=$clientID" \
--data-urlencode 'grant_type=client_credentials' \
--data-urlencode "client_secret=$clientSecret")
access_token=$(echo "$token_data" | jq -r '.access_token')

echo $access_token