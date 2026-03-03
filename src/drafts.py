import base64
import time
from email.mime.text import MIMEText

from googleapiclient.errors import HttpError

from .formatting import text_to_html


def create_message(to, subject, body_text):
    html_body = text_to_html(body_text)
    message = MIMEText(html_body, 'html')
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'message': {'raw': raw}}


def create_draft_with_retry(service, user_id, message_body, max_retries=3):
    """Create draft with retry logic for rate limiting."""
    for attempt in range(max_retries):
        try:
            return service.users().drafts().create(userId=user_id, body=message_body).execute()
        except HttpError as error:
            if error.resp.status in [429, 500, 502, 503]:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Rate limit hit, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
            else:
                raise
