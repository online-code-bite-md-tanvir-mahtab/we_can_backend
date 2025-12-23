import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        "serviceAccountKey.json",
        scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials.token


def send_fcm_notification(token, title, body, data=None):
    access_token = get_access_token()

    with open("serviceAccountKey.json") as f:
        project_id = json.load(f)["project_id"]

    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": data or {},
            "android": {
                "priority": "HIGH",
                "notification": {
  "title": "🚨 Emergency Alert",
  "body": "Tap to view emergency",
  "click_action": "FLUTTER_NOTIFICATION_CLICK"
}

            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
