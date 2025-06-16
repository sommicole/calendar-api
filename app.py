from flask import Flask, request, jsonify
from msal import ConfidentialClientApplication
import requests
import os

app = Flask(__name__)

# Microsoft Graph credentials (secured via environment variables)
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
TENANT_ID = os.environ.get('TENANT_ID')
EMAIL = os.environ.get('EMAIL')

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

@app.route('/create_event', methods=['POST'])
def create_event():
    data = request.json
    subject = data.get('subject')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    location = data.get('location', '')

    # Acquire token
    app_auth = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY
    )
    token_response = app_auth.acquire_token_for_client(scopes=SCOPE)
    access_token = token_response.get('access_token')

    if not access_token:
        return jsonify({"error": "Failed to obtain access token", "details": token_response}), 401

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    event = {
        "subject": subject,
        "start": {
            "dateTime": start_time,
            "timeZone": "Eastern Standard Time"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Eastern Standard Time"
        },
        "location": {
            "displayName": location
        }
    }

    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL}/events"
    response = requests.post(url, headers=headers, json=event)

    return jsonify({
        "status": response.status_code,
        "response": response.json()
    })

@app.route('/', methods=['GET'])
def home():
    return "Calendar API is running", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))