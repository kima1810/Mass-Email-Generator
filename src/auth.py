import os
import webbrowser

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .config import SCOPES
from .paths import get_token_path, resource_path


def authenticate_gmail():
    creds = None
    token_path = get_token_path()

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(resource_path('credentials.json'), SCOPES)

            def open_browser(url):
                webbrowser.open(url, new=1)
                return True

            creds = flow.run_local_server(
                port=0,
                open_browser=True,
                success_message='Authentication successful! You can close this window and return to the application.',
                timeout_seconds=120
            )

            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        except Exception as error:
            raise Exception(
                f"Authentication failed: {str(error)}\n\nPlease ensure:\n"
                "1. Your default browser is set\n"
                "2. You have internet connection\n"
                "3. Firewall is not blocking the connection"
            )

    return build('gmail', 'v1', credentials=creds)


def get_gmail_signature(service):
    try:
        profile = service.users().settings().sendAs().list(userId='me').execute()
        primary = next((item for item in profile['sendAs'] if item.get('isPrimary')), None)
        return primary.get('signature', '') if primary else ''
    except Exception as error:
        print(f"Could not retrieve signature: {str(error)}")
        return ''
