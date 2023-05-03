import ast
import json
import requests
import urllib.parse
import re
import boto3
import datetime


SLACK_API_TOKEN = ""
CHANNEL_NAME = "s"
SLACK_API_URL = ""

jamf_url = ""
control_group = ""
domain = ""

def lambda_handler(event, context):
    #Invoke Secrets Manager to retrieve Jamf Pro API credentials
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(
        SecretId='prod/JamfProAPI')
    secretDict = json.loads(response['SecretString'])
    api_user = secretDict['username']
    api_password = secretDict['password']
    
    #Parse the Slack message content
    output = f"""{event}"""
    data = ast.literal_eval(output)
    body_value = data['body']
    decoded_body = urllib.parse.unquote(body_value)
    query_params = urllib.parse.parse_qs(decoded_body)
    print(query_params)
    
    #Parse extract device Serial Number from Slack
    serial_from_slack = query_params.get('text', [None])[0]
    print(serial_from_slack)
    user_name = query_params['user_name']
    user_name = user_name[0]
    user_name = user_name.strip("[]'")
    print(user_name)
    
    #Parse extract user's details from Slack
    user_id = query_params['user_id']
    user_id = user_id[0]
    user_id = user_id.strip("[]'")
    print(user_id)
    
    #Check if the user is allowed to use LAPS by checking Azure AD group membership
    token_url = f"https://{jamf_url}.jamfcloud.com/api/v1/auth/token"
    headers = {"Accept": "application/json"}
    resp = requests.post(token_url, auth=(api_user, api_password), headers=headers)
    resp.raise_for_status()
    resp_data = resp.json()
    print(f"Access token granted, valid until {resp_data['expires']}.")
    data = resp.json()
    token = data["token"]
    
    url = f"https://{jamf_url}.jamfcloud.com/api/v1/cloud-idp/1002/test-user-membership"
    payload = {
        "username": f"{user_name}@{domain}",
        "groupname": f"{control_group}"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    resp_data = response.json()
    is_member = resp_data.get("isMember")
    
    if is_member:
        print("isMember is True")

        headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "content-type": "application/json"
        }
        url = f"https://{jamf_url}.jamfcloud.com/JSSResource/computers/serialnumber/{serial_from_slack}"
        resp = requests.get(url, headers=headers)
        resp_json = resp.json()
        resp_json = resp.text
        output = json.loads(resp_json)
        id = output["computer"]["general"]["id"]
        print(id)
        
        url = f"https://{jamf_url}.jamfcloud.com/api/v1/computers-inventory/{id}?section=GENERAL"
        resp = requests.get(url, headers=headers)
        resp_json = resp.json()
        resp_json = resp.text
        output = json.loads(resp_json)
        managementId = output["general"]["managementId"]
        device_name = output["general"]["name"]
        
        url = f"https://{jamf_url}.jamfcloud.com/api/v1/local-admin-password/settings"
        resp = requests.get(url, headers=headers)
        resp_json = resp.json()
        resp_json = resp.text
        output = json.loads(resp_json)
        passwordRotationTime = output["passwordRotationTime"]
        seconds = 3600
        passwordRotationTime = passwordRotationTime // 60  
        
        url = f"https://{jamf_url}.jamfcloud.com/api/v1/local-admin-password/{managementId}/accounts"
        resp = requests.get(url, headers=headers)
        resp_json = resp.json()
        resp_json = resp.text
        output = json.loads(resp_json)
        username = output["results"][0]["username"]
        
        url = f"https://{jamf_url}.jamfcloud.com/api/v1/computers-inventory/{id}?section=HARDWARE"
        resp = requests.get(url, headers=headers)
        resp_json = resp.json()
        resp_json = resp.text
        output = json.loads(resp_json)
        serialNumber = output["hardware"]["serialNumber"]
        print(serialNumber)
        
        url = f"https://{jamf_url}.jamfcloud.com/api/v1/local-admin-password/{managementId}/account/{username}/password"
        resp = requests.get(url, headers=headers)
        resp_json = resp.json()
        resp_json = resp.text
        output = json.loads(resp_json)
        password = output["password"]
        
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        time = time.replace(" ", "").replace("-", "").replace(":", "").replace(";", "")
        print(time)
        
        secretsmanager = boto3.client('secretsmanager')
        response = secretsmanager.create_secret(
            Name = f"{serialNumber}-{time}",
            SecretString = (
                '{"computer": "' + device_name + '", '
                '"username": ": "' + username + '", '
                '"password": "' + password + '"}'
                )
            )
        vault_name = f"{serialNumber}-{time}"
        print(f"Secret URL: https://console.aws.amazon.com/secretsmanager/home?region={boto3.session.Session().region_name}#/secret?name={vault_name}")
        secretsmanager_url = f"https://console.aws.amazon.com/secretsmanager/home?region={boto3.session.Session().region_name}#/secret?name={vault_name}"
        
        payload = {
            "channel": user_id,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*LAPS Details for Computer: {device_name}*",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Username:*\n{username}",
                        },
                        ],
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Device password securely stored in AWS Secrets Manager:*\n{secretsmanager_url}"},
                        ],
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Important Note: the password will be automatically rotated after {passwordRotationTime} minutes*"},
                        ],
                },
                ],
        }
        
        headers = {
            "Authorization": f"Bearer {SLACK_API_TOKEN}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        response = requests.post(SLACK_API_URL, headers=headers, json=payload)
        if response.status_code == 200 and response.json().get("ok"):
            print(f"Message successfully posted to {CHANNEL_NAME}")
        else:
            print("Error posting message to Slack:", response.json())
        return {
            'statusCode': 200,
            'body': (f"LAPS request in progress\nYou will get a message from the Slack LAPS app soon\n\nRequested by Administrator: {user_name}\nTarget device with Serial Number:{serial_from_slack}.")
        }
    else:
        print("isMember is not True")
        print(f"{user_name} attempted to request LAPS credentials for device record with Serial Number:{serial_from_slack} but is not authorized as is not member of the {control_group} LDAP Group.")
        
        return {
        'statusCode': 200,
        'body': (f"LAPS Request denied:\nAccount:{user_name} attempted to request LAPS credentials for device record with Serial Number:{serial_from_slack} but is not authorized due to lack of permissions.\nPlease contact your Jamf Pro administrator.")
    }